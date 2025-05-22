# src/__init__.py
"""
SUPLAUNCHER - Современный Minecraft лаунчер
"""

__version__ = "1.0.0"
__author__ = "SUP Team"
__email__ = "support@villadesup.ru"

# ==========================================

# src/core/__init__.py
"""
Модуль ядра приложения
Содержит базовые классы и утилиты
"""

from .config import *
from .logger import Logger
from .paths import Paths

__all__ = [
    'Logger',
    'Paths',
    'COLORS',
    'UI',
    'FONTS',
    'ANIMATIONS',
    'APP_NAME',
    'APP_VERSION'
]

# ==========================================

# src/models/__init__.py
"""
Модуль моделей данных
"""

from .profile import Profile
from .settings import LauncherSettings

__all__ = [
    'Profile',
    'LauncherSettings'
]

# ==========================================

# src/ui/__init__.py
"""
Модуль пользовательского интерфейса
"""

# ==========================================

# src/ui/components/__init__.py
"""
Переиспользуемые UI компоненты
"""

from .animated_button import AnimatedButton
from .custom_title_bar import CustomTitleBar
from .notification import Notification, NotificationManager
from .profile_card import ProfileCard
from .progress_indicator import ProgressIndicator

__all__ = [
    'AnimatedButton',
    'CustomTitleBar',
    'Notification',
    'NotificationManager',
    'ProfileCard',
    'ProgressIndicator'
]

# ==========================================

# src/ui/views/__init__.py
"""
Представления (экраны) приложения
"""

from .home_view import HomeView
from .profiles_view import ProfilesView
from .creator_view import CreatorView
from .settings_view import SettingsView

__all__ = [
    'HomeView',
    'ProfilesView',
    'CreatorView',
    'SettingsView'
]

# ==========================================

# src/ui/windows/__init__.py
"""
Окна приложения
"""

from .main_window import MainWindow
from .settings_window import SettingsWindow
from .profile_editor import ProfileEditor

__all__ = [
    'MainWindow',
    'SettingsWindow',
    'ProfileEditor'
]

# ==========================================

# src/controllers/__init__.py
"""
Контроллеры для управления логикой приложения
"""

from .app_controller import AppController
from .profile_controller import ProfileController
from .minecraft_controller import MinecraftController

__all__ = [
    'AppController',
    'ProfileController',
    'MinecraftController'
]

# ==========================================

# src/services/__init__.py
"""
Сервисы для взаимодействия с внешними API и системами
"""

from .auth_service import AuthService, MinecraftAccount
from .minecraft_service import MinecraftService, MinecraftLaunchThread
from .profile_service import ProfileService
from .update_service import UpdateService
from .version_service import VersionService, MinecraftVersion, LoaderVersion

__all__ = [
    'AuthService',
    'MinecraftAccount',
    'MinecraftService',
    'MinecraftLaunchThread',
    'ProfileService',
    'UpdateService',
    'VersionService',
    'MinecraftVersion',
    'LoaderVersion'
]

# Все импорты организованы для удобства Юра
