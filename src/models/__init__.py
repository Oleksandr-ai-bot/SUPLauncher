"""
Модуль моделей данных
Содержит классы для представления данных приложения
"""

from .profile import Profile
from .settings import LauncherSettings

# Дополнительные типы для типизации
from typing import Dict, List, Optional, Any

# Псевдонимы для удобства
ProfileDict = Dict[str, Profile]
SettingsDict = Dict[str, Any]

__all__ = [
    "Profile",
    "LauncherSettings",
    "ProfileDict",
    "SettingsDict"
]

# Валидаторы моделей
def validate_profile_data(data: dict) -> bool:
    """Валидация данных профиля"""
    required_fields = ["id", "name", "version_id"]
    return all(field in data for field in required_fields)

def validate_settings_data(data: dict) -> bool:
    """Валидация данных настроек"""
    return isinstance(data, dict)

# Экспортируем валидаторы
__all__.extend([
    "validate_profile_data",
    "validate_settings_data"
])