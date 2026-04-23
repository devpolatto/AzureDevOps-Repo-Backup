"""Cliente Azure DevOps API."""

import base64
from typing import Dict, Any, List, Optional

from backup_azure_devops.logger import write_log
from backup_azure_devops.models import Project, Repository
from backup_azure_devops.protocols import HttpClient, Logger


class AzureDevOpsClient:
    """Cliente para API do Azure DevOps."""

    def __init__(
        self,
        base_url: str,
        pat: str,
        http_client: HttpClient,
        logger: Logger,
        api_version: str = "7.1",
    ):
        """Inicializa o cliente.

        Args:
            base_url: URL base (ex: https://dev.azure.com/<organization>)
            pat: Personal Access Token
            http_client: Cliente HTTP para fazer requisições
            logger: Logger para mensagens
            api_version: Versão da API (padrão: 7.1)
        """
        self.base_url = base_url
        self.pat = pat
        self.http_client = http_client
        self.logger = logger
        self.api_version = api_version
        self._headers = self._create_auth_headers()

    def _create_auth_headers(self) -> Dict[str, str]:
        """Cria headers de autenticação Basic com PAT."""
        auth_str = f":{self.pat}"
        b64_token = base64.b64encode(auth_str.encode("ascii")).decode("ascii")
        return {
            "Authorization": f"Basic {b64_token}",
            "Content-Type": "application/json",
        }

    def get_projects(self) -> List[Project]:
        """Retorna lista de todos os projects da organização."""
        self.logger.info(f"Listando todos os Projects em '{self.base_url.split('/')[-1]}'...")

        url = f"{self.base_url}/_apis/projects?api-version={self.api_version}&$top=500"

        try:
            response = self.http_client.get(url, headers=self._headers)
            count = response.get("count", 0)
            self.logger.success(f"Encontrados {count} project(s).")

            projects = []
            for proj in response.get("value", []):
                projects.append(
                    Project(
                        id=proj.get("id", ""),
                        name=proj.get("name", ""),
                        url=proj.get("url", ""),
                    )
                )
            return projects
        except Exception as e:
            self.logger.error(f"Erro ao listar projects: {e}")
            raise

    def get_repositories(self, project_name: str) -> List[Repository]:
        """Retorna lista de repositórios de um project específico."""
        url = (
            f"{self.base_url}/{project_name}/_apis/git/repositories"
            f"?api-version={self.api_version}"
        )

        try:
            response = self.http_client.get(url, headers=self._headers)

            repositories = []
            for repo in response.get("value", []):
                repositories.append(
                    Repository(
                        id=repo.get("id", ""),
                        name=repo.get("name", ""),
                        url=repo.get("url", ""),
                        clone_url=repo.get("remoteUrl", ""),
                        default_branch=repo.get("defaultBranch", "refs/heads/main"),
                    )
                )
            return repositories
        except Exception as e:
            self.logger.error(f"Erro ao listar repositórios de {project_name}: {e}")
            raise
