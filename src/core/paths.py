import os
import sys
import appdirs
from typing import Dict, Optional


class Paths:
    """Управление путями приложения"""

    def __init__(self, app_name: str = "SUPLAUNCHER", author: str = "SUP Team"):
        self.app_name = app_name
        self.author = author

        # Базовые пути
        self.is_frozen = getattr(sys, 'frozen', False)
        if self.is_frozen:
            self.app_dir = os.path.dirname(sys.executable)
        else:
            self.app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Пути для хранения пользовательских данных
        self.data_dir = appdirs.user_data_dir(app_name, author)
        self.config_dir = appdirs.user_config_dir(app_name, author)
        self.cache_dir = appdirs.user_cache_dir(app_name, author)
        self.log_dir = os.path.join(self.data_dir, 'logs')

        # Пути для игры
        self.minecraft_dir = os.path.join(self.data_dir, 'minecraft')
        self.profiles_dir = os.path.join(self.data_dir, 'profiles')
        self.versions_dir = os.path.join(self.minecraft_dir, 'versions')
        self.assets_dir = os.path.join(self.minecraft_dir, 'assets')
        self.libraries_dir = os.path.join(self.minecraft_dir, 'libraries')
        self.resource_packs_dir = os.path.join(self.minecraft_dir, 'resourcepacks')

        # Пути для ресурсов приложения
        if self.is_frozen:
            self.resources_dir = os.path.join(self.app_dir, 'resources')
        else:
            self.resources_dir = os.path.join(self.app_dir, 'assets')

        self.images_dir = os.path.join(self.resources_dir, 'images')
        self.icons_dir = os.path.join(self.resources_dir, 'icons')
        self.fonts_dir = os.path.join(self.resources_dir, 'fonts')
        self.sounds_dir = os.path.join(self.resources_dir, 'sounds')
        self.styles_dir = os.path.join(self.resources_dir, 'styles')

        # Создание необходимых директорий
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        """Создает все необходимые директории"""
        directories = [
            self.data_dir, self.config_dir, self.cache_dir, self.log_dir,
            self.minecraft_dir, self.profiles_dir, self.versions_dir,
            self.assets_dir, self.libraries_dir, self.resource_packs_dir
        ]

        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def get_resource_path(self, resource_type: str, filename: str) -> str:
        """Получает путь к ресурсу определенного типа"""
        resource_map = {
            'image': self.images_dir,
            'icon': self.icons_dir,
            'font': self.fonts_dir,
            'sound': self.sounds_dir,
            'style': self.styles_dir,
        }

        if resource_type not in resource_map:
            raise ValueError(f"Неизвестный тип ресурса: {resource_type}")

        return os.path.join(resource_map[resource_type], filename)

    def get_config_file(self) -> str:
        """Получает путь к файлу конфигурации"""
        return os.path.join(self.config_dir, 'config.json')

    def get_profile_path(self, profile_id: str) -> str:
        """Получает путь к файлу профиля"""
        return os.path.join(self.profiles_dir, f"{profile_id}.json")

    def get_log_file(self) -> str:
        """Получает путь к текущему лог-файлу"""
        import datetime
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"launcher-{date_str}.log")
