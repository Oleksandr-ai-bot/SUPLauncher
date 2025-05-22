from PySide6.QtCore import QObject, Signal, Slot
from typing import Dict, Optional, List

from core.logger import Logger
from models.profile import Profile
from services.profile_service import ProfileService


class ProfileController(QObject):
    """Контроллер для управления профилями"""

    # Сигналы
    profilesUpdated = Signal(dict)  # Словарь профилей
    profileSelected = Signal(str)  # ID выбранного профиля
    profileCreated = Signal(str)  # ID созданного профиля
    profileDeleted = Signal(str)  # ID удаленного профиля
    profileUpdated = Signal(str)  # ID обновленного профиля

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger().get_logger()
        self.profile_service = ProfileService()
        self.profiles = {}
        self.selected_profile_id = None

        # Загружаем профили при инициализации
        self.load_profiles()

    @Slot()
    def load_profiles(self):
        """Загрузка всех профилей"""
        self.logger.info("Загрузка профилей")

        # Загружаем профили через сервис
        self.profiles = self.profile_service.get_all_profiles()

        # Если профилей нет, создаем профиль по умолчанию
        if not self.profiles:
            self.logger.info("Профили не найдены, создание SUPMINE профиля по умолчанию")
            default_profile = self._create_default_profile()
            if default_profile:
                self.profiles[default_profile.id] = default_profile

        # Выбираем профиль по умолчанию, если ничего не выбрано
        self._select_default_profile()

        # Уведомляем о загрузке профилей
        self.profilesUpdated.emit(self.profiles)

    @Slot(str)
    def select_profile(self, profile_id: str):
        """Выбор профиля"""
        if profile_id in self.profiles:
            self.logger.info(f"Выбран профиль: {profile_id}")
            self.selected_profile_id = profile_id
            self.profileSelected.emit(profile_id)

    @Slot(str)
    def delete_profile(self, profile_id: str):
        """Удаление профиля"""
        if profile_id in self.profiles:
            self.logger.info(f"Удаление профиля: {profile_id}")

            # Удаляем профиль
            profile = self.profiles[profile_id]
            if profile.delete():
                # Удаляем из словаря
                del self.profiles[profile_id]

                # Если удаляем текущий выбранный профиль, выбираем новый
                if self.selected_profile_id == profile_id:
                    self._select_default_profile()

                # Уведомляем об удалении
                self.profileDeleted.emit(profile_id)
                self.profilesUpdated.emit(self.profiles)

    @Slot(str, str, str, str, int, bool)
    def update_profile(self, profile_id: str, name: str, version_id: str,
                       java_args: str, max_ram: int, fullscreen: bool):
        """Обновление параметров профиля"""
        if profile_id in self.profiles:
            self.logger.info(f"Обновление профиля: {profile_id}")

            # Получаем профиль
            profile = self.profiles[profile_id]

            # Обновляем параметры
            profile.name = name
            profile.version_id = version_id
            profile.java_args = java_args
            profile.max_ram = max_ram
            profile.fullscreen = fullscreen

            # Сохраняем изменения
            if profile.save():
                # Уведомляем об обновлении
                self.profileUpdated.emit(profile_id)
                self.profilesUpdated.emit(self.profiles)

    def _create_default_profile(self) -> Optional[Profile]:
        """Создание профиля SUPMINE по умолчанию"""
        try:
            # Создаем новый профиль
            profile = Profile()
            profile.name = "SUPMINE"
            profile.version_id = "1.20.1"
            profile.loader_type = "forge"
            profile.loader_version = "1.20.1-47.2.0"  # Пример версии Forge

            # Сохраняем профиль
            if profile.save():
                self.logger.info(f"Создан профиль по умолчанию: {profile.name} ({profile.id})")
                return profile

            self.logger.error("Не удалось сохранить профиль по умолчанию")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка создания профиля по умолчанию: {str(e)}")
            return None

    def _select_default_profile(self):
        """Выбор профиля по умолчанию"""
        if not self.profiles:
            self.selected_profile_id = None
            return

        # Если ничего не выбрано или выбранного профиля нет, выбираем первый
        if not self.selected_profile_id or self.selected_profile_id not in self.profiles:
            self.selected_profile_id = next(iter(self.profiles))
            self.logger.info(f"Выбран профиль по умолчанию: {self.selected_profile_id}")
            self.profileSelected.emit(self.selected_profile_id)
