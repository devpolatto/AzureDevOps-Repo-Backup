"""Configuração da aplicação com Pydantic."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do arquivo .env"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    organization: str = Field(default="MyOrganization", alias="ORGANIZATION")
    pat: str = Field(..., alias="AZURE_PAT")
    backup_path: str = Field(default="", alias="BACKUP_PATH")
    api_version: str = Field(default="7.1", alias="API_VERSION")

    def model_post_init(self, __context):
        """Define backup_path padrão se não for fornecido."""
        if not self.backup_path:
            self.backup_path = f"./Backup-AzureDevOps/{self.organization}"

    @property
    def base_url(self) -> str:
        """Retorna a URL base da API do Azure DevOps."""
        return f"https://dev.azure.com/{self.organization}"
