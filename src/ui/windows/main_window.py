from PySide6.QtCore import Qt, Slot, QSize, QTimer
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QStackedWidget,
                               QToolBar, QLabel, QPushButton, QMessageBox, QSizePolicy)
from PySide6.QtGui import QIcon, QAction, QCloseEvent

from core.logger import Logger
from core.paths import Paths
from core.config import COLORS, UI, FONTS
from models.profile import Profile
from models.settings import LauncherSettings

from ui.components.custom_title_bar import CustomTitleBar
from ui.components.notification import NotificationManager
from ui.views.home_view import HomeView
from ui.views.profiles_view import ProfilesView
from ui.views.creator_view import CreatorView
from ui.views.settings_view import SettingsView


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint)
        self.logger = Logger().get_logger()
        self.paths = Paths()

        # Настройка размеров окна
        self.setMinimumSize(UI["window_min_width"], UI["window_min_height"])
        self.resize(UI["window_default_width"], UI["window_default_height"])

        # Состояние окна
        self._maximized = False

        # Менеджер уведомлений
        self.notification_manager = NotificationManager(self)

        # Контроллеры (будут установлены позже)
        self.app_controller = None
        self.profile_controller = None
        self.minecraft_controller = None

        # Инициализация UI
        self._init_ui()

        self.logger.info("Инициализация главного окна завершена")

    def _init_ui(self):
        """Инициализация интерфейса"""
        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Основной layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Кастомная панель заголовка
        self.title_bar = CustomTitleBar(self)
        self.title_bar.minimizeClicked.connect(self.showMinimized)
        self.title_bar.maximizeClicked.connect(self._toggle_maximize)
        self.title_bar.closeClicked.connect(self.close)

        # Контейнер для содержимого
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Панель навигации
        self.navigation_toolbar = QToolBar()
        self.navigation_toolbar.setMovable(False)
        self.navigation_toolbar.setObjectName("navigationToolbar")
        self.navigation_toolbar.setStyleSheet(f"""
            QToolBar#navigationToolbar {{
                background-color: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['border_light']};
                spacing: {UI['spacing_medium']}px;
                padding: {UI['padding_small']}px {UI['padding_medium']}px;
            }}

            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 8px;
                color: {COLORS['text_secondary']};
                min-width: 60px;
                text-align: center;
            }}

            QToolButton:hover {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
            }}

            QToolButton:checked {{
                background-color: rgba({int(COLORS['accent_primary'][1:3], 16)}, {int(COLORS['accent_primary'][3:5], 16)}, {int(COLORS['accent_primary'][5:7], 16)}, 0.2);
                color: {COLORS['accent_primary']};
            }}
        """)

        # Добавление кнопок навигации
        self._create_navigation_actions()

        # Стек представлений
        self.view_stack = QStackedWidget()

        # Инициализация представлений
        self.home_view = HomeView()
        self.profiles_view = ProfilesView()
        self.creator_view = CreatorView()
        self.settings_view = SettingsView()

        # Добавление представлений в стек
        self.view_stack.addWidget(self.home_view)
        self.view_stack.addWidget(self.profiles_view)
        self.view_stack.addWidget(self.creator_view)
        self.view_stack.addWidget(self.settings_view)

        # Добавление элементов в layout содержимого
        self.content_layout.addWidget(self.navigation_toolbar)
        self.content_layout.addWidget(self.view_stack, 1)

        # Добавление элементов в основной layout
        self.main_layout.addWidget(self.title_bar)
        self.main_layout.addWidget(self.content_container, 1)

        # Выбираем начальное представление
        self._switch_view(0)

    def _create_navigation_actions(self):
        """Создание действий навигации"""
        # Получаем пути к иконкам
        home_icon_path = self.paths.get_resource_path("icon", "home.svg")
        profile_icon_path = self.paths.get_resource_path("icon", "profile.svg")
        add_icon_path = self.paths.get_resource_path("icon", "add.svg")
        settings_icon_path = self.paths.get_resource_path("icon", "settings.svg")

        # Создаем действия с проверкой существования иконок
        try:
            self.home_action = QAction(QIcon(home_icon_path) if home_icon_path else QIcon(), "Главная", self)
        except:
            self.home_action = QAction("Главная", self)

        self.home_action.setCheckable(True)
        self.home_action.setChecked(True)
        self.home_action.triggered.connect(lambda: self._switch_view(0))

        try:
            self.profiles_action = QAction(QIcon(profile_icon_path) if profile_icon_path else QIcon(), "Профили", self)
        except:
            self.profiles_action = QAction("Профили", self)

        self.profiles_action.setCheckable(True)
        self.profiles_action.triggered.connect(lambda: self._switch_view(1))

        try:
            self.creator_action = QAction(QIcon(add_icon_path) if add_icon_path else QIcon(), "Создать сборку", self)
        except:
            self.creator_action = QAction("Создать сборку", self)

        self.creator_action.setCheckable(True)
        self.creator_action.triggered.connect(lambda: self._switch_view(2))

        try:
            self.settings_action = QAction(QIcon(settings_icon_path) if settings_icon_path else QIcon(), "Настройки",
                                           self)
        except:
            self.settings_action = QAction("Настройки", self)

        self.settings_action.setCheckable(True)
        self.settings_action.triggered.connect(lambda: self._switch_view(3))

        # Добавляем действия в тулбар
        self.navigation_toolbar.addAction(self.home_action)
        self.navigation_toolbar.addAction(self.profiles_action)
        self.navigation_toolbar.addAction(self.creator_action)

        # Добавляем разделитель (пустое пространство)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.navigation_toolbar.addWidget(spacer)

        self.navigation_toolbar.addAction(self.settings_action)

        # Группа действий для навигации
        self.view_actions = [self.home_action, self.profiles_action, self.creator_action, self.settings_action]

    def _switch_view(self, index: int):
        """Переключение между представлениями"""
        # Переключаем стек
        self.view_stack.setCurrentIndex(index)

        # Обновляем действия
        for i, action in enumerate(self.view_actions):
            action.setChecked(i == index)

        # Логируем переключение
        view_names = ["Главная", "Профили", "Создание", "Настройки"]
        if 0 <= index < len(view_names):
            self.logger.info(f"Переключение на вкладку: {view_names[index]}")

    def _toggle_maximize(self):
        """Переключение между нормальным и максимизированным состоянием"""
        if self._maximized:
            self.showNormal()
            self._maximized = False
        else:
            self.showMaximized()
            self._maximized = True

    def set_controllers(self, app_controller, profile_controller, minecraft_controller):
        """Установка контроллеров для взаимодействия с моделью"""
        self.app_controller = app_controller
        self.profile_controller = profile_controller
        self.minecraft_controller = minecraft_controller

        # Подключение сигналов контроллеров
        self._connect_signals()

    def _connect_signals(self):
        """Подключение сигналов между контроллерами и представлениями"""

        if not all([self.app_controller, self.profile_controller, self.minecraft_controller]):
            self.logger.error("Не все контроллеры установлены")
            return

        try:
            # Сигналы ProfileController
            self.profile_controller.profilesUpdated.connect(self._on_profiles_updated)
            self.profile_controller.profileSelected.connect(self._on_profile_selected)

            # Сигналы AppController
            self.app_controller.launchStateChanged.connect(self._on_launch_state_changed)
            self.app_controller.launchProgressUpdated.connect(self._on_launch_progress_updated)
            self.app_controller.updateAvailable.connect(self._on_update_available)

            # Сигналы представлений
            # HomeView
            self.home_view.playClicked.connect(self.app_controller.launch_minecraft)
            self.home_view.profileSelectionChanged.connect(self.profile_controller.select_profile)

            # ProfilesView
            self.profiles_view.profileSelected.connect(self.profile_controller.select_profile)
            self.profiles_view.profileDeleted.connect(self.profile_controller.delete_profile)
            self.profiles_view.playProfile.connect(self.app_controller.launch_minecraft)

            # SettingsView
            if hasattr(self.settings_view, 'settingsChanged'):
                self.settings_view.settingsChanged.connect(self.app_controller.update_settings)

            self.logger.info("Сигналы контроллеров подключены")
        except Exception as e:
            self.logger.error(f"Ошибка подключения сигналов: {str(e)}")

    @Slot(dict)
    def _on_profiles_updated(self, profiles: dict):
        """Обработка обновления списка профилей"""
        try:
            # Обновляем представление главной страницы
            self.home_view.update_profiles(profiles)

            # Обновляем представление профилей
            self.profiles_view.update_profiles(profiles)

            self.logger.info(f"Обновлены профили в UI: {len(profiles)} профилей")
        except Exception as e:
            self.logger.error(f"Ошибка обновления профилей в UI: {str(e)}")

    @Slot(str)
    def _on_profile_selected(self, profile_id: str):
        """Обработка выбора профиля"""
        try:
            # Обновляем представления
            self.home_view.selected_profile_id = profile_id
            self.profiles_view.set_selected_profile(profile_id)

            self.logger.info(f"Выбран профиль: {profile_id}")
        except Exception as e:
            self.logger.error(f"Ошибка выбора профиля: {str(e)}")

    @Slot(bool)
    def _on_launch_state_changed(self, is_launching: bool):
        """Обработка изменения состояния запуска"""
        try:
            # Обновляем представление главной страницы
            self.home_view.set_launching_state(is_launching)

            # Показываем уведомление
            if is_launching:
                self.notification_manager.show_notification(
                    "Запуск игры",
                    "Подготовка к запуску Minecraft...",
                    "info",
                    3000
                )

            self.logger.info(f"Состояние запуска изменено: {is_launching}")
        except Exception as e:
            self.logger.error(f"Ошибка изменения состояния запуска: {str(e)}")

    @Slot(int, int, str)
    def _on_launch_progress_updated(self, current: int, maximum: int, status: str):
        """Обработка обновления прогресса запуска"""
        try:
            # Обновляем представление главной страницы
            self.home_view.update_progress(current, maximum, status)
        except Exception as e:
            self.logger.error(f"Ошибка обновления прогресса: {str(e)}")

    @Slot(str)
    def _on_update_available(self, version: str):
        """Обработка обнаружения доступного обновления"""
        # Показываем уведомление об обновлении
        QTimer.singleShot(500, lambda: self._show_update_notification(version))

    def _show_update_notification(self, version: str):
        """Показ уведомления о доступном обновлении"""
        try:
            message_box = QMessageBox(self)
            message_box.setWindowTitle("Доступно обновление")
            message_box.setText(f"Доступна новая версия SUPLAUNCHER: {version}")
            message_box.setInformativeText("Хотите перейти на сайт для загрузки?")
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.Yes)
            message_box.setIcon(QMessageBox.Information)

            # Стилизация
            message_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {COLORS['bg_primary']};
                    color: {COLORS['text_primary']};
                }}
                QPushButton {{
                    background-color: {COLORS['bg_secondary']};
                    color: {COLORS['text_primary']};
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_tertiary']};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS['accent_primary']};
                }}
            """)

            result = message_box.exec_()

            if result == QMessageBox.Yes:
                # Открываем страницу с обновлением
                import webbrowser
                webbrowser.open("https://villadesup.ru/launcher")

        except Exception as e:
            self.logger.error(f"Ошибка показа уведомления об обновлении: {str(e)}")

    def show_notification(self, title: str, message: str, notification_type: str = "info", duration: int = 5000):
        """Показ уведомления"""
        try:
            self.notification_manager.show_notification(title, message, notification_type, duration)
        except Exception as e:
            self.logger.error(f"Ошибка показа уведомления: {str(e)}")

    def closeEvent(self, event: QCloseEvent):
        """Обработка события закрытия окна"""
        try:
            # Проверяем, не запускается ли игра
            if hasattr(self.home_view, 'is_launching') and self.home_view.is_launching:
                # Спрашиваем подтверждение
                message_box = QMessageBox(self)
                message_box.setWindowTitle("Подтверждение")
                message_box.setText("Выполняется запуск игры. Вы уверены, что хотите закрыть лаунчер?")
                message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                message_box.setDefaultButton(QMessageBox.No)
                message_box.setIcon(QMessageBox.Question)

                # Стилизация
                message_box.setStyleSheet(f"""
                    QMessageBox {{
                        background-color: {COLORS['bg_primary']};
                        color: {COLORS['text_primary']};
                    }}
                    QPushButton {{
                        background-color: {COLORS['bg_secondary']};
                        color: {COLORS['text_primary']};
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        min-width: 80px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['bg_tertiary']};
                    }}
                    QPushButton:pressed {{
                        background-color: {COLORS['accent_primary']};
                    }}
                """)

                result = message_box.exec_()

                if result == QMessageBox.No:
                    event.ignore()
                    return

                # Отменяем запуск
                if self.app_controller:
                    self.app_controller.cancel_launch()

            # Сохраняем настройки перед закрытием
            if hasattr(self, 'settings_view'):
                try:
                    # Попытка сохранить настройки
                    pass
                except Exception as e:
                    self.logger.error(f"Ошибка сохранения настроек при закрытии: {str(e)}")

            # Принимаем событие закрытия
            self.logger.info("Закрытие главного окна")
            event.accept()

        except Exception as e:
            self.logger.error(f"Ошибка при закрытии окна: {str(e)}")
            event.accept()  # Принимаем событие в любом случае

    def showEvent(self, event):
        """Обработка события показа окна"""
        super().showEvent(event)
        self.logger.info("Главное окно показано")

    def resizeEvent(self, event):
        """Обработка события изменения размера окна"""
        super().resizeEvent(event)
        # Можно добавить логику адаптивного интерфейса здесь

# Главное окно создано с любовью для Юра
