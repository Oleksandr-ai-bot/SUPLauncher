"""
SUPLAUNCHER - Современный Minecraft лаунчер
Главный пакет приложения
"""

__version__ = "1.0.0"
__author__ = "SUP Team"
__email__ = "support@villadesup.ru"
__description__ = "Современный Minecraft лаунчер с минималистичным дизайном"
__url__ = "https://villadesup.ru"

# Проверяем совместимость Python
import sys
if sys.version_info < (3, 9):
    raise RuntimeError("SUPLAUNCHER требует Python 3.9 или выше")

# Проверяем наличие PySide6
try:
    import PySide6
except ImportError:
    raise ImportError(
        "PySide6 не установлен. Установите его командой: pip install PySide6"
    )

# Экспортируем основные компоненты
from core.config import APP_NAME, APP_VERSION
from core.logger import Logger
from core.paths import Paths

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "__url__",
    "APP_NAME",
    "APP_VERSION",
    "Logger",
    "Paths"
]

