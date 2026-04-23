"""Testes para modelos de dados."""

import pytest
from datetime import datetime

from backup_azure_devops.models import BackupReport, BackupStatus, Project, Repository


class TestBackupStatus:
    """Testes do enum BackupStatus."""

    def test_backup_status_cloned(self):
        """Testa status CLONED."""
        assert BackupStatus.CLONED.value == "CLONED"

    def test_backup_status_updated(self):
        """Testa status UPDATED."""
        assert BackupStatus.UPDATED.value == "UPDATED"

    def test_backup_status_error(self):
        """Testa status ERROR."""
        assert BackupStatus.ERROR.value == "ERROR"


class TestBackupReport:
    """Testes do modelo BackupReport."""

    def test_backup_report_creation(self, sample_backup_report):
        """Testa criação de relatório."""
        assert sample_backup_report.project == "TestProject"
        assert sample_backup_report.repository == "TestRepo"
        assert sample_backup_report.status == BackupStatus.CLONED
        assert sample_backup_report.duration_seconds == 12.5

    def test_backup_report_to_dict(self, sample_backup_report):
        """Testa conversão para dicionário."""
        data = sample_backup_report.to_dict()

        assert isinstance(data, dict)
        assert data["Project"] == "TestProject"
        assert data["Repository"] == "TestRepo"
        assert data["Status"] == "CLONED"
        assert data["Duration_s"] == 12.5
        assert "Timestamp" in data
        assert "LocalPath" in data

    def test_backup_report_timestamp_format(self, sample_backup_report):
        """Testa formatação do timestamp."""
        data = sample_backup_report.to_dict()
        timestamp_str = data["Timestamp"]

        # Verifica formato YYYY-MM-DD HH:MM:SS
        assert len(timestamp_str) == 19
        assert timestamp_str[4] == "-"
        assert timestamp_str[7] == "-"
        assert timestamp_str[10] == " "
        assert timestamp_str[13] == ":"
        assert timestamp_str[16] == ":"

    def test_backup_report_different_statuses(self):
        """Testa relatório com diferentes status."""
        now = datetime.now()

        for status in BackupStatus:
            report = BackupReport(
                timestamp=now,
                project="TestProject",
                repository="TestRepo",
                status=status,
                duration_seconds=10.0,
                local_path="/tmp/test",
            )

            data = report.to_dict()
            assert data["Status"] == status.value


class TestProject:
    """Testes do modelo Project."""

    def test_project_creation(self, sample_project):
        """Testa criação de project."""
        assert sample_project.id == "proj-1"
        assert sample_project.name == "TestProject"
        assert sample_project.url == "https://dev.azure.com/TestOrg/TestProject"

    def test_project_equality(self):
        """Testa igualdade de projects."""
        proj1 = Project(id="1", name="ProjectA", url="https://example.com/A")
        proj2 = Project(id="1", name="ProjectA", url="https://example.com/A")

        assert proj1 == proj2


class TestRepository:
    """Testes do modelo Repository."""

    def test_repository_creation(self, sample_repository):
        """Testa criação de repositório."""
        assert sample_repository.id == "repo-1"
        assert sample_repository.name == "TestRepo"
        assert sample_repository.default_branch == "refs/heads/main"

    def test_repository_clone_url(self, sample_repository):
        """Testa URL de clone."""
        assert "TestRepo" in sample_repository.clone_url
        assert sample_repository.clone_url.startswith("https://")
