from typing import Dict, Optional, List
import os

from core.logger import Logger
from core.paths import Paths
from models.profile import Profile


class ProfileService:
    """Сервис для работы с профилями"""

    def __init__(self):
        self.logger = Logger().get_logger()
        self.paths = Paths()

    def get_all_profiles(self) -> Dict[str, Profile]:
        """Получение всех профилей"""
        return Profile.get_all_profiles()

    def get_profile(self, profile_id: str) -> Optional[Profile]:
        """Получение профиля по ID"""
        return Profile.load(profile_id)

    def create_profile(self, name: str, version_id: str, loader_type: Optional[str] = None,
                       loader_version: Optional[str] = None) -> Optional[Profile]:
        """Создание нового профиля"""
        try:
            profile = Profile()
            profile.name = name
            profile.version_id = version_id
            profile.loader_type = loader_type
            profile.loader_version = loader_version

            if profile.save():
                self.logger.info(f"Создан профиль: {name} ({profile.id})")
                return profile

            self.logger.error(f"Не удалось сохранить профиль: {name}")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка создания профиля: {str(e)}")
            return None

    def update_profile(self, profile: Profile) -> bool:
        """Обновление профиля"""
        try:
            if profile.save():
                self.logger.info(f"Обновлен профиль: {profile.name} ({profile.id})")
                return True

            self.logger.error(f"Не удалось сохранить профиль: {profile.name} ({profile.id})")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка обновления профиля: {str(e)}")
            return False

    def delete_profile(self, profile_id: str) -> bool:
        """Удаление профиля"""
        try:
            profile = Profile.load(profile_id)
            if profile and profile.delete():
                self.logger.info(f"Удален профиль: {profile.name} ({profile.id})")
                return True

            self.logger.error(f"Не удалось удалить профиль: {profile_id}")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка удаления профиля: {str(e)}")
            return False

    def import_profile(self, file_path: str) -> Optional[Profile]:
        """Импорт профиля из файла"""
        try:
            # Проверяем существование файла
            if not os.path.exists(file_path):
                self.logger.error(f"Файл не найден: {file_path}")
                return None

            # Загружаем профиль из файла
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Создаем новый профиль
            profile = Profile(**data)

            # Генерируем новый ID, чтобы избежать конфликтов
            import uuid
            profile.id = str(uuid.uuid4())

            # Сохраняем профиль
            if profile.save():
                self.logger.info(f"Импортирован профиль: {profile.name} ({profile.id})")
                return profile

            self.logger.error(f"Не удалось сохранить импортированный профиль")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка импорта профиля: {str(e)}")
            return None

    def export_profile(self, profile_id: str, file_path: str) -> bool:
        """Экспорт профиля в файл"""
        try:
            profile = Profile.load(profile_id)
            if not profile:
                self.logger.error(f"Профиль не найден: {profile_id}")
                return False

            # Сохраняем профиль в файл
            import json
            from dataclasses import asdict

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(profile), f, ensure_ascii=False, indent=2)

            self.logger.info(f"Экспортирован профиль: {profile.name} ({profile.id}) в {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка экспорта профиля: {str(e)}")
            return False
