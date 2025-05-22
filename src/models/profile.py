import json
import uuid
import os
import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

from core.paths import Paths
from core.logger import Logger
from core.config import DEFAULT_GAME_SETTINGS

logger = Logger().get_logger()
paths = Paths()


@dataclass
class Profile:
    """Модель профиля Minecraft"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Новый профиль"
    version_id: str = "latest-release"
    game_directory: Optional[str] = None
    java_path: Optional[str] = None
    min_ram: int = DEFAULT_GAME_SETTINGS["min_ram"]
    max_ram: int = DEFAULT_GAME_SETTINGS["max_ram"]
    resolution_width: int = DEFAULT_GAME_SETTINGS["resolution_width"]
    resolution_height: int = DEFAULT_GAME_SETTINGS["resolution_height"]
    fullscreen: bool = DEFAULT_GAME_SETTINGS["fullscreen"]
    java_args: str = DEFAULT_GAME_SETTINGS["java_args"]
    loader_type: Optional[str] = None  # None, "forge", "fabric", "quilt"
    loader_version: Optional[str] = None
    icon: str = "default"  # Имя файла значка
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    last_used: Optional[str] = None
    mods: List[str] = field(default_factory=list)
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def save(self) -> bool:
        """Сохраняет профиль в файл"""
        try:
            profile_path = paths.get_profile_path(self.id)
            os.makedirs(os.path.dirname(profile_path), exist_ok=True)

            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=2)

            logger.info(f"Профиль сохранен: {self.name} ({self.id})")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения профиля: {str(e)}")
            return False

    @classmethod
    def load(cls, profile_id: str) -> Optional['Profile']:
        """Загружает профиль из файла"""
        try:
            profile_path = paths.get_profile_path(profile_id)

            if not os.path.exists(profile_path):
                logger.warning(f"Профиль не найден: {profile_id}")
                return None

            with open(profile_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            profile = cls(**data)
            logger.info(f"Профиль загружен: {profile.name} ({profile.id})")
            return profile
        except Exception as e:
            logger.error(f"Ошибка загрузки профиля: {str(e)}")
            return None

    @classmethod
    def get_all_profiles(cls) -> Dict[str, 'Profile']:
        """Возвращает словарь всех профилей"""
        profiles = {}
        profiles_dir = paths.profiles_dir

        if not os.path.exists(profiles_dir):
            os.makedirs(profiles_dir)
            return profiles

        for filename in os.listdir(profiles_dir):
            if filename.endswith('.json'):
                profile_id = filename[:-5]  # Удаляем расширение .json
                profile = cls.load(profile_id)
                if profile:
                    profiles[profile_id] = profile

        return profiles

    def delete(self) -> bool:
        """Удаляет профиль"""
        try:
            profile_path = paths.get_profile_path(self.id)

            if os.path.exists(profile_path):
                os.remove(profile_path)
                logger.info(f"Профиль удален: {self.name} ({self.id})")
                return True

            logger.warning(f"Профиль для удаления не найден: {self.id}")
            return False
        except Exception as e:
            logger.error(f"Ошибка удаления профиля: {str(e)}")
            return False

    def update_last_used(self):
        """Обновляет время последнего использования"""
        self.last_used = datetime.datetime.now().isoformat()
        return self.save()

# Профили созданы специально для Юра
