"""Testes para configuração."""

import pytest
import tempfile
import os
from pathlib import Path
from pydantic import ValidationError

from backup_azure_devops.config import Settings


class TestSettings:
    """Testes do modelo Settings."""

    def test_settings_with_all_values(self, mock_settings):
        """Testa criação com todos os valores."""
        assert mock_settings.organization == "TestOrg"
        assert mock_settings.pat == "fake_pat_token_12345"
        assert mock_settings.backup_path == "/tmp/test_backup"
        assert mock_settings.api_version == "7.1"

    def test_settings_base_url_property(self, mock_settings):
        """Testa construção da URL base."""
        expected_url = "https://dev.azure.com/TestOrg"
        assert mock_settings.base_url == expected_url

    def test_settings_default_values(self, tmp_path, monkeypatch):
        """Testa valores padrão sem arquivo .env."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        monkeypatch.chdir(tmp_path)

        settings = Settings(AZURE_PAT="test_token")

        assert settings.organization == "MyOrganization"
        assert settings.api_version == "7.1"
        assert settings.backup_path == "./Backup-AzureDevOps/MyOrganization"

    def test_settings_pat_required(self, tmp_path, monkeypatch):
        """Testa que PAT é obrigatório."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        monkeypatch.chdir(tmp_path)

        with pytest.raises(ValidationError):
            Settings()

    def test_settings_organization_override(self, tmp_path):
        """Testa override da organização."""
        settings = Settings(
            AZURE_PAT="token",
            ORGANIZATION="CustomOrg",
        )

        assert settings.organization == "CustomOrg"
        assert settings.base_url == "https://dev.azure.com/CustomOrg"
