"""Testes para executor de comandos git."""

import pytest
import subprocess
from unittest.mock import Mock, patch

from backup_azure_devops.services.git_executor import (
    SubprocessGitExecutor,
    GitException,
)


class TestSubprocessGitExecutor:
    """Testes do executor git."""

    def test_executor_initialization(self, mock_logger):
        """Testa inicialização do executor."""
        executor = SubprocessGitExecutor(logger=mock_logger)
        assert executor.logger is mock_logger

    @patch("subprocess.run")
    def test_execute_success(self, mock_subprocess_run, mock_logger):
        """Testa execução bem-sucedida de comando."""
        mock_subprocess_run.return_value = None

        executor = SubprocessGitExecutor(logger=mock_logger)
        result = executor.execute(["git", "clone", "url", "path"])

        assert result is True
        mock_subprocess_run.assert_called_once()

    @patch("subprocess.run")
    def test_execute_with_cwd(self, mock_subprocess_run, mock_logger):
        """Testa execução com diretório de trabalho."""
        mock_subprocess_run.return_value = None

        executor = SubprocessGitExecutor(logger=mock_logger)
        executor.execute(["git", "pull"], cwd="/tmp/repo")

        call_kwargs = mock_subprocess_run.call_args[1]
        assert call_kwargs["cwd"] == "/tmp/repo"

    @patch("subprocess.run")
    def test_execute_subprocess_error(self, mock_subprocess_run, mock_logger):
        """Testa tratamento de erro do subprocess."""
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            1, "git", stderr="fatal error"
        )

        executor = SubprocessGitExecutor(logger=mock_logger)

        with pytest.raises(GitException):
            executor.execute(["git", "clone", "url", "path"])

        mock_logger.error.assert_called()

    @patch("subprocess.run")
    def test_execute_unexpected_error(self, mock_subprocess_run, mock_logger):
        """Testa tratamento de erro inesperado."""
        mock_subprocess_run.side_effect = Exception("Unexpected error")

        executor = SubprocessGitExecutor(logger=mock_logger)

        with pytest.raises(GitException):
            executor.execute(["git", "status"])

        mock_logger.error.assert_called()

    @patch("subprocess.run")
    def test_execute_logs_error_message(self, mock_subprocess_run, mock_logger):
        """Testa que erro é logado corretamente."""
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            1, "git", stderr="permission denied"
        )

        executor = SubprocessGitExecutor(logger=mock_logger)

        with pytest.raises(GitException):
            executor.execute(["git", "push", "origin", "main"])

        assert mock_logger.error.called
