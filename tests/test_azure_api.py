"""Testes para cliente Azure DevOps API."""

import pytest
import base64
from unittest.mock import Mock

from backup_azure_devops.services.azure_api import AzureDevOpsClient


class TestAzureDevOpsClient:
    """Testes do cliente Azure DevOps."""

    def test_client_initialization(self, azure_api_client):
        """Testa inicialização do cliente."""
        assert azure_api_client.base_url == "https://dev.azure.com/TestOrg"
        assert azure_api_client.pat == "fake_pat_token_12345"
        assert azure_api_client.api_version == "7.1"

    def test_auth_headers_creation(self, azure_api_client):
        """Testa criação dos headers de autenticação."""
        headers = azure_api_client._create_auth_headers()

        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")
        assert headers["Content-Type"] == "application/json"

    def test_auth_header_encoding(self, mock_settings, mock_logger, mock_http_client):
        """Testa encoding correto do PAT no header."""
        pat = "mytoken123"
        client = AzureDevOpsClient(
            base_url="https://dev.azure.com/TestOrg",
            pat=pat,
            http_client=mock_http_client,
            logger=mock_logger,
        )

        headers = client._create_auth_headers()
        auth_value = headers["Authorization"]

        encoded_part = auth_value.replace("Basic ", "")
        decoded = base64.b64decode(encoded_part).decode("ascii")
        assert decoded == f":{pat}"

    def test_get_projects_success(self, azure_api_client, mock_http_client, mock_logger):
        """Testa listagem bem-sucedida de projects."""
        mock_http_client.get.return_value = {
            "count": 2,
            "value": [
                {"id": "proj-1", "name": "ProjectA", "url": "https://example.com/A"},
                {"id": "proj-2", "name": "ProjectB", "url": "https://example.com/B"},
            ],
        }

        projects = azure_api_client.get_projects()

        assert len(projects) == 2
        assert projects[0].name == "ProjectA"
        assert projects[1].name == "ProjectB"
        mock_logger.success.assert_called()

    def test_get_projects_empty(self, azure_api_client, mock_http_client):
        """Testa listagem vazia de projects."""
        mock_http_client.get.return_value = {"count": 0, "value": []}

        projects = azure_api_client.get_projects()

        assert len(projects) == 0

    def test_get_projects_api_error(self, azure_api_client, mock_http_client, mock_logger):
        """Testa tratamento de erro na API."""
        mock_http_client.get.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            azure_api_client.get_projects()

        mock_logger.error.assert_called()

    def test_get_repositories_success(self, azure_api_client, mock_http_client, mock_logger):
        """Testa listagem bem-sucedida de repositórios."""
        mock_http_client.get.return_value = {
            "count": 2,
            "value": [
                {
                    "id": "repo-1",
                    "name": "RepoA",
                    "url": "https://example.com/A",
                    "remoteUrl": "https://dev.azure.com/TestOrg/ProjectA/_git/RepoA",
                    "defaultBranch": "refs/heads/main",
                },
                {
                    "id": "repo-2",
                    "name": "RepoB",
                    "url": "https://example.com/B",
                    "remoteUrl": "https://dev.azure.com/TestOrg/ProjectA/_git/RepoB",
                    "defaultBranch": "refs/heads/main",
                },
            ],
        }

        repos = azure_api_client.get_repositories("ProjectA")

        assert len(repos) == 2
        assert repos[0].name == "RepoA"
        assert repos[1].name == "RepoB"
        assert repos[0].clone_url == "https://dev.azure.com/TestOrg/ProjectA/_git/RepoA"

    def test_get_repositories_empty(self, azure_api_client, mock_http_client):
        """Testa listagem vazia de repositórios."""
        mock_http_client.get.return_value = {"count": 0, "value": []}

        repos = azure_api_client.get_repositories("ProjectA")

        assert len(repos) == 0

    def test_get_repositories_api_error(self, azure_api_client, mock_http_client, mock_logger):
        """Testa tratamento de erro ao listar repositórios."""
        mock_http_client.get.side_effect = Exception("API error")

        with pytest.raises(Exception):
            azure_api_client.get_repositories("ProjectA")

        mock_logger.error.assert_called()
