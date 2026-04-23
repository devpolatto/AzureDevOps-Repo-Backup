"""Modelos de dados estruturados."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any


class BackupStatus(Enum):
    """Status de um backup de repositório."""

    CLONED = "CLONED"
    UPDATED = "UPDATED"
    ERROR = "ERROR"


@dataclass
class BackupReport:
    """Relatório de um backup de repositório."""

    timestamp: datetime
    project: str
    repository: str
    status: BackupStatus
    duration_seconds: float
    local_path: str

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização CSV."""
        return {
            "Timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Project": self.project,
            "Repository": self.repository,
            "Status": self.status.value,
            "Duration_s": round(self.duration_seconds, 1),
            "LocalPath": self.local_path,
        }


@dataclass
class Project:
    """Projeto no Azure DevOps."""

    id: str
    name: str
    url: str


@dataclass
class Repository:
    """Repositório Git no Azure DevOps."""

    id: str
    name: str
    url: str
    clone_url: str
    default_branch: str
