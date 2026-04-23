"""Serviço de backup principal."""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import quote

from backup_azure_devops.models import BackupReport, BackupStatus
from backup_azure_devops.protocols import GitExecutor, Logger
from backup_azure_devops.services.azure_api import AzureDevOpsClient
from backup_azure_devops.services.git_executor import GitException


class BackupService:
    """Orquestrador do backup de repositórios."""

    def __init__(
        self,
        api_client: AzureDevOpsClient,
        git_executor: GitExecutor,
        logger: Logger,
        backup_base_path: str,
        pull_branches: bool = False,
    ):
        """Inicializa o serviço.

        Args:
            api_client: Cliente Azure DevOps API
            git_executor: Executor de comandos git
            logger: Logger para mensagens
            backup_base_path: Caminho base para salvar backups
            pull_branches: Se True, faz pull de cada branch após clone/fetch
        """
        self.api_client = api_client
        self.git_executor = git_executor
        self.logger = logger
        self.backup_base_path = Path(backup_base_path)
        self.pull_branches = pull_branches

    def backup_all(self) -> List[BackupReport]:
        """Faz backup de todos os repositórios da organização.

        Returns:
            Lista de relatórios de backup
        """
        # Cria diretório de backup se não existir
        self.backup_base_path.mkdir(parents=True, exist_ok=True)

        reports: List[BackupReport] = []

        # Lista todos os projects
        try:
            projects = self.api_client.get_projects()
        except Exception as e:
            self.logger.error(f"Erro ao listar projects: {e}")
            raise

        if not projects:
            self.logger.error("Nenhum project encontrado.")
            return reports

        # Para cada project, lista seus repositórios
        for project in projects:
            self.logger.info("──────────────────────────────────────")
            self.logger.info(f"Project: {project.name}")

            try:
                repos = self.api_client.get_repositories(project.name)
            except Exception:
                continue

            if not repos:
                self.logger.warn(f"Nenhum repositório em '{project.name}'.")
                continue

            self.logger.success(f"Encontrados {len(repos)} repositório(s).")

            # Faz backup de cada repositório
            for repo in repos:
                self.logger.info(f"  → Repo: {repo.name}")

                dest_path = self.backup_base_path / project.name / repo.name
                report = self._backup_repository(
                    project.name, repo.name, repo.clone_url, str(dest_path)
                )
                reports.append(report)

        return reports

    def _sync_all_branches(self, destination_path: str) -> None:
        """Sincroniza todas as branches remotas como branches locais.

        Args:
            destination_path: Caminho do repositório
        """
        try:
            # Muda para detached HEAD para não ter conflito com branch ativa
            self.git_executor.execute(
                ["git", "checkout", "--detach"],
                destination_path,
            )

            # Obtém todas as branches remotas
            result = subprocess.run(
                ["git", "branch", "-r"],
                cwd=destination_path,
                capture_output=True,
                text=True,
                check=True,
            )

            branches = [
                line.strip().split("/", 1)[1]
                for line in result.stdout.split("\n")
                if line.strip() and "HEAD" not in line
            ]

            # Cria branches locais para cada branch remota
            for branch in branches:
                self.git_executor.execute(
                    ["git", "branch", "-f", branch, f"origin/{branch}"],
                    destination_path,
                )

                # Se pull_branches está ativo, faz pull de cada branch
                if self.pull_branches:
                    self.git_executor.execute(
                        ["git", "checkout", branch],
                        destination_path,
                    )
                    self.git_executor.execute(
                        ["git", "pull", "origin", branch],
                        destination_path,
                    )

        except Exception as e:
            self.logger.warn(f"Não foi possível sincronizar todas as branches: {e}")

    def _backup_repository(
        self, project_name: str, repo_name: str, clone_url: str, destination_path: str
    ) -> BackupReport:
        """Faz backup de um repositório específico.

        Args:
            project_name: Nome do project
            repo_name: Nome do repositório
            clone_url: URL de clone
            destination_path: Caminho local para o backup

        Returns:
            Relatório do backup
        """
        start_time = datetime.now()
        status = BackupStatus.ERROR

        # Remove organização do clone_url se existir (remoteUrl vem com Org@host)
        clean_url = clone_url
        if "@" in clean_url:
            clean_url = "https://" + clean_url.split("@", 1)[1]
        # Injeta PAT na URL para autenticação
        auth_clone_url = clean_url.replace("https://", f"https://{quote(self.api_client.pat)}@")

        try:
            git_dir = os.path.join(destination_path, ".git")

            if os.path.exists(git_dir):
                # Repositório já existe → atualiza
                self.logger.info(f"Atualizando (pull) '{repo_name}'...")

                success = True
                try:
                    self.git_executor.execute(
                        ["git", "remote", "set-url", "origin", auth_clone_url], destination_path
                    )
                    self.git_executor.execute(
                        ["git", "fetch", "--all", "--prune", "--tags"], destination_path
                    )
                    self._sync_all_branches(destination_path)
                except GitException:
                    success = False

                if success:
                    status = BackupStatus.UPDATED
                else:
                    status = BackupStatus.ERROR
            else:
                # Primeiro backup → clone completo
                self.logger.info(f"Clonando '{repo_name}'...")

                # Cria diretório pai se não existir
                parent_dir = os.path.dirname(destination_path)
                os.makedirs(parent_dir, exist_ok=True)

                try:
                    self.git_executor.execute(
                        ["git", "clone", auth_clone_url, destination_path]
                    )
                    self._sync_all_branches(destination_path)
                    status = BackupStatus.CLONED
                except GitException:
                    status = BackupStatus.ERROR

            if status != BackupStatus.ERROR:
                self.logger.success(f"'{repo_name}' — {status.value} com sucesso.")
            else:
                self.logger.error(f"Falha no backup de '{repo_name}'.")

        except Exception as e:
            self.logger.error(f"Falha no backup de '{repo_name}': {e}")
            status = BackupStatus.ERROR

        # Retorna relatório
        elapsed = (datetime.now() - start_time).total_seconds()
        return BackupReport(
            timestamp=datetime.now(),
            project=project_name,
            repository=repo_name,
            status=status,
            duration_seconds=elapsed,
            local_path=destination_path,
        )
