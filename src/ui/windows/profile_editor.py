from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QComboBox, QSpinBox, QCheckBox,
                               QGroupBox, QFrame, QPushButton, QFileDialog,
                               QTextEdit, QTabWidget, QWidget, QMessageBox,
                               QSlider, QFormLayout)
from PySide6.QtGui import QIcon, QFont, QPixmap

from core.config import COLORS, UI, FONTS
from core.paths import Paths
from models.profile import Profile
from ui.components.animated_button import AnimatedButton


class ProfileEditor(QDialog):
    """Редактор профиля Minecraft"""

    # Сигналы
    profileSaved = Signal(object)  # Profile объект

    def __init__(self, profile: Profile = None, parent=None):
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.paths = Paths()
        self.profile = profile or Profile()
        self.is_new_profile = profile is None

        # Настройка окна
        self.setWindowTitle("Новый профиль" if self.is_new_profile else f"Редактирование: {self.profile.name}")
        self.setModal(True)
        self.setMinimumSize(500, 600)
        self.resize(600, 700)

        # Инициализация UI
        self._init_ui()

        # Загружаем данные профиля в UI
        if not self.is_new_profile:
            self._load_profile_to_ui()

    def _init_ui(self):
        """Инициализация интерфейса"""
        # Основной layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(UI["padding_large"], UI["padding_large"],
                                       UI["padding_large"], UI["padding_large"])
        self.layout.setSpacing(UI["spacing_large"])

        # Заголовок
        self.title_label = QLabel("Новый профиль" if self.is_new_profile else "Редактирование профиля")
        self.title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-family: "{FONTS['secondary']}";
            font-size: {FONTS['sizes']['xl']}px;
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
        self._create_version_tab()
        self._create_java_tab()
        self._create_game_tab()

        # Кнопки действий
        self.buttons_container = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(UI["spacing_medium"])

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

        # Основная информация
        info_group = QGroupBox("Основная информация")
        info_group.setStyleSheet(self._get_group_style())
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(UI["spacing_small"])

        # Название профиля
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название профиля")
        self.name_input.setStyleSheet(self._get_input_style())
        info_layout.addRow("Название:", self.name_input)

        # Описание
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Краткое описание профиля (необязательно)")
        self.description_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 6px;
                padding: 8px;
                color: {COLORS['text_primary']};
            }}
            QTextEdit:focus {{
                border: 2px solid {COLORS['accent_primary']};
            }}
        """)
        info_layout.addRow("Описание:", self.description_input)

        # Иконка профиля
        icon_container = QWidget()
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(UI["spacing_small"])

        self.icon_combo = QComboBox()
        self.icon_combo.addItems(["По умолчанию", "Forge", "Fabric", "Vanilla", "Модпак"])
        self.icon_combo.setStyleSheet(self._get_combo_style())

        self.icon_preview = QLabel()
        self.icon_preview.setFixedSize(32, 32)
        self.icon_preview.setStyleSheet(f"""
            border: 1px solid {COLORS['border_light']};
            border-radius: 4px;
            background-color: {COLORS['bg_primary']};
        """)
        self.icon_preview.setAlignment(Qt.AlignCenter)
        self.icon_preview.setText("📦")  # Эмодзи по умолчанию

        icon_layout.addWidget(self.icon_combo, 1)
        icon_layout.addWidget(self.icon_preview)

        info_layout.addRow("Иконка:", icon_container)

        # Директория игры
        game_dir_container = QWidget()
        game_dir_layout = QHBoxLayout(game_dir_container)
        game_dir_layout.setContentsMargins(0, 0, 0, 0)
        game_dir_layout.setSpacing(UI["spacing_small"])

        self.game_dir_input = QLineEdit()
        self.game_dir_input.setPlaceholderText("По умолчанию (автоматически)")
        self.game_dir_input.setStyleSheet(self._get_input_style())

        self.browse_button = QPushButton("Обзор...")
        self.browse_button.setMinimumHeight(32)
        self.browse_button.clicked.connect(self._browse_game_directory)

        game_dir_layout.addWidget(self.game_dir_input, 1)
        game_dir_layout.addWidget(self.browse_button)

        info_layout.addRow("Директория игры:", game_dir_container)

        # Добавление групп в layout
        layout.addWidget(info_group)
        layout.addStretch(1)

        self.tab_widget.addTab(tab, "Общие")

    def _create_version_tab(self):
        """Создание вкладки версии"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                  UI["padding_medium"], UI["padding_medium"])
        layout.setSpacing(UI["spacing_medium"])

        # Версия Minecraft
        version_group = QGroupBox("Версия Minecraft")
        version_group.setStyleSheet(self._get_group_style())
        version_layout = QFormLayout(version_group)
        version_layout.setSpacing(UI["spacing_small"])

        self.version_combo = QComboBox()
        self.version_combo.setEditable(True)
        self.version_combo.setStyleSheet(self._get_combo_style())

        # Добавляем популярные версии
        versions = ["1.20.1", "1.19.4", "1.18.2", "1.17.1", "1.16.5", "1.15.2", "1.14.4", "1.12.2"]
        self.version_combo.addItems(versions)

        version_layout.addRow("Версия:", self.version_combo)

        # Загрузчик модов
        loader_group = QGroupBox("Загрузчик модов")
        loader_group.setStyleSheet(self._get_group_style())
        loader_layout = QVBoxLayout(loader_group)
        loader_layout.setSpacing(UI["spacing_small"])

        # Тип загрузчика
        loader_type_container = QWidget()
        loader_type_layout = QHBoxLayout(loader_type_container)
        loader_type_layout.setContentsMargins(0, 0, 0, 0)
        loader_type_layout.setSpacing(UI["spacing_medium"])

        self.vanilla_radio = QCheckBox("Vanilla (без модов)")
        self.forge_radio = QCheckBox("Forge")
        self.fabric_radio = QCheckBox("Fabric")

        # Делаем радио-кнопки взаимоисключающими
        self.vanilla_radio.toggled.connect(lambda checked: self._on_loader_changed("vanilla", checked))
        self.forge_radio.toggled.connect(lambda checked: self._on_loader_changed("forge", checked))
        self.fabric_radio.toggled.connect(lambda checked: self._on_loader_changed("fabric", checked))

        for radio in [self.vanilla_radio, self.forge_radio, self.fabric_radio]:
            radio.setStyleSheet(self._get_checkbox_style())

        loader_type_layout.addWidget(self.vanilla_radio)
        loader_type_layout.addWidget(self.forge_radio)
        loader_type_layout.addWidget(self.fabric_radio)
        loader_type_layout.addStretch(1)

        # Версия загрузчика
        self.loader_version_combo = QComboBox()
        self.loader_version_combo.setEditable(True)
        self.loader_version_combo.setEnabled(False)
        self.loader_version_combo.setStyleSheet(self._get_combo_style())

        loader_layout.addWidget(loader_type_container)
        loader_layout.addWidget(QLabel("Версия загрузчика:"))
        loader_layout.addWidget(self.loader_version_combo)

        # По умолчанию выбираем Vanilla
        self.vanilla_radio.setChecked(True)

        # Добавление групп в layout
        layout.addWidget(version_group)
        layout.addWidget(loader_group)
        layout.addStretch(1)

        self.tab_widget.addTab(tab, "Версия")

    def _create_java_tab(self):
        """Создание вкладки настроек Java"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                  UI["padding_medium"], UI["padding_medium"])
        layout.setSpacing(UI["spacing_medium"])

        # Настройки Java
        java_group = QGroupBox("Настройки Java")
        java_group.setStyleSheet(self._get_group_style())
        java_layout = QFormLayout(java_group)
        java_layout.setSpacing(UI["spacing_small"])

        # Путь к Java
        java_path_container = QWidget()
        java_path_layout = QHBoxLayout(java_path_container)
        java_path_layout.setContentsMargins(0, 0, 0, 0)
        java_path_layout.setSpacing(UI["spacing_small"])

        self.java_path_input = QLineEdit()
        self.java_path_input.setPlaceholderText("Автоматическое определение")
        self.java_path_input.setStyleSheet(self._get_input_style())

        self.java_browse_button = QPushButton("Обзор...")
        self.java_browse_button.setMinimumHeight(32)
        self.java_browse_button.clicked.connect(self._browse_java_path)

        java_path_layout.addWidget(self.java_path_input, 1)
        java_path_layout.addWidget(self.java_browse_button)

        java_layout.addRow("Путь к Java:", java_path_container)

        # JVM аргументы
        self.jvm_args_input = QLineEdit()
        self.jvm_args_input.setPlaceholderText("-XX:+UnlockExperimentalVMOptions -XX:+UseG1GC")
        self.jvm_args_input.setStyleSheet(self._get_input_style())
        java_layout.addRow("JVM аргументы:", self.jvm_args_input)

        # Настройки памяти
        memory_group = QGroupBox("Настройки памяти")
        memory_group.setStyleSheet(self._get_group_style())
        memory_layout = QVBoxLayout(memory_group)
        memory_layout.setSpacing(UI["spacing_medium"])

        # Слайдер памяти
        memory_slider_container = QWidget()
        memory_slider_layout = QVBoxLayout(memory_slider_container)
        memory_slider_layout.setSpacing(UI["spacing_small"])

        self.memory_label = QLabel("Выделяемая память: 4 GB")
        self.memory_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-weight: bold;
        """)

        self.memory_slider = QSlider(Qt.Horizontal)
        self.memory_slider.setMinimum(1024)  # 1 GB
        self.memory_slider.setMaximum(16384)  # 16 GB
        self.memory_slider.setValue(4096)  # 4 GB по умолчанию
        self.memory_slider.setTickPosition(QSlider.TicksBelow)
        self.memory_slider.setTickInterval(1024)
        self.memory_slider.valueChanged.connect(self._on_memory_changed)

        memory_slider_layout.addWidget(self.memory_label)
        memory_slider_layout.addWidget(self.memory_slider)

        # Точные значения
        precise_memory_container = QWidget()
        precise_memory_layout = QHBoxLayout(precise_memory_container)
        precise_memory_layout.setContentsMargins(0, 0, 0, 0)
        precise_memory_layout.setSpacing(UI["spacing_medium"])

        # Минимальная память
        min_memory_container = QWidget()
        min_memory_layout = QVBoxLayout(min_memory_container)
        min_memory_layout.setContentsMargins(0, 0, 0, 0)
        min_memory_layout.setSpacing(2)

        min_memory_label = QLabel("Минимум (MB):")
        min_memory_label.setStyleSheet(f"color: {COLORS['text_secondary']};")

        self.min_memory_spinbox = QSpinBox()
        self.min_memory_spinbox.setMinimum(512)
        self.min_memory_spinbox.setMaximum(32768)
        self.min_memory_spinbox.setValue(2048)
        self.min_memory_spinbox.setSuffix(" MB")

        min_memory_layout.addWidget(min_memory_label)
        min_memory_layout.addWidget(self.min_memory_spinbox)

        # Максимальная память
        max_memory_container = QWidget()
        max_memory_layout = QVBoxLayout(max_memory_container)
        max_memory_layout.setContentsMargins(0, 0, 0, 0)
        max_memory_layout.setSpacing(2)

        max_memory_label = QLabel("Максимум (MB):")
        max_memory_label.setStyleSheet(f"color: {COLORS['text_secondary']};")

        self.max_memory_spinbox = QSpinBox()
        self.max_memory_spinbox.setMinimum(1024)
        self.max_memory_spinbox.setMaximum(32768)
        self.max_memory_spinbox.setValue(4096)
        self.max_memory_spinbox.setSuffix(" MB")
        self.max_memory_spinbox.valueChanged.connect(self._on_max_memory_changed)

        max_memory_layout.addWidget(max_memory_label)
        max_memory_layout.addWidget(self.max_memory_spinbox)

        precise_memory_layout.addWidget(min_memory_container)
        precise_memory_layout.addWidget(max_memory_container)
        precise_memory_layout.addStretch(1)

        memory_layout.addWidget(memory_slider_container)
        memory_layout.addWidget(precise_memory_container)

        # Добавление групп в layout
        layout.addWidget(java_group)
        layout.addWidget(memory_group)
        layout.addStretch(1)

        self.tab_widget.addTab(tab, "Java")

    def _create_game_tab(self):
        """Создание вкладки игровых настроек"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                  UI["padding_medium"], UI["padding_medium"])
        layout.setSpacing(UI["spacing_medium"])

        # Настройки окна
        window_group = QGroupBox("Настройки окна")
        window_group.setStyleSheet(self._get_group_style())
        window_layout = QFormLayout(window_group)
        window_layout.setSpacing(UI["spacing_small"])

        # Полноэкранный режим
        self.fullscreen_checkbox = QCheckBox("Полноэкранный режим")
        self.fullscreen_checkbox.setStyleSheet(self._get_checkbox_style())
        self.fullscreen_checkbox.toggled.connect(self._on_fullscreen_changed)
        window_layout.addRow(self.fullscreen_checkbox)

        # Разрешение окна
        resolution_container = QWidget()
        resolution_layout = QHBoxLayout(resolution_container)
        resolution_layout.setContentsMargins(0, 0, 0, 0)
        resolution_layout.setSpacing(UI["spacing_small"])

        self.width_spinbox = QSpinBox()
        self.width_spinbox.setMinimum(640)
        self.width_spinbox.setMaximum(7680)
        self.width_spinbox.setValue(854)
        self.width_spinbox.setSuffix(" px")

        x_label = QLabel("×")
        x_label.setAlignment(Qt.AlignCenter)
        x_label.setStyleSheet(f"color: {COLORS['text_secondary']};")

        self.height_spinbox = QSpinBox()
        self.height_spinbox.setMinimum(480)
        self.height_spinbox.setMaximum(4320)
        self.height_spinbox.setValue(480)
        self.height_spinbox.setSuffix(" px")

        # Кнопки быстрых разрешений
        resolution_presets_container = QWidget()
        resolution_presets_layout = QHBoxLayout(resolution_presets_container)
        resolution_presets_layout.setContentsMargins(0, 0, 0, 0)
        resolution_presets_layout.setSpacing(4)

        presets = [
            ("854×480", 854, 480),
            ("1280×720", 1280, 720),
            ("1920×1080", 1920, 1080),
            ("2560×1440", 2560, 1440)
        ]

        for name, width, height in presets:
            preset_button = QPushButton(name)
            preset_button.setMaximumHeight(24)
            preset_button.clicked.connect(lambda checked, w=width, h=height: self._set_resolution(w, h))
            preset_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_tertiary']};
                    border: 1px solid {COLORS['border_light']};
                    border-radius: 4px;
                    padding: 2px 6px;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['accent_primary']};
                }}
            """)
            resolution_presets_layout.addWidget(preset_button)

        resolution_presets_layout.addStretch(1)

        resolution_layout.addWidget(self.width_spinbox)
        resolution_layout.addWidget(x_label)
        resolution_layout.addWidget(self.height_spinbox)
        resolution_layout.addStretch(1)

        self.resolution_container = QWidget()
        resolution_main_layout = QVBoxLayout(self.resolution_container)
        resolution_main_layout.setContentsMargins(0, 0, 0, 0)
        resolution_main_layout.setSpacing(4)
        resolution_main_layout.addWidget(resolution_container)
        resolution_main_layout.addWidget(resolution_presets_container)

        window_layout.addRow("Разрешение:", self.resolution_container)

        # Дополнительные настройки
        extra_group = QGroupBox("Дополнительные настройки")
        extra_group.setStyleSheet(self._get_group_style())
        extra_layout = QVBoxLayout(extra_group)
        extra_layout.setSpacing(UI["spacing_small"])

        # Автозапуск
        self.auto_join_checkbox = QCheckBox("Автоподключение к серверу (в разработке)")
        self.auto_join_checkbox.setEnabled(False)
        self.auto_join_checkbox.setStyleSheet(self._get_checkbox_style())

        # Сервер для автоподключения
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("IP сервера (в разработке)")
        self.server_input.setEnabled(False)
        self.server_input.setStyleSheet(self._get_input_style())

        extra_layout.addWidget(self.auto_join_checkbox)
        extra_layout.addWidget(self.server_input)

        # Добавление групп в layout
        layout.addWidget(window_group)
        layout.addWidget(extra_group)
        layout.addStretch(1)

        self.tab_widget.addTab(tab, "Игра")

    def _load_profile_to_ui(self):
        """Загрузка данных профиля в элементы UI"""
        # Общая информация
        self.name_input.setText(self.profile.name)
        if hasattr(self.profile, 'description'):
            self.description_input.setPlainText(self.profile.custom_settings.get('description', ''))

        # Версия
        self.version_combo.setCurrentText(self.profile.version_id)

        # Загрузчик
        if self.profile.loader_type == "forge":
            self.forge_radio.setChecked(True)
        elif self.profile.loader_type == "fabric":
            self.fabric_radio.setChecked(True)
        else:
            self.vanilla_radio.setChecked(True)

        if self.profile.loader_version:
            self.loader_version_combo.setCurrentText(self.profile.loader_version)

        # Java настройки
        if self.profile.java_path:
            self.java_path_input.setText(self.profile.java_path)
        if self.profile.java_args:
            self.jvm_args_input.setText(self.profile.java_args)

        # Память
        self.min_memory_spinbox.setValue(self.profile.min_ram)
        self.max_memory_spinbox.setValue(self.profile.max_ram)
        self.memory_slider.setValue(self.profile.max_ram)
        self._on_memory_changed(self.profile.max_ram)

        # Игровые настройки
        self.fullscreen_checkbox.setChecked(self.profile.fullscreen)
        self.width_spinbox.setValue(self.profile.resolution_width)
        self.height_spinbox.setValue(self.profile.resolution_height)
        self._on_fullscreen_changed(self.profile.fullscreen)

        # Директория игры
        if self.profile.game_directory:
            self.game_dir_input.setText(self.profile.game_directory)

    def _save_profile_from_ui(self):
        """Сохранение данных из UI в профиль"""
        # Проверяем обязательные поля
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Название профиля не может быть пустым")
            return False

        # Общая информация
        self.profile.name = self.name_input.text().strip()

        # Сохраняем описание в custom_settings
        description = self.description_input.toPlainText().strip()
        if description:
            self.profile.custom_settings['description'] = description
        elif 'description' in self.profile.custom_settings:
            del self.profile.custom_settings['description']

        # Версия
        self.profile.version_id = self.version_combo.currentText()

        # Загрузчик
        if self.forge_radio.isChecked():
            self.profile.loader_type = "forge"
        elif self.fabric_radio.isChecked():
            self.profile.loader_type = "fabric"
        else:
            self.profile.loader_type = None

        if self.loader_version_combo.currentText():
            self.profile.loader_version = self.loader_version_combo.currentText()
        else:
            self.profile.loader_version = None

        # Java настройки
        self.profile.java_path = self.java_path_input.text().strip() or None
        self.profile.java_args = self.jvm_args_input.text().strip()

        # Память
        self.profile.min_ram = self.min_memory_spinbox.value()
        self.profile.max_ram = self.max_memory_spinbox.value()

        # Игровые настройки
        self.profile.fullscreen = self.fullscreen_checkbox.isChecked()
        self.profile.resolution_width = self.width_spinbox.value()
        self.profile.resolution_height = self.height_spinbox.value()

        # Директория игры
        self.profile.game_directory = self.game_dir_input.text().strip() or None

        return True

    def _save_and_close(self):
        """Сохранение профиля и закрытие окна"""
        if self._save_profile_from_ui():
            if self.profile.save():
                self.profileSaved.emit(self.profile)
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить профиль")

    def _on_loader_changed(self, loader_type: str, checked: bool):
        """Обработка изменения типа загрузчика"""
        if checked:
            # Отключаем другие радио-кнопки
            if loader_type != "vanilla":
                self.vanilla_radio.setChecked(False)
            if loader_type != "forge":
                self.forge_radio.setChecked(False)
            if loader_type != "fabric":
                self.fabric_radio.setChecked(False)

            # Включаем/отключаем выбор версии загрузчика
            self.loader_version_combo.setEnabled(loader_type != "vanilla")

            # Заполняем версии загрузчика
            if loader_type == "forge":
                self.loader_version_combo.clear()
                forge_versions = ["47.2.0", "47.1.0", "46.0.14"]  # Пример версий
                self.loader_version_combo.addItems(forge_versions)
            elif loader_type == "fabric":
                self.loader_version_combo.clear()
                fabric_versions = ["0.14.21", "0.14.20", "0.14.19"]  # Пример версий
                self.loader_version_combo.addItems(fabric_versions)
            else:
                self.loader_version_combo.clear()

    def _on_memory_changed(self, value: int):
        """Обработка изменения слайдера памяти"""
        gb_value = value / 1024
        self.memory_label.setText(f"Выделяемая память: {gb_value:.1f} GB")
        self.max_memory_spinbox.setValue(value)

    def _on_max_memory_changed(self, value: int):
        """Обработка изменения максимальной памяти в spinbox"""
        self.memory_slider.setValue(value)
        self._on_memory_changed(value)

    def _on_fullscreen_changed(self, checked: bool):
        """Обработка изменения полноэкранного режима"""
        self.resolution_container.setEnabled(not checked)

    def _set_resolution(self, width: int, height: int):
        """Установка предустановленного разрешения"""
        self.width_spinbox.setValue(width)
        self.height_spinbox.setValue(height)

    def _browse_game_directory(self):
        """Выбор директории игры"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите директорию для игры",
            self.game_dir_input.text() or self.paths.minecraft_dir
        )

        if dir_path:
            self.game_dir_input.setText(dir_path)

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

    def _get_input_style(self) -> str:
        """Получение стиля для полей ввода"""
        return f"""
            QLineEdit {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['accent_primary']};
            }}
        """

    def _get_combo_style(self) -> str:
        """Получение стиля для комбобоксов"""
        return f"""
            QComboBox {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {COLORS['text_primary']};
            }}
            QComboBox:focus {{
                border: 2px solid {COLORS['accent_primary']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border_light']};
                selection-background-color: {COLORS['accent_primary']};
            }}
        """

    def _get_checkbox_style(self) -> str:
        """Получение стиля для чекбоксов"""
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

# Редактор профилей создан с вниманием к деталям для Юра
