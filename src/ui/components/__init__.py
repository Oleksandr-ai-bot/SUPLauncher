"""
Переиспользуемые UI компоненты
Содержит кастомные виджеты и элементы интерфейса
"""

from .animated_button import AnimatedButton
from .custom_title_bar import CustomTitleBar
from .notification import Notification, NotificationManager
from .profile_card import ProfileCard
from .progress_indicator import ProgressIndicator

__all__ = [
    "AnimatedButton",
    "CustomTitleBar",
    "Notification",
    "NotificationManager",
    "ProfileCard",
    "ProgressIndicator"
]

# Фабричные функции для создания компонентов
def create_play_button(text: str = "ИГРАТЬ") -> AnimatedButton:
    """Создание кнопки запуска игры"""
    from core.config import COLORS

    button = AnimatedButton(text)
    button.set_accent_color(COLORS["accent_primary"])
    button.setMinimumHeight(48)
    return button

def create_notification_manager(parent=None) -> NotificationManager:
    """Создание менеджера уведомлений"""
    return NotificationManager(parent)

def create_progress_indicator() -> ProgressIndicator:
    """Создание индикатора прогресса"""
    return ProgressIndicator()

# Экспортируем фабричные функции
__all__.extend([
    "create_play_button",
    "create_notification_manager",
    "create_progress_indicator"
])