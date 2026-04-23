"""Testes para serviço de backup."""

import pytest
import tempfile
from unittest.mock import Mock
from datetime import datetime
from pathlib import Path

from backup_azure_devops.models import BackupStatus, Project, Repository
from backup_azure_devops.services.backup_service import BackupService
from backup_azure_devops.services.git_executor import GitException


class TestBackupService:
    """Testes do serviço de backup."""

    def test_backup_service_initialization(self, backup_service):
        """Testa inicialização do serviço."""
        assert backup_service.api_client is not None
        assert backup_service.git_executor is not None
        assert backup_service.logger is not None

    def test_backup_all_no_projects(self, backup_service, azure_api_client, mock_http_client):
        """Testa backup quando não há projects."""
        mock_http_client.get.return_value = {"count": 0, "value": []}

        reports = backup_service.backup_all()

        assert len(reports) == 0

    def test_backup_all_with_projects(
        self, backup_service, azure_api_client, mock_http_client, mock_logger
    ):
        """Testa backup com projects."""
        # Setup: API retorna 1 project com 1 repo
        mock_http_client.get.side_effect = [
            {
                "count": 1,
                "value": [
                    {
                        "id": "proj-1",
                        "name": "TestProject",
                        "url": "https://example.com",
                    }
                ],
            },
            {
                "count": 1,
                "value": [
                    {
                        "id": "repo-1",
                        "name": "TestRepo",
                        "url": "https://example.com/repo",
                        "remoteUrl": "https://dev.azure.com/TestOrg/TestProject/_git/TestRepo",
                        "defaultBranch": "refs/heads/main",
                    }
                ],
            },
        ]

        reports = backup_service.backup_all()

        assert len(reports) == 1
        assert reports[0].project == "TestProject"
        assert reports[0].repository == "TestRepo"

    def test_backup_clone_new_repository(self, backup_service, mock_git_executor, mock_logger):
        """Testa clone de repositório novo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_service.backup_base_path = Path(tmpdir)
            mock_git_executor.execute.return_value = True

            report = backup_service._backup_repository(
                "TestProject",
                "TestRepo",
                "https://example.com/repo.git",
                f"{tmpdir}/TestProject/TestRepo",
            )

            assert report.status == BackupStatus.CLONED
            assert "clone" in str(mock_git_executor.execute.call_args_list).lower()

    def test_backup_update_existing_repository(
        self, backup_service, mock_git_executor, mock_logger
    ):
        """Testa atualização de repositório existente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_service.backup_base_path = Path(tmpdir)

            # Cria diretório .git simulando repo existente
            repo_path = Path(tmpdir) / "TestProject" / "TestRepo"
            repo_path.mkdir(parents=True)
            (repo_path / ".git").mkdir()

            mock_git_executor.execute.return_value = True

            report = backup_service._backup_repository(
                "TestProject",
                "TestRepo",
                "https://example.com/repo.git",
                str(repo_path),
            )

            assert report.status == BackupStatus.UPDATED
            assert "fetch" in str(mock_git_executor.execute.call_args_list).lower()
            assert "checkout" in str(mock_git_executor.execute.call_args_list).lower()

    def test_backup_git_error_new_repo(
        self, backup_service, mock_git_executor, mock_logger
    ):
        """Testa tratamento de erro ao clonar."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_service.backup_base_path = Path(tmpdir)

            mock_git_executor.execute.side_effect = GitException("Clone failed")

            report = backup_service._backup_repository(
                "TestProject",
                "TestRepo",
                "https://example.com/repo.git",
                f"{tmpdir}/TestProject/TestRepo",
            )

            assert report.status == BackupStatus.ERROR
            mock_logger.error.assert_called()

    def test_backup_git_error_existing_repo(
        self, backup_service, mock_git_executor, mock_logger
    ):
        """Testa tratamento de erro ao fazer pull."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_service.backup_base_path = Path(tmpdir)

            repo_path = Path(tmpdir) / "TestProject" / "TestRepo"
            repo_path.mkdir(parents=True)
            (repo_path / ".git").mkdir()

            mock_git_executor.execute.side_effect = GitException("Pull failed")

            report = backup_service._backup_repository(
                "TestProject",
                "TestRepo",
                "https://example.com/repo.git",
                str(repo_path),
            )

            assert report.status == BackupStatus.ERROR

    def test_backup_report_duration(self, backup_service, mock_git_executor):
        """Testa que duração é registrada corretamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_service.backup_base_path = Path(tmpdir)
            mock_git_executor.execute.return_value = True

            report = backup_service._backup_repository(
                "TestProject",
                "TestRepo",
                "https://example.com/repo.git",
                f"{tmpdir}/TestProject/TestRepo",
            )

            assert report.duration_seconds >= 0
            assert isinstance(report.duration_seconds, float)

    def test_backup_report_fields(self, backup_service, mock_git_executor):
        """Testa que todos os campos do relatório são preenchidos."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_service.backup_base_path = Path(tmpdir)
            mock_git_executor.execute.return_value = True

            report = backup_service._backup_repository(
                "TestProject",
                "TestRepo",
                "https://example.com/repo.git",
                f"{tmpdir}/TestProject/TestRepo",
            )

            assert report.timestamp is not None
            assert report.project == "TestProject"
            assert report.repository == "TestRepo"
            assert report.status in [BackupStatus.CLONED, BackupStatus.UPDATED, BackupStatus.ERROR]
            assert report.duration_seconds >= 0
            assert report.local_path is not None
