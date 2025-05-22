"""
Сервисы для взаимодействия с внешними API и системами
Содержит бизнес-логику и интеграции
"""

from .auth_service import AuthService, MinecraftAccount
from .minecraft_service import MinecraftService, MinecraftLaunchThread
from .profile_service import ProfileService
from .update_service import UpdateService
from .version_service import VersionService, MinecraftVersion, LoaderVersion

__all__ = [
    "AuthService",
    "MinecraftAccount",
    "MinecraftService",
    "MinecraftLaunchThread",
    "ProfileService",
    "UpdateService",
    "VersionService",
    "MinecraftVersion",
    "LoaderVersion"
]

# Типы сервисов
SERVICE_TYPES = {
    "auth": AuthService,
    "minecraft": MinecraftService,
    "profile": ProfileService,
    "update": UpdateService,
    "version": VersionService
}


def create_service(service_type: str, *args, **kwargs):
    """Фабрика для создания сервисов"""
    if service_type not in SERVICE_TYPES:
        raise ValueError(f"Неизвестный тип сервиса: {service_type}")

    service_class = SERVICE_TYPES[service_type]
    return service_class(*args, **kwargs)


def get_available_services() -> list:
    """Получение списка доступных сервисов"""
    return list(SERVICE_TYPES.keys())


# Паттерн инициализации сервисов
def setup_services():
    """Настройка всех сервисов приложения"""
    services = {}

    # Создаем сервисы
    services["auth"] = AuthService()
    services["profile"] = ProfileService()
    services["version"] = VersionService()
    services["update"] = UpdateService()
    services["minecraft"] = MinecraftService()

    return services


# Проверка доступности внешних зависимостей
def check_service_dependencies() -> dict:
    """Проверка доступности зависимостей сервисов"""
    dependencies = {}

    # Проверяем minecraft-launcher-lib
    try:
        import minecraft_launcher_lib
        dependencies["minecraft_launcher_lib"] = True
    except ImportError:
        dependencies["minecraft_launcher_lib"] = False

    # Проверяем requests
    try:
        import requests
        dependencies["requests"] = True
    except ImportError:
        dependencies["requests"] = False

    # Проверяем другие зависимости
    try:
        import random_username
        dependencies["random_username"] = True
    except ImportError:
        dependencies["random_username"] = False

    try:
        import psutil
        dependencies["psutil"] = True
    except ImportError:
        dependencies["psutil"] = False

    return dependencies


# Экспортируем вспомогательные функции
__all__.extend([
    "SERVICE_TYPES",
    "create_service",
    "get_available_services",
    "setup_services",
    "check_service_dependencies"
])

# Проверяем критические зависимости при импорте
_dependencies = check_service_dependencies()
if not _dependencies.get("minecraft_launcher_lib", False):
    import warnings

    warnings.warn(
        "minecraft-launcher-lib не установлен. "
        "Запуск Minecraft будет недоступен. "
        "Установите: pip install minecraft-launcher-lib",
        ImportWarning
    )