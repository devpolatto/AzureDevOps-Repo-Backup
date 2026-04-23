"""Writer para relatórios de backup em CSV."""

import csv
from pathlib import Path
from typing import List

from backup_azure_devops.models import BackupReport
from backup_azure_devops.protocols import Logger


class CSVReportWriter:
    """Escreve relatórios de backup em CSV."""

    def __init__(self, logger: Logger):
        """Inicializa o writer.

        Args:
            logger: Logger para mensagens
        """
        self.logger = logger

    def write(self, reports: List[BackupReport], filepath: str) -> bool:
        """Escreve relatórios em arquivo CSV.

        Args:
            reports: Lista de relatórios
            filepath: Caminho do arquivo CSV

        Returns:
            True se sucesso, False se erro
        """
        try:
            # Cria diretório se não existir
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            # Escreve CSV
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "Timestamp",
                    "Project",
                    "Repository",
                    "Status",
                    "Duration_s",
                    "LocalPath",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for report in reports:
                    writer.writerow(report.to_dict())

            self.logger.success("Relatório CSV salvo com sucesso.")
            return True
        except IOError as e:
            self.logger.error(f"Erro ao salvar relatório CSV: {e}")
            return False
