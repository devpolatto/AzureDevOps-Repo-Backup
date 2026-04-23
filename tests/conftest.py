"""Pytest configuration and shared fixtures."""

import pytest
from datetime import datetime
from unittest.mock import Mock

from backup_azure_devops.config import Settings
from backup_azure_devops.logger import write_log
from backup_azure_devops.models import BackupReport, BackupStatus, Project, Repository
from backup_azure_devops.protocols import GitExecutor, HttpClient, Logger
from backup_azure_devops.services.azure_api import AzureDevOpsClient
from backup_azure_devops.services.git_executor import SubprocessGitExecutor
from backup_azure_devops.services.backup_service import BackupService


@pytest.fixture
def mock_settings():
    """Configurações para testes."""
    return Settings(
        ORGANIZATION="TestOrg",
        AZURE_PAT="fake_pat_token_12345",
        BACKUP_PATH="/tmp/test_backup",
        API_VERSION="7.1",
    )


@pytest.fixture
def mock_git_executor():
    """Mock do executor git."""
    executor = Mock(spec=GitExecutor)
    executor.execute.return_value = True
    return executor


@pytest.fixture
def mock_http_client():
    """Mock do cliente HTTP."""
    client = Mock(spec=HttpClient)
    client.get.return_value = {
        "count": 0,
        "value": [],
    }
    return client


@pytest.fixture
def mock_logger():
    """Mock do logger."""
    logger = Mock(spec=Logger)
    logger.info = Mock()
    logger.error = Mock()
    logger.success = Mock()
    logger.warn = Mock()
    return logger


@pytest.fixture
def azure_api_client(mock_http_client, mock_logger, mock_settings):
    """Cliente Azure DevOps com HTTP mockado."""
    return AzureDevOpsClient(
        base_url=mock_settings.base_url,
        pat=mock_settings.pat,
        http_client=mock_http_client,
        logger=mock_logger,
        api_version=mock_settings.api_version,
    )


@pytest.fixture
def backup_service(mock_git_executor, azure_api_client, mock_logger, mock_settings):
    """Serviço de backup com dependências mockadas."""
    return BackupService(
        api_client=azure_api_client,
        git_executor=mock_git_executor,
        logger=mock_logger,
        backup_base_path=mock_settings.backup_path,
        pull_branches=False,
    )


@pytest.fixture
def sample_project():
    """Projeto de exemplo para testes."""
    return Project(
        id="proj-1",
        name="TestProject",
        url="https://dev.azure.com/TestOrg/TestProject",
    )


@pytest.fixture
def sample_repository():
    """Repositório de exemplo para testes."""
    return Repository(
        id="repo-1",
        name="TestRepo",
        url="https://dev.azure.com/TestOrg/TestProject/_git/TestRepo",
        clone_url="https://dev.azure.com/TestOrg/TestProject/_git/TestRepo",
        default_branch="refs/heads/main",
    )


@pytest.fixture
def sample_backup_report(sample_project, sample_repository):
    """Relatório de backup de exemplo para testes."""
    return BackupReport(
        timestamp=datetime.now(),
        project=sample_project.name,
        repository=sample_repository.name,
        status=BackupStatus.CLONED,
        duration_seconds=12.5,
        local_path="/tmp/test_backup/TestProject/TestRepo",
    )
