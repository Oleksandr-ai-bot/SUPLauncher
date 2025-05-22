from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QCheckBox, QComboBox, QSlider, QSpinBox,
                               QGroupBox, QFrame, QSpacerItem, QSizePolicy,
                               QScrollArea, QPushButton, QLineEdit, QFileDialog)
from PySide6.QtGui import QIcon, QFont, QDesktopServices
from PySide6.QtCore import QUrl

from core.config import COLORS, UI, FONTS, APP_VERSION
from core.paths import Paths
from models.settings import LauncherSettings
from ui.components.animated_button import AnimatedButton
import webbrowser


class SettingsView(QWidget):
    """Представление настроек лаунчера"""

    # Сигналы
    settingsChanged = Signal(object)  # LauncherSettings объект

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paths = Paths()
        self.settings = LauncherSettings.load()

        # Инициализация UI
        self._init_ui()

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

        # Scroll area для настроек
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['bg_primary']};
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['text_secondary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        # Контейнер для настроек
        self.settings_widget = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_widget)
        self.settings_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_layout.setSpacing(UI["spacing_large"])

        # Группа настроек лаунчера
        self._create_launcher_settings_group()

        # Группа настроек игры
        self._create_game_settings_group()

        # Группа системной информации
        self._create_system_info_group()

        # Группа о программе
        self._create_about_group()

        # Добавляем растяжку в конце
        self.settings_layout.addStretch(1)

        # Устанавливаем виджет в scroll area
        self.scroll_area.setWidget(self.settings_widget)

        # Кнопки действий
        self.actions_container = QWidget()
        self.actions_layout = QHBoxLayout(self.actions_container)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setSpacing(UI["spacing_medium"])

        # Кнопка сброса настроек
        self.reset_button = AnimatedButton("Сбросить настройки")
        self.reset_button.setMinimumHeight(UI["button_height"])
        self.reset_button.clicked.connect(self._reset_settings)

        # Кнопка сохранения
        self.save_button = AnimatedButton("Сохранить")
        self.save_button.set_accent_color(COLORS["accent_primary"])
        self.save_button.setMinimumHeight(UI["button_height"])
        self.save_button.clicked.connect(self._save_settings)

        # Добавление кнопок
        self.actions_layout.addStretch(1)
        self.actions_layout.addWidget(self.reset_button)
        self.actions_layout.addWidget(self.save_button)

        # Добавление всех элементов в основной layout
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.scroll_area, 1)
        self.layout.addWidget(self.actions_container)

    def _create_launcher_settings_group(self):
        """Создание группы настроек лаунчера"""
        group = QGroupBox("Настройки лаунчера")
        group.setStyleSheet(f"""
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
            }}
        """)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                  UI["padding_medium"], UI["padding_medium"])
        layout.setSpacing(UI["spacing_medium"])

        # Закрытие при запуске игры
        self.close_on_launch_checkbox = QCheckBox("Закрывать лаунчер при запуске игры")
        self.close_on_launch_checkbox.setChecked(self.settings.close_on_launch)
        self.close_on_launch_checkbox.setStyleSheet(f"""
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
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['accent_primary']};
                border: 2px solid {COLORS['accent_primary']};
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {COLORS['text_primary']};
            }}
        """)

        # Проверка обновлений
        self.check_updates_checkbox = QCheckBox("Автоматически проверять обновления")
        self.check_updates_checkbox.setChecked(self.settings.check_updates)
        self.check_updates_checkbox.setStyleSheet(self.close_on_launch_checkbox.styleSheet())

        # Включение анимаций
        self.enable_animations_checkbox = QCheckBox("Включить анимации")
        self.enable_animations_checkbox.setChecked(self.settings.enable_animations)
        self.enable_animations_checkbox.setStyleSheet(self.close_on_launch_checkbox.styleSheet())

        # Включение звуков
        self.enable_sounds_checkbox = QCheckBox("Включить звуковые эффекты")
        self.enable_sounds_checkbox.setChecked(self.settings.enable_sounds)
        self.enable_sounds_checkbox.setStyleSheet(self.close_on_launch_checkbox.styleSheet())

        # Язык интерфейса
        language_container = QWidget()
        language_layout = QHBoxLayout(language_container)
        language_layout.setContentsMargins(0, 0, 0, 0)
        language_layout.setSpacing(UI["spacing_small"])

        language_label = QLabel("Язык интерфейса:")
        language_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['sizes']['normal']}px;
        """)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["Автоматически", "Русский", "English"])

        # Устанавливаем текущее значение
        current_lang = self.settings.language
        if current_lang == "auto":
            self.language_combo.setCurrentIndex(0)
        elif current_lang == "ru":
            self.language_combo.setCurrentIndex(1)
        elif current_lang == "en":
            self.language_combo.setCurrentIndex(2)

        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo, 1)

        # Добавление элементов в группу
        layout.addWidget(self.close_on_launch_checkbox)
        layout.addWidget(self.check_updates_checkbox)
        layout.addWidget(self.enable_animations_checkbox)
        layout.addWidget(self.enable_sounds_checkbox)
        layout.addWidget(language_container)

        self.settings_layout.addWidget(group)

    def _create_game_settings_group(self):
        """Создание группы настроек игры"""
        group = QGroupBox("Настройки игры по умолчанию")
        group.setStyleSheet(f"""
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
            }}
        """)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                  UI["padding_medium"], UI["padding_medium"])
        layout.setSpacing(UI["spacing_medium"])

        # Настройки памяти
        memory_container = QWidget()
        memory_layout = QVBoxLayout(memory_container)
        memory_layout.setContentsMargins(0, 0, 0, 0)
        memory_layout.setSpacing(UI["spacing_small"])

        memory_label = QLabel("Выделяемая память (RAM):")
        memory_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['sizes']['normal']}px;
        """)

        memory_slider_container = QWidget()
        memory_slider_layout = QHBoxLayout(memory_slider_container)
        memory_slider_layout.setContentsMargins(0, 0, 0, 0)
        memory_slider_layout.setSpacing(UI["spacing_small"])

        self.memory_slider = QSlider(Qt.Horizontal)
        self.memory_slider.setMinimum(1024)  # 1 GB
        self.memory_slider.setMaximum(16384)  # 16 GB
        self.memory_slider.setValue(4096)  # 4 GB по умолчанию
        self.memory_slider.setTickPosition(QSlider.TicksBelow)
        self.memory_slider.setTickInterval(1024)

        self.memory_value_label = QLabel("4 GB")
        self.memory_value_label.setMinimumWidth(60)
        self.memory_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.memory_value_label.setStyleSheet(f"""
            color: {COLORS['accent_primary']};
            font-size: {FONTS['sizes']['normal']}px;
            font-weight: bold;
        """)

        # Подключаем обновление значения
        self.memory_slider.valueChanged.connect(
            lambda value: self.memory_value_label.setText(f"{value // 1024} GB")
        )

        memory_slider_layout.addWidget(self.memory_slider)
        memory_slider_layout.addWidget(self.memory_value_label)

        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(memory_slider_container)

        # Java аргументы
        java_args_container = QWidget()
        java_args_layout = QVBoxLayout(java_args_container)
        java_args_layout.setContentsMargins(0, 0, 0, 0)
        java_args_layout.setSpacing(UI["spacing_small"])

        java_args_label = QLabel("Дополнительные аргументы JVM:")
        java_args_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['sizes']['normal']}px;
        """)

        self.java_args_input = QLineEdit()
        self.java_args_input.setPlaceholderText("Введите дополнительные JVM аргументы...")
        self.java_args_input.setText("-XX:+UnlockExperimentalVMOptions -XX:+UseG1GC")

        java_args_layout.addWidget(java_args_label)
        java_args_layout.addWidget(self.java_args_input)

        # Добавление элементов в группу
        layout.addWidget(memory_container)
        layout.addWidget(java_args_container)

        self.settings_layout.addWidget(group)

    def _create_system_info_group(self):
        """Создание группы системной информации"""
        group = QGroupBox("Системная информация")
        group.setStyleSheet(f"""
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
            }}
        """)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                  UI["padding_medium"], UI["padding_medium"])
        layout.setSpacing(UI["spacing_small"])

        # Получаем системную информацию
        import platform
        import psutil

        # Операционная система
        os_info = f"{platform.system()} {platform.release()}"
        os_label = QLabel(f"Операционная система: {os_info}")
        os_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['sizes']['small']}px;
        """)

        # Архитектура
        arch_label = QLabel(f"Архитектура: {platform.machine()}")
        arch_label.setStyleSheet(os_label.styleSheet())

        # Объем RAM
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3))
        ram_label = QLabel(f"Оперативная память: {ram_gb} GB")
        ram_label.setStyleSheet(os_label.styleSheet())

        # Python версия
        python_version = f"{platform.python_version()}"
        python_label = QLabel(f"Python версия: {python_version}")
        python_label.setStyleSheet(os_label.styleSheet())

        # Добавление элементов в группу
        layout.addWidget(os_label)
        layout.addWidget(arch_label)
        layout.addWidget(ram_label)
        layout.addWidget(python_label)

        self.settings_layout.addWidget(group)

    def _create_about_group(self):
        """Создание группы о программе"""
        group = QGroupBox("О программе")
        group.setStyleSheet(f"""
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
            }}
        """)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                  UI["padding_medium"], UI["padding_medium"])
        layout.setSpacing(UI["spacing_medium"])

        # Название и версия
        app_info_label = QLabel(f"SUPLAUNCHER v{APP_VERSION}")
        app_info_label.setStyleSheet(f"""
            color: {COLORS['accent_primary']};
            font-size: {FONTS['sizes']['large']}px;
            font-weight: bold;
        """)

        # Описание
        description_label = QLabel("Современный Minecraft лаунчер с минималистичным дизайном")
        description_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['sizes']['normal']}px;
        """)
        description_label.setWordWrap(True)

        # Ссылки
        links_container = QWidget()
        links_layout = QHBoxLayout(links_container)
        links_layout.setContentsMargins(0, 0, 0, 0)
        links_layout.setSpacing(UI["spacing_medium"])

        # Кнопка сайта
        website_button = AnimatedButton("Официальный сайт")
        website_button.setMinimumHeight(36)
        website_button.clicked.connect(lambda: webbrowser.open("https://villadesup.ru"))

        # Кнопка открытия папки данных
        data_folder_button = AnimatedButton("Папка данных")
        data_folder_button.setMinimumHeight(36)
        data_folder_button.clicked.connect(self._open_data_folder)

        # Кнопка логов
        logs_button = AnimatedButton("Папка логов")
        logs_button.setMinimumHeight(36)
        logs_button.clicked.connect(self._open_logs_folder)

        links_layout.addWidget(website_button)
        links_layout.addWidget(data_folder_button)
        links_layout.addWidget(logs_button)
        links_layout.addStretch(1)

        # Добавление элементов в группу
        layout.addWidget(app_info_label)
        layout.addWidget(description_label)
        layout.addWidget(links_container)

        self.settings_layout.addWidget(group)

    def _save_settings(self):
        """Сохранение настроек"""
        # Обновляем настройки из UI
        self.settings.close_on_launch = self.close_on_launch_checkbox.isChecked()
        self.settings.check_updates = self.check_updates_checkbox.isChecked()
        self.settings.enable_animations = self.enable_animations_checkbox.isChecked()
        self.settings.enable_sounds = self.enable_sounds_checkbox.isChecked()

        # Язык
        lang_index = self.language_combo.currentIndex()
        if lang_index == 0:
            self.settings.language = "auto"
        elif lang_index == 1:
            self.settings.language = "ru"
        elif lang_index == 2:
            self.settings.language = "en"

        # Сохраняем и уведомляем
        if self.settings.save():
            self.settingsChanged.emit(self.settings)

            # Показываем подтверждение
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Настройки сохранены")
            msg.setText("Настройки успешно сохранены.")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)

            # Стилизация
            msg.setStyleSheet(f"""
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
            """)

            msg.exec_()

    def _reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        from PySide6.QtWidgets import QMessageBox

        # Диалог подтверждения
        msg = QMessageBox(self)
        msg.setWindowTitle("Сброс настроек")
        msg.setText("Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        # Стилизация
        msg.setStyleSheet(f"""
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
        """)

        result = msg.exec_()

        if result == QMessageBox.Yes:
            # Создаем новые настройки по умолчанию
            self.settings = LauncherSettings()

            # Обновляем UI
            self._update_ui_from_settings()

            # Сохраняем
            self._save_settings()

    def _update_ui_from_settings(self):
        """Обновление UI на основе текущих настроек"""
        self.close_on_launch_checkbox.setChecked(self.settings.close_on_launch)
        self.check_updates_checkbox.setChecked(self.settings.check_updates)
        self.enable_animations_checkbox.setChecked(self.settings.enable_animations)
        self.enable_sounds_checkbox.setChecked(self.settings.enable_sounds)

        # Язык
        if self.settings.language == "auto":
            self.language_combo.setCurrentIndex(0)
        elif self.settings.language == "ru":
            self.language_combo.setCurrentIndex(1)
        elif self.settings.language == "en":
            self.language_combo.setCurrentIndex(2)

    def _open_data_folder(self):
        """Открытие папки данных лаунчера"""
        import os
        import subprocess
        import platform

        data_dir = self.paths.data_dir

        try:
            if platform.system() == "Windows":
                os.startfile(data_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", data_dir])
            else:  # Linux
                subprocess.run(["xdg-open", data_dir])
        except Exception as e:
            print(f"Не удалось открыть папку: {e}")

    # Настройки тщательно продуманы для Юра

    def _open_logs_folder(self):
        """Открытие папки логов"""
        import os
        import subprocess
        import platform

        logs_dir = self.paths.log_dir

        try:
            if platform.system() == "Windows":
                os.startfile(logs_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", logs_dir])
            else:  # Linux
                subprocess.run(["xdg-open", logs_dir])
        except Exception as e:
            print(f"Не удалось открыть папку: {e}")
