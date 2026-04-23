"""Entry point para CLI do backup Azure DevOps."""

import argparse
import sys
import shutil
from pathlib import Path

from backup_azure_devops.config import Settings
from backup_azure_devops.logger import write_log
from backup_azure_devops.services.azure_api import AzureDevOpsClient
from backup_azure_devops.services.git_executor import SubprocessGitExecutor
from backup_azure_devops.services.backup_service import BackupService
from backup_azure_devops.services.report_writer import CSVReportWriter


class SimpleLogger:
    """Logger simples que implementa Protocol Logger."""

    def info(self, message: str) -> None:
        write_log(message, "INFO")

    def success(self, message: str) -> None:
        write_log(message, "SUCCESS")

    def warn(self, message: str) -> None:
        write_log(message, "WARN")

    def error(self, message: str) -> None:
        write_log(message, "ERROR")


class RequestsHttpClient:
    """HTTP client usando requests."""

    def get(self, url: str, headers=None):
        import requests

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP error: {e}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Backup de repositórios Azure DevOps"
    )
    parser.add_argument(
        "--pull-branches",
        action="store_true",
        help="Faz pull de cada branch durante o backup (mais lento, mas mais completo)",
    )
    args = parser.parse_args()

    try:
        settings = Settings()
    except Exception as e:
        write_log(f"Erro ao carregar configurações: {e}", "ERROR")
        write_log("Certifique-se que o arquivo .env existe e está correto.", "ERROR")
        sys.exit(1)

    if not shutil.which("git"):
        write_log("Git não encontrado no PATH. Instale o Git antes de continuar.", "ERROR")
        sys.exit(1)

    logger = SimpleLogger()

    write_log("════════════════════════════════════════", "INFO")
    write_log(f"Backup Azure DevOps — Organização: {settings.organization}", "INFO")
    write_log(f"Destino: {settings.backup_path}", "INFO")
    if args.pull_branches:
        write_log("Modo: Pull completo de cada branch (LENTO)", "INFO")
    else:
        write_log("Modo: Apenas sincronização de branches (RÁPIDO)", "INFO")
    write_log("════════════════════════════════════════", "INFO")

    http_client = RequestsHttpClient()
    git_executor = SubprocessGitExecutor(logger=logger)

    api_client = AzureDevOpsClient(
        base_url=settings.base_url,
        pat=settings.pat,
        http_client=http_client,
        logger=logger,
        api_version=settings.api_version,
    )

    backup_service = BackupService(
        api_client=api_client,
        git_executor=git_executor,
        logger=logger,
        backup_base_path=settings.backup_path,
        pull_branches=args.pull_branches,
    )

    try:
        reports = backup_service.backup_all()
    except Exception as e:
        write_log(f"Erro durante backup: {e}", "ERROR")
        sys.exit(1)

    report_path = Path(settings.backup_path) / f"backup_log_{Path(settings.backup_path).stem}.csv"
    writer = CSVReportWriter(logger=logger)

    write_log("════════════════════════════════════════", "INFO")
    write_log("BACKUP CONCLUÍDO", "INFO")
    write_log(f"Total de repositórios: {len(reports)}", "INFO")

    if reports:
        success_count = sum(1 for r in reports if r.status.value in ["CLONED", "UPDATED"])
        failures = len(reports) - success_count
        log_level = "SUCCESS" if failures == 0 else "WARN"
        write_log(f"Sucesso: {success_count}  |  Falhas: {failures}", log_level)

        write_log(f"Salvando relatório em: {report_path}", "INFO")
        writer.write(reports, str(report_path))

        write_log("════════════════════════════════════════", "INFO")
        print("\n📋 RESUMO DO BACKUP:\n")
        for report in reports:
            print(
                f"  {report.project}/{report.repository:<30} | "
                f"{report.status.value:<10} | {report.duration_seconds:.1f}s"
            )
        print()


if __name__ == "__main__":
    main()
