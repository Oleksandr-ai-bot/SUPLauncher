"""
Окна приложения
Содержит основные и диалоговые окна
"""

from .main_window import MainWindow
from .settings_window import SettingsWindow
from .profile_editor import ProfileEditor

__all__ = [
    "MainWindow",
    "SettingsWindow",
    "ProfileEditor"
]

# Типы окон для удобства
WINDOW_TYPES = {
    "main": MainWindow,
    "settings": SettingsWindow,
    "profile_editor": ProfileEditor
}


def create_window(window_type: str, *args, **kwargs):
    """Фабрика для создания окон"""
    if window_type not in WINDOW_TYPES:
        raise ValueError(f"Неизвестный тип окна: {window_type}")

    window_class = WINDOW_TYPES[window_type]
    return window_class(*args, **kwargs)


def get_available_windows() -> list:
    """Получение списка доступных окон"""
    return list(WINDOW_TYPES.keys())


# Экспортируем вспомогательные функции
__all__.extend([
    "WINDOW_TYPES",
    "create_window",
    "get_available_windows"
])