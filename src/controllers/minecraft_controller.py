from PySide6.QtCore import QObject, Signal, Slot, QThread, QMetaObject, Qt
from typing import Optional, Dict, List

from core.logger import Logger
from core.paths import Paths
from models.profile import Profile
from services.minecraft_service import MinecraftLaunchThread


class MinecraftController(QObject):
    """Контроллер для управления запуском Minecraft"""

    # Сигналы
    launchStarted = Signal(str)  # ID профиля
    launchFinished = Signal(str, bool)  # ID профиля, успешно ли
    progressUpdated = Signal(int, int, str)  # текущее, максимум, статус

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger().get_logger()
        self.paths = Paths()

        # Инициализация рабочего потока
        self.launch_thread = None
        self.current_profile_id = None

    @Slot(str)
    def launch_game(self, profile_id: str):
        """Запуск игры с указанным профилем"""
        self.logger.info(f"Запуск игры с профилем: {profile_id}")

        # Проверяем, не запускается ли уже игра
        if self.launch_thread and self.launch_thread.isRunning():
            self.logger.warning("Уже выполняется запуск игры")
            return

        # Загружаем профиль
        profile = Profile.load(profile_id)
        if not profile:
            self.logger.error(f"Не удалось загрузить профиль: {profile_id}")
            self.launchFinished.emit(profile_id, False)
            return

        # Запоминаем текущий профиль
        self.current_profile_id = profile_id

        # Создаем и настраиваем рабочий поток
        self.launch_thread = MinecraftLaunchThread(profile)

        # Подключаем сигналы
        self.launch_thread.progressUpdated.connect(self._on_progress_updated)
        self.launch_thread.launchFinished.connect(self._on_launch_finished)

        # Запускаем поток
        self.launch_thread.start()

        # Уведомляем о начале запуска
        self.launchStarted.emit(profile_id)

    @Slot()
    def cancel_launch(self):
        """Отмена запуска игры"""
        if self.launch_thread and self.launch_thread.isRunning():
            self.logger.info("Отмена запуска игры")

            # Останавливаем поток
            self.launch_thread.stop()
            self.launch_thread.wait()

            # Уведомляем об отмене запуска
            if self.current_profile_id:
                self.launchFinished.emit(self.current_profile_id, False)
                self.current_profile_id = None

    @Slot(int, int, str)
    def _on_progress_updated(self, current: int, maximum: int, status: str):
        """Обработка обновления прогресса"""
        self.progressUpdated.emit(current, maximum, status)

    @Slot(bool)
    def _on_launch_finished(self, success: bool):
        """Обработка завершения запуска"""
        if self.current_profile_id:
            self.logger.info(f"Запуск завершен: {success}")

            # Обновляем время последнего использования профиля
            if success:
                profile = Profile.load(self.current_profile_id)
                if profile:
                    import datetime
                    profile.last_used = datetime.datetime.now().isoformat()
                    profile.save()

            # Уведомляем о завершении запуска
            self.launchFinished.emit(self.current_profile_id, success)
            self.current_profile_id = None
