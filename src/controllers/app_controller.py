from PySide6.QtCore import QObject, Signal, Slot, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from core.logger import Logger
from core.paths import Paths
from models.settings import LauncherSettings
from controllers.profile_controller import ProfileController
from controllers.minecraft_controller import MinecraftController
from services.update_service import UpdateService


class AppController(QObject):
    """Главный контроллер приложения, координирующий работу других контроллеров"""

    # Сигналы
    settingsLoaded = Signal(object)  # Объект настроек
    settingsUpdated = Signal(object)  # Объект настроек
    launchStateChanged = Signal(bool)  # Состояние запуска (True = запускается)
    launchProgressUpdated = Signal(int, int, str)  # Прогресс запуска
    updateAvailable = Signal(str)  # Новая версия

    def __init__(self, app: QApplication, parent=None):
        super().__init__(parent)
        self.logger = Logger().get_logger()
        self.paths = Paths()
        self.app = app

        # Инициализация настроек
        self.settings = LauncherSettings.load()

        # Инициализация контроллеров
        self.profile_controller = ProfileController(self)
        self.minecraft_controller = MinecraftController(self)

        # Инициализация сервисов
        self.update_service = UpdateService()

        # Подключение сигналов контроллеров
        self._connect_signals()

        # Проверка обновлений (с задержкой)
        if self.settings.check_updates:
            QTimer.singleShot(2000, self.check_updates)

    def _connect_signals(self):
        """Подключение сигналов между контроллерами"""
        # Сигналы контроллера Minecraft
        self.minecraft_controller.launchStarted.connect(self._on_launch_started)
        self.minecraft_controller.launchFinished.connect(self._on_launch_finished)
        self.minecraft_controller.progressUpdated.connect(self._on_launch_progress)

    @Slot()
    def initialize(self):
        """Инициализация приложения"""
        self.logger.info("Инициализация приложения")

        # Уведомляем о загруженных настройках
        self.settingsLoaded.emit(self.settings)

        # Инициализируем профили
        self.profile_controller.load_profiles()

    @Slot(str)
    def launch_minecraft(self, profile_id: str):
        """Запуск Minecraft с выбранным профилем"""
        self.logger.info(f"Запуск Minecraft с профилем: {profile_id}")

        # Запускаем через контроллер Minecraft
        self.minecraft_controller.launch_game(profile_id)

    @Slot()
    def cancel_launch(self):
        """Отмена запуска Minecraft"""
        self.logger.info("Отмена запуска Minecraft")

        # Отменяем через контроллер Minecraft
        self.minecraft_controller.cancel_launch()

    @Slot(object)
    def update_settings(self, settings: LauncherSettings):
        """Обновление настроек лаунчера"""
        self.logger.info("Обновление настроек лаунчера")

        # Сохраняем новые настройки
        self.settings = settings
        self.settings.save()

        # Уведомляем об обновлении настроек
        self.settingsUpdated.emit(self.settings)

    @Slot()
    def check_updates(self):
        """Проверка наличия обновлений лаунчера"""
        if not self.settings.check_updates:
            return

        self.logger.info("Проверка обновлений")

        try:
            latest_version = self.update_service.check_for_updates()
            if latest_version:
                self.logger.info(f"Доступно обновление: {latest_version}")
                self.updateAvailable.emit(latest_version)
        except Exception as e:
            self.logger.error(f"Ошибка проверки обновлений: {str(e)}")

    @Slot(str)
    def _on_launch_started(self, profile_id: str):
        """Обработка начала запуска игры"""
        self.logger.info(f"Начат запуск игры с профилем: {profile_id}")

        # Уведомляем о изменении состояния запуска
        self.launchStateChanged.emit(True)

    @Slot(str, bool)
    def _on_launch_finished(self, profile_id: str, success: bool):
        """Обработка завершения запуска игры"""
        self.logger.info(f"Завершен запуск игры с профилем: {profile_id}, успех: {success}")

        # Уведомляем о изменении состояния запуска
        self.launchStateChanged.emit(False)

        # Если запуск не удался, показываем сообщение
        if not success:
            QMessageBox.warning(
                None,
                "Ошибка запуска",
                f"Не удалось запустить Minecraft. Проверьте логи для получения дополнительной информации."
            )

    @Slot(int, int, str)
    def _on_launch_progress(self, current: int, maximum: int, status: str):
        """Обработка прогресса запуска игры"""
        # Пересылаем прогресс
        self.launchProgressUpdated.emit(current, maximum, status)
