"""Testes para writer de relatórios."""

import pytest
import tempfile
import csv
from pathlib import Path

from backup_azure_devops.services.report_writer import CSVReportWriter
from backup_azure_devops.models import BackupReport, BackupStatus
from datetime import datetime


class TestCSVReportWriter:
    """Testes do writer de relatórios CSV."""

    def test_writer_initialization(self, mock_logger):
        """Testa inicialização do writer."""
        writer = CSVReportWriter(logger=mock_logger)
        assert writer.logger is mock_logger

    def test_write_single_report(self, mock_logger, sample_backup_report):
        """Testa escrita de um único relatório."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "report.csv"

            writer = CSVReportWriter(logger=mock_logger)
            result = writer.write([sample_backup_report], str(filepath))

            assert result is True
            assert filepath.exists()
            mock_logger.success.assert_called()

    def test_write_multiple_reports(self, mock_logger, sample_backup_report):
        """Testa escrita de múltiplos relatórios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "report.csv"

            report1 = sample_backup_report
            report2 = BackupReport(
                timestamp=datetime.now(),
                project="ProjectB",
                repository="RepoB",
                status=BackupStatus.UPDATED,
                duration_seconds=8.2,
                local_path="/tmp/test_backup/ProjectB/RepoB",
            )

            writer = CSVReportWriter(logger=mock_logger)
            result = writer.write([report1, report2], str(filepath))

            assert result is True

            with open(filepath) as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            assert len(rows) == 2
            assert rows[0]["Project"] == "TestProject"
            assert rows[1]["Project"] == "ProjectB"

    def test_write_csv_headers(self, mock_logger, sample_backup_report):
        """Testa que headers CSV estão corretos."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "report.csv"

            writer = CSVReportWriter(logger=mock_logger)
            writer.write([sample_backup_report], str(filepath))

            with open(filepath) as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames

            expected_headers = ["Timestamp", "Project", "Repository", "Status", "Duration_s", "LocalPath"]
            assert headers == expected_headers

    def test_write_csv_content_format(self, mock_logger, sample_backup_report):
        """Testa formato do conteúdo CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "report.csv"

            writer = CSVReportWriter(logger=mock_logger)
            writer.write([sample_backup_report], str(filepath))

            with open(filepath) as f:
                reader = csv.DictReader(f)
                row = next(reader)

            assert row["Project"] == "TestProject"
            assert row["Repository"] == "TestRepo"
            assert row["Status"] == "CLONED"
            assert float(row["Duration_s"]) == 12.5
            assert row["LocalPath"] == "/tmp/test_backup/TestProject/TestRepo"

    def test_write_creates_directory(self, mock_logger, sample_backup_report):
        """Testa que diretório é criado se não existir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "subdir" / "report.csv"

            writer = CSVReportWriter(logger=mock_logger)
            result = writer.write([sample_backup_report], str(filepath))

            assert result is True
            assert filepath.exists()

    def test_write_error_handling(self, mock_logger):
        """Testa tratamento de erro em escrita."""
        filepath = "/invalid/nonexistent/path/report.csv"

        writer = CSVReportWriter(logger=mock_logger)
        result = writer.write([], filepath)

        assert result is False
        mock_logger.error.assert_called()

    def test_write_empty_reports(self, mock_logger):
        """Testa escrita de lista vazia."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "report.csv"

            writer = CSVReportWriter(logger=mock_logger)
            result = writer.write([], str(filepath))

            assert result is True
            assert filepath.exists()

            with open(filepath) as f:
                lines = f.readlines()

            assert len(lines) == 1
