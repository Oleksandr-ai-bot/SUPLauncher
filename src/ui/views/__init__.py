"""
Представления (экраны) приложения
Содержит основные экраны пользовательского интерфейса
"""

from .home_view import HomeView
from .profiles_view import ProfilesView
from .creator_view import CreatorView
from .settings_view import SettingsView

__all__ = [
    "HomeView",
    "ProfilesView",
    "CreatorView",
    "SettingsView"
]

# Перечисление доступных представлений
VIEW_TYPES = {
    "home": HomeView,
    "profiles": ProfilesView,
    "creator": CreatorView,
    "settings": SettingsView
}


def create_view(view_type: str, parent=None):
    """Фабрика для создания представлений"""
    if view_type not in VIEW_TYPES:
        raise ValueError(f"Неизвестный тип представления: {view_type}")

    view_class = VIEW_TYPES[view_type]
    return view_class(parent)


def get_available_views() -> list:
    """Получение списка доступных представлений"""
    return list(VIEW_TYPES.keys())


# Экспортируем вспомогательные функции
__all__.extend([
    "VIEW_TYPES",
    "create_view",
    "get_available_views"
])