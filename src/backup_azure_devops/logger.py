"""Utilidade de logging com cores."""

from datetime import datetime
from typing import Optional

try:
    from colorama import Fore, Style, init

    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False


def get_color(level: str) -> str:
    """Retorna a cor ANSI baseada no nível de log."""
    if not HAS_COLORAMA:
        return ""

    colors = {
        "SUCCESS": Fore.GREEN,
        "WARN": Fore.YELLOW,
        "ERROR": Fore.RED,
        "INFO": Fore.CYAN,
    }
    return colors.get(level, Fore.WHITE)


def reset_color() -> str:
    """Retorna o reset de cor ANSI."""
    return Style.RESET_ALL if HAS_COLORAMA else ""


def write_log(message: str, level: str = "INFO") -> None:
    """Escreve mensagem de log com timestamp e cor."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = get_color(level)
    print(f"{color}[{timestamp}] [{level}] {message}{reset_color()}")
