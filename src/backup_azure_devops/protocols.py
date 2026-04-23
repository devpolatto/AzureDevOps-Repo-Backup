"""Type protocols para abstrações de dependências."""

from typing import Any, Dict, List, Optional, Protocol


class GitExecutor(Protocol):
    """Interface para executar comandos git."""

    def execute(self, cmd: List[str], cwd: Optional[str] = None) -> bool:
        """Executa um comando git.

        Args:
            cmd: Lista de argumentos do comando (ex: ["git", "clone", "url", "path"])
            cwd: Diretório de trabalho (opcional)

        Returns:
            True se sucesso, False se erro

        Raises:
            GitException: Se comando falhar
        """
        ...


class HttpClient(Protocol):
    """Interface para fazer chamadas HTTP."""

    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Faz uma requisição GET HTTP.

        Args:
            url: URL para requisitar
            headers: Headers opcionais

        Returns:
            JSON response como dicionário

        Raises:
            RequestException: Se requisição falhar
        """
        ...


class Logger(Protocol):
    """Interface para logging."""

    def info(self, message: str) -> None:
        """Loga uma mensagem informativa."""
        ...

    def success(self, message: str) -> None:
        """Loga uma mensagem de sucesso."""
        ...

    def warn(self, message: str) -> None:
        """Loga uma mensagem de aviso."""
        ...

    def error(self, message: str) -> None:
        """Loga uma mensagem de erro."""
        ...
