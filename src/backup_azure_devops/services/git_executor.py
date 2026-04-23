"""Executor de comandos Git."""

import subprocess
from typing import List, Optional

from backup_azure_devops.protocols import Logger


class GitException(Exception):
    """Exceção de erro em comando git."""

    pass


class SubprocessGitExecutor:
    """Executor de comandos git via subprocess."""

    def __init__(self, logger: Logger):
        """Inicializa o executor.

        Args:
            logger: Logger para mensagens
        """
        self.logger = logger

    def execute(self, cmd: List[str], cwd: Optional[str] = None) -> bool:
        """Executa um comando git.

        Args:
            cmd: Lista com comando git (ex: ["git", "clone", "url", "path"])
            cwd: Diretório de trabalho (opcional)

        Returns:
            True se sucesso

        Raises:
            GitException: Se comando falhar
        """
        try:
            subprocess.run(
                cmd,
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            error_msg = f"Erro ao executar git: {' '.join(cmd)} — {e.stderr}"
            self.logger.error(error_msg)
            raise GitException(error_msg) from e
        except Exception as e:
            error_msg = f"Erro inesperado ao executar git: {e}"
            self.logger.error(error_msg)
            raise GitException(error_msg) from e
