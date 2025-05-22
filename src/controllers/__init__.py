"""
Контроллеры для управления логикой приложения
Реализуют паттерн MVC для разделения логики и представления
"""

from .app_controller import AppController
from .profile_controller import ProfileController
from .minecraft_controller import MinecraftController

__all__ = [
    "AppController",
    "ProfileController",
    "MinecraftController"
]

# Типы контроллеров
CONTROLLER_TYPES = {
    "app": AppController,
    "profile": ProfileController,
    "minecraft": MinecraftController
}

def create_controller(controller_type: str, *args, **kwargs):
    """Фабрика для создания контроллеров"""
    if controller_type not in CONTROLLER_TYPES:
        raise ValueError(f"Неизвестный тип контроллера: {controller_type}")

    controller_class = CONTROLLER_TYPES[controller_type]
    return controller_class(*args, **kwargs)

def get_available_controllers() -> list:
    """Получение списка доступных контроллеров"""
    return list(CONTROLLER_TYPES.keys())

# Паттерн инициализации контроллеров
def setup_controllers(app):
    """Настройка всех контроллеров приложения"""
    controllers = {}

    # Создаем контроллеры в правильном порядке
    controllers["profile"] = ProfileController()
    controllers["minecraft"] = MinecraftController()
    controllers["app"] = AppController(app)

    return controllers

# Экспортируем вспомогательные функции
__all__.extend([
    "CONTROLLER_TYPES",
    "create_controller",
    "get_available_controllers",
    "setup_controllers"
])