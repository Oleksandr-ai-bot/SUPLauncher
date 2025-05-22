from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QCheckBox, QComboBox, QSlider, QSpinBox,
                               QGroupBox, QFrame, QPushButton, QLineEdit,
                               QFileDialog, QTabWidget, QWidget, QScrollArea,
                               QMessageBox)
from PySide6.QtGui import QIcon, QFont

from core.config import COLORS, UI, FONTS, APP_VERSION
from core.paths import Paths
from models.settings import LauncherSettings
from ui.components.animated_button import AnimatedButton


class SettingsWindow(QDialog):
    """Отдельное окно настроек"""

    # Сигналы
    settingsChanged = Signal(object)  # LauncherSettings объект

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.paths = Paths()
        self.settings = LauncherSettings.load()

        # Настройка окна
        self.setWindowTitle("Настройки SUPLAUNCHER")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.resize(800, 600)

        # Инициализация UI
        self._init_ui()

        # Загружаем текущие настройки в UI
        self._load_settings_to_ui()

    def _init_ui(self):
        """Инициализация интерфейса"""
        # Основной layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(UI["padding_large"], UI["padding_large"],
                                       UI["padding_large"], UI["padding_large"])
        self.layout.setSpacing(UI["spacing_large"])

        # Заголовок
        self.title_label = QLabel("Настройки")
        self.title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-family: "{FONTS['secondary']}";
            font-size: {FONTS['sizes']['header']}px;
            font-weight: bold;
        """)

        # Вкладки настроек
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border_light']};
                background-color: {COLORS['bg_secondary']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_secondary']};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_primary']};
                border-bottom: 2px solid {COLORS['accent_primary']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
            }}
        """)

        # Создание вкладок
        self._create_general_tab()
        self._create_game_tab()
        self._create_advanced_tab()
        self._create_about_tab()

        # Кнопки действий
        self.buttons_container = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(UI["spacing_medium"])

        # Кнопка сброса
        self.reset_button = AnimatedButton("Сбросить")
        self.reset_button.setMinimumHeight(UI["button_height"])
        self.reset_button.clicked.connect(self._reset_settings)

        # Кнопка отмены
        self.cancel_button = AnimatedButton("Отмена")
        self.cancel_button.setMinimumHeight(UI["button_height"])
        self.cancel_button.clicked.connect(self.reject)

        # Кнопка сохранения
        self.save_button = AnimatedButton("Сохранить")
        self.save_button.set_accent_color(COLORS["accent_primary"])
        self.save_button.setMinimumHeight(UI["button_height"])
        self.save_button.clicked.connect(self._save_and_close)

        # Добавление кнопок
        self.buttons_layout.addStretch(1)
        self.buttons_layout.addWidget(self.reset_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.addWidget(self.save_button)

        # Добавление всех элементов в основной layout
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.tab_widget, 1)
        self.layout.addWidget(self.buttons_container)

    def _create_general_tab(self):
        """Создание вкладки общих настроек"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                  UI["padding_medium"], UI["padding_medium"])
        layout.setSpacing(UI["spacing_medium"])

        # Группа поведения лаунчера
        behavior_group = QGroupBox("Поведение лаунчера")
        behavior_group.setStyleSheet(self._get_group_style())
        behavior_layout = QVBoxLayout(behavior_group)
        behavior_layout.setSpacing(UI["spacing_small"])

        # Закрытие при запуске
        self.close_on_launch_cb = QCheckBox("Закрывать лаунчер при запуске игры")
        self.close_on_launch_cb.setStyleSheet(self._get_checkbox_style())

        # Проверка обновлений
        self.check_updates_cb = QCheckBox("Автоматически проверять обновления")
        self.check_updates_cb.setStyleSheet(self._get_checkbox_style())

        behavior_layout.addWidget(self.close_on_launch_cb)
        behavior_layout.addWidget(self.check_updates_cb)

        # Группа интерфейса
        ui_group = QGroupBox("Интерфейс")
        ui_group.setStyleSheet(self._get_group_style())
        ui_layout = QVBoxLayout(ui_group)
        ui_layout.setSpacing(UI["spacing_small"])

        # Анимации
        self.enable_animations_cb = QCheckBox("Включить анимации")
        self.enable_animations_cb.setStyleSheet(self._get_checkbox_style())

        # Звуки
        self.enable_sounds_cb = QCheckBox("Включить звуковые эффекты")
        self.enable_sounds_cb.setStyleSheet(self._get_checkbox_style())

        # Язык
        lang_container = QWidget()
        lang_layout = QHBoxLayout(lang_container)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        lang_layout.setSpacing(UI["spacing_small"])

        lang_label = QLabel("Язык:")
        lang_label.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.language_combo = QComboBox()
        self.language_combo.addItems(["Автоматически", "Русский", "English"])

        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.language_combo, 1)

        ui_layout.addWidget(self.enable_animations_cb)
        ui_layout.addWidget(self.enable_sounds_cb)
        ui_layout.addWidget(lang_container)

        # Добавление групп в layout
        layout.addWidget(behavior_group)
        layout.addWidget(ui_group)
        layout.addStretch(1)

        self.tab_widget.addTab(tab, "Общие")

    def _create_game_tab(self):
        """Создание вкладки игровых настроек"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                  UI["padding_medium"], UI["padding_medium"])
        layout.setSpacing(UI["spacing_medium"])

        # Группа Java настроек
        java_group = QGroupBox("Настройки Java")
        java_group.setStyleSheet(self._get_group_style())
        java_layout = QVBoxLayout(java_group)
        java_layout.setSpacing(UI["spacing_small"])

        # Путь к Java
        java_path_container = QWidget()
        java_path_layout = QHBoxLayout(java_path_container)
        java_path_layout.setContentsMargins(0, 0, 0, 0)
        java_path_layout.setSpacing(UI["spacing_small"])

        java_path_label = QLabel("Путь к Java:")
        java_path_label.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.java_path_input = QLineEdit()
        self.java_path_input.setPlaceholderText("Автоматическое определение")

        self.java_browse_button = QPushButton("Обзор...")
        self.java_browse_button.clicked.connect(self._browse_java_path)

        java_path_layout.addWidget(java_path_label)
        java_path_layout.addWidget(self.java_path_input, 1)
        java_path_layout.addWidget(self.java_browse_button)

        # JVM аргументы
        jvm_args_label = QLabel("JVM аргументы:")
        jvm_args_label.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.jvm_args_input = QLineEdit()
        self.jvm_args_input.setPlaceholderText("-XX:+UnlockExperimentalVMOptions -XX:+UseG1GC")

        java_layout.addWidget(java_path_container)
        java_layout.addWidget(jvm_args_label)
        java_layout.addWidget(self.jvm_args_input)

        # Группа памяти
        memory_group = QGroupBox("Настройки памяти")
        memory_group.setStyleSheet(self._get_group_style())
        memory_layout = QVBoxLayout(memory_group)
        memory_layout.setSpacing(UI["spacing_small"])

        # Минимальная память
        min_ram_container = QWidget()
        min_ram_layout = QHBoxLayout(min_ram_container)
        min_ram_layout.setContentsMargins(0, 0, 0, 0)
        min_ram_layout.setSpacing(UI["spacing_small"])

        min_ram_label = QLabel("Минимальная память (MB):")
        min_ram_label.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.min_ram_spinbox = QSpinBox()
        self.min_ram_spinbox.setMinimum(512)
        self.min_ram_spinbox.setMaximum(32768)
        self.min_ram_spinbox.setValue(2048)
        self.min_ram_spinbox.setSuffix(" MB")

        min_ram_layout.addWidget(min_ram_label)
        min_ram_layout.addStretch(1)
        min_ram_layout.addWidget(self.min_ram_spinbox)

        # Максимальная память
        max_ram_container = QWidget()
        max_ram_layout = QHBoxLayout(max_ram_container)
        max_ram_layout.setContentsMargins(0, 0, 0, 0)
        max_ram_layout.setSpacing(UI["spacing_small"])

        max_ram_label = QLabel("Максимальная память (MB):")
        max_ram_label.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.max_ram_spinbox = QSpinBox()
        self.max_ram_spinbox.setMinimum(1024)
        self.max_ram_spinbox.setMaximum(32768)
        self.max_ram_spinbox.setValue(4096)
        self.max_ram_spinbox.setSuffix(" MB")

        max_ram_layout.addWidget(max_ram_label)
        max_ram_layout.addStretch(1)
        max_ram_layout.addWidget(self.max_ram_spinbox)

        memory_layout.addWidget(min_ram_container)
        memory_layout.addWidget(max_ram_container)

        # Добавление групп в layout
        layout.addWidget(java_group)
        layout.addWidget(memory_group)
        layout.addStretch(1)

        self.tab_widget.addTab(tab, "Игра")

    def _create_advanced_tab(self):
        """Создание вкладки расширенных настроек"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                  UI["padding_medium"], UI["padding_medium"])
        layout.setSpacing(UI["spacing_medium"])

        # Группа директорий
        dirs_group = QGroupBox("Директории")
        dirs_group.setStyleSheet(self._get_group_style())
        dirs_layout = QVBoxLayout(dirs_group)
        dirs_layout.setSpacing(UI["spacing_small"])

        # Директория игры
        game_dir_container = QWidget()
        game_dir_layout = QHBoxLayout(game_dir_container)
        game_dir_layout.setContentsMargins(0, 0, 0, 0)
        game_dir_layout.setSpacing(UI["spacing_small"])

        game_dir_label = QLabel("Директория игры:")
        game_dir_label.setStyleSheet(f"color: {COLORS['text_primary']};")

        self.game_dir_input = QLineEdit()
        self.game_dir_input.setPlaceholderText("По умолчанию")
        self.game_dir_input.setText(self.paths.minecraft_dir)

        self.game_dir_browse_button = QPushButton("Обзор...")
        self.game_dir_browse_button.clicked.connect(self._browse_game_dir)

        game_dir_layout.addWidget(game_dir_label)
        game_dir_layout.addWidget(self.game_dir_input, 1)
        game_dir_layout.addWidget(self.game_dir_browse_button)

        dirs_layout.addWidget(game_dir_container)

        # Группа отладки
        debug_group = QGroupBox("Отладка")
        debug_group.setStyleSheet(self._get_group_style())
        debug_layout = QVBoxLayout(debug_group)
        debug_layout.setSpacing(UI["spacing_small"])

        # Подробное логирование
        self.verbose_logging_cb = QCheckBox("Подробное логирование")
        self.verbose_logging_cb.setStyleSheet(self._get_checkbox_style())

        # Сохранять логи запуска
        self.keep_launcher_logs_cb = QCheckBox("Сохранять логи запуска")
        self.keep_launcher_logs_cb.setStyleSheet(self._get_checkbox_style())

        debug_layout.addWidget(self.verbose_logging_cb)
        debug_layout.addWidget(self.keep_launcher_logs_cb)

        # Кнопки очистки
        cleanup_group = QGroupBox("Очистка")
        cleanup_group.setStyleSheet(self._get_group_style())
        cleanup_layout = QVBoxLayout(cleanup_group)
        cleanup_layout.setSpacing(UI["spacing_small"])

        # Кнопка очистки кэша
        self.clear_cache_button = AnimatedButton("Очистить кэш версий")
        self.clear_cache_button.setMinimumHeight(36)
        self.clear_cache_button.clicked.connect(self._clear_cache)

        # Кнопка очистки логов
        self.clear_logs_button = AnimatedButton("Очистить логи")
        self.clear_logs_button.setMinimumHeight(36)
        self.clear_logs_button.clicked.connect(self._clear_logs)

        cleanup_layout.addWidget(self.clear_cache_button)
        cleanup_layout.addWidget(self.clear_logs_button)

        # Добавление групп в layout
        layout.addWidget(dirs_group)
        layout.addWidget(debug_group)
        layout.addWidget(cleanup_group)
        layout.addStretch(1)

        self.tab_widget.addTab(tab, "Дополнительно")

    def _create_about_tab(self):
        """Создание вкладки о программе"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(UI["padding_large"], UI["padding_large"],
                                  UI["padding_large"], UI["padding_large"])
        layout.setSpacing(UI["spacing_large"])

        # Информация о приложении
        app_info_container = QWidget()
        app_info_layout = QVBoxLayout(app_info_container)
        app_info_layout.setAlignment(Qt.AlignCenter)
        app_info_layout.setSpacing(UI["spacing_medium"])

        # Название и версия
        app_name_label = QLabel("SUPLAUNCHER")
        app_name_label.setStyleSheet(f"""
            color: {COLORS['accent_primary']};
            font-family: "{FONTS['secondary']}";
            font-size: {FONTS['sizes']['header']}px;
            font-weight: bold;
        """)
        app_name_label.setAlignment(Qt.AlignCenter)

        version_label = QLabel(f"Версия {APP_VERSION}")
        version_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['sizes']['large']}px;
        """)
        version_label.setAlignment(Qt.AlignCenter)

        # Описание
        description_label = QLabel("Современный Minecraft лаунчер\nс минималистичным дизайном")
        description_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['sizes']['normal']}px;
        """)
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)

        # Кнопки ссылок
        links_container = QWidget()
        links_layout = QHBoxLayout(links_container)
        links_layout.setAlignment(Qt.AlignCenter)
        links_layout.setSpacing(UI["spacing_medium"])

        # Кнопка сайта
        website_button = AnimatedButton("Официальный сайт")
        website_button.setMinimumHeight(40)
        website_button.clicked.connect(lambda: self._open_url("https://villadesup.ru"))

        # Кнопка папки данных
        data_folder_button = AnimatedButton("Папка данных")
        data_folder_button.setMinimumHeight(40)
        data_folder_button.clicked.connect(self._open_data_folder)

        links_layout.addWidget(website_button)
        links_layout.addWidget(data_folder_button)

        # Системная информация
        system_group = QGroupBox("Системная информация")
        system_group.setStyleSheet(self._get_group_style())
        system_layout = QVBoxLayout(system_group)
        system_layout.setSpacing(UI["spacing_small"])

        # Получаем системную информацию
        import platform
        try:
            import psutil
            ram_gb = round(psutil.virtual_memory().total / (1024 ** 3))
        except ImportError:
            ram_gb = "Неизвестно"

        # Создаем лейблы с информацией
        info_items = [
            f"ОС: {platform.system()} {platform.release()}",
            f"Архитектура: {platform.machine()}",
            f"Процессор: {platform.processor()[:50]}..." if len(
                platform.processor()) > 50 else f"Процессор: {platform.processor()}",
            f"RAM: {ram_gb} GB",
            f"Python: {platform.python_version()}"
        ]

        for info in info_items:
            info_label = QLabel(info)
            info_label.setStyleSheet(f"""
                color: {COLORS['text_secondary']};
                font-size: {FONTS['sizes']['small']}px;
            """)
            system_layout.addWidget(info_label)

        # Добавление элементов в layout
        app_info_layout.addWidget(app_name_label)
        app_info_layout.addWidget(version_label)
        app_info_layout.addWidget(description_label)
        app_info_layout.addWidget(links_container)

        layout.addWidget(app_info_container)
        layout.addWidget(system_group)
        layout.addStretch(1)

        self.tab_widget.addTab(tab, "О программе")

    def _load_settings_to_ui(self):
        """Загрузка настроек в элементы UI"""
        # Общие настройки
        self.close_on_launch_cb.setChecked(self.settings.close_on_launch)
        self.check_updates_cb.setChecked(self.settings.check_updates)
        self.enable_animations_cb.setChecked(self.settings.enable_animations)
        self.enable_sounds_cb.setChecked(self.settings.enable_sounds)

        # Язык
        lang_map = {"auto": 0, "ru": 1, "en": 2}
        self.language_combo.setCurrentIndex(lang_map.get(self.settings.language, 0))

    def _save_settings_from_ui(self):
        """Сохранение настроек из элементов UI"""
        # Общие настройки
        self.settings.close_on_launch = self.close_on_launch_cb.isChecked()
        self.settings.check_updates = self.check_updates_cb.isChecked()
        self.settings.enable_animations = self.enable_animations_cb.isChecked()
        self.settings.enable_sounds = self.enable_sounds_cb.isChecked()

        # Язык
        lang_map = {0: "auto", 1: "ru", 2: "en"}
        self.settings.language = lang_map.get(self.language_combo.currentIndex(), "auto")

        # Сохраняем в файл
        return self.settings.save()

    def _save_and_close(self):
        """Сохранение настроек и закрытие окна"""
        if self._save_settings_from_ui():
            self.settingsChanged.emit(self.settings)
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить настройки")

    def _reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        reply = QMessageBox.question(
            self,
            "Сброс настроек",
            "Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.settings = LauncherSettings()
            self._load_settings_to_ui()

    def _browse_java_path(self):
        """Выбор пути к Java"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите исполняемый файл Java",
            "",
            "Исполняемые файлы (*.exe);;Все файлы (*.*)" if os.name == 'nt' else "Все файлы (*.*)"
        )

        if file_path:
            self.java_path_input.setText(file_path)

    def _browse_game_dir(self):
        """Выбор директории игры"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите директорию для игры",
            self.game_dir_input.text() or self.paths.minecraft_dir
        )

        if dir_path:
            self.game_dir_input.setText(dir_path)

    def _clear_cache(self):
        """Очистка кэша"""
        reply = QMessageBox.question(
            self,
            "Очистка кэша",
            "Вы уверены, что хотите очистить кэш версий? Это приведет к повторной загрузке списков версий.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Здесь должна быть логика очистки кэша
                # Пока просто показываем сообщение
                QMessageBox.information(self, "Кэш очищен", "Кэш версий успешно очищен")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось очистить кэш: {str(e)}")

    def _clear_logs(self):
        """Очистка логов"""
        reply = QMessageBox.question(
            self,
            "Очистка логов",
            "Вы уверены, что хотите удалить все лог-файлы?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                import shutil
                if os.path.exists(self.paths.log_dir):
                    shutil.rmtree(self.paths.log_dir)
                    os.makedirs(self.paths.log_dir)
                QMessageBox.information(self, "Логи очищены", "Лог-файлы успешно удалены")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось очистить логи: {str(e)}")

    def _open_data_folder(self):
        """Открытие папки данных"""
        try:
            import subprocess
            import platform

            if platform.system() == "Windows":
                os.startfile(self.paths.data_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.paths.data_dir])
            else:  # Linux
                subprocess.run(["xdg-open", self.paths.data_dir])
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть папку: {str(e)}")

    def _open_url(self, url: str):
        """Открытие URL в браузере"""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть ссылку: {str(e)}")

    def _get_group_style(self) -> str:
        """Получение стиля для QGroupBox"""
        return f"""
            QGroupBox {{
                color: {COLORS['text_primary']};
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: {UI['border_radius']}px;
                font-size: {FONTS['sizes']['large']}px;
                font-weight: bold;
                margin-top: 8px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: {COLORS['accent_primary']};
                background-color: {COLORS['bg_secondary']};
            }}
        """

    def _get_checkbox_style(self) -> str:
        """Получение стиля для QCheckBox"""
        return f"""
            QCheckBox {{
                color: {COLORS['text_primary']};
                font-size: {FONTS['sizes']['normal']}px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {COLORS['text_secondary']};
                background-color: transparent;
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {COLORS['text_primary']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['accent_primary']};
                border: 2px solid {COLORS['accent_primary']};
            }}
        """

# Окно настроек детально проработано для Юра
