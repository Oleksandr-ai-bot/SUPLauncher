import logging
import sys
import os
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

from core.paths import Paths


class Logger:
    """Настраиваемая система логирования"""

    def __init__(self, name: str = "SUPLAUNCHER", level: int = logging.INFO):
        self.paths = Paths()
        self.console = Console(theme=Theme({
            "info": "cyan",
            "warning": "yellow",
            "error": "red",
            "critical": "bold red",
        }))

        # Создаем логгер
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Очищаем существующие обработчики
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Консольный обработчик с rich
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True
        )
        console_handler.setLevel(level)

        # Файловый обработчик
        log_file = self.paths.get_log_file()
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)

        # Добавляем обработчики
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """Возвращает настроенный логгер"""
        return self.logger
