from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QRadioButton, QComboBox, QLineEdit, QPushButton,
                               QButtonGroup, QSpacerItem, QSizePolicy, QFrame)
from PySide6.QtGui import QIcon, QFont, QFontMetrics

from core.config import COLORS, UI, FONTS, ANIMATIONS
from core.paths import Paths
from ui.components.animated_button import AnimatedButton


class CreatorView(QWidget):
    """Заглушка для экрана создания сборок"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paths = Paths()

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
        self.title_label = QLabel("Создание Новой Сборки")
        self.title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-family: "{FONTS['secondary']}";
            font-size: {FONTS['sizes']['header']}px;
            font-weight: bold;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)

        # Контейнер для формы
        self.form_container = QWidget()
        self.form_container.setStyleSheet(f"""
            background-color: {COLORS['bg_secondary']};
            border-radius: {UI['border_radius']}px;
        """)

        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setContentsMargins(UI["padding_large"], UI["padding_large"],
                                            UI["padding_large"], UI["padding_large"])
        self.form_layout.setSpacing(UI["spacing_large"])

        # Тип загрузчика
        self.loader_container = QWidget()
        self.loader_layout = QVBoxLayout(self.loader_container)
        self.loader_layout.setContentsMargins(0, 0, 0, 0)
        self.loader_layout.setSpacing(UI["spacing_medium"])

        self.loader_label = QLabel("Выберите тип загрузчика:")
        self.loader_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['sizes']['large']}px;
            font-weight: bold;
        """)

        # Кнопки выбора загрузчика
        self.loader_buttons_container = QWidget()
        self.loader_buttons_layout = QHBoxLayout(self.loader_buttons_container)
        self.loader_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.loader_buttons_layout.setSpacing(UI["spacing_medium"])

        # Группа для radio-кнопок
        self.loader_group = QButtonGroup(self)

        # Forge
        self.forge_radio = QRadioButton("Forge")
        self.forge_radio.setStyleSheet(f"""
            QRadioButton {{
                color: {COLORS['text_primary']};
                font-size: {FONTS['sizes']['normal']}px;
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid {COLORS['text_secondary']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {COLORS['accent_primary']};
                border: 2px solid {COLORS['accent_primary']};
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {COLORS['text_primary']};
            }}
        """)
        self.forge_radio.setChecked(True)
        self.loader_group.addButton(self.forge_radio)

        # Fabric
        self.fabric_radio = QRadioButton("Fabric")
        self.fabric_radio.setStyleSheet(f"""
            QRadioButton {{
                color: {COLORS['text_primary']};
                font-size: {FONTS['sizes']['normal']}px;
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid {COLORS['text_secondary']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {COLORS['accent_primary']};
                border: 2px solid {COLORS['accent_primary']};
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {COLORS['text_primary']};
            }}
        """)
        self.loader_group.addButton(self.fabric_radio)

        # Добавление кнопок в контейнер
        self.loader_buttons_layout.addWidget(self.forge_radio)
        self.loader_buttons_layout.addWidget(self.fabric_radio)
        self.loader_buttons_layout.addStretch(1)

        # Добавление элементов в секцию загрузчика
        self.loader_layout.addWidget(self.loader_label)
        self.loader_layout.addWidget(self.loader_buttons_container)

        # Выбор версии Minecraft
        self.version_container = QWidget()
        self.version_layout = QVBoxLayout(self.version_container)
        self.version_layout.setContentsMargins(0, 0, 0, 0)
        self.version_layout.setSpacing(UI["spacing_small"])

        self.version_label = QLabel("Версия Minecraft:")
        self.version_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['sizes']['large']}px;
            font-weight: bold;
        """)

        self.version_combobox = QComboBox()
        self.version_combobox.setMinimumHeight(38)

        # Добавление примерных версий
        versions = ["1.20.1", "1.19.4", "1.18.2", "1.17.1", "1.16.5", "1.15.2", "1.14.4", "1.12.2"]
        for version in versions:
            self.version_combobox.addItem(version)

        # Добавление элементов в секцию версии
        self.version_layout.addWidget(self.version_label)
        self.version_layout.addWidget(self.version_combobox)

        # Название сборки
        self.name_container = QWidget()
        self.name_layout = QVBoxLayout(self.name_container)
        self.name_layout.setContentsMargins(0, 0, 0, 0)
        self.name_layout.setSpacing(UI["spacing_small"])

        self.name_label = QLabel("Название сборки:")
        self.name_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['sizes']['large']}px;
            font-weight: bold;
        """)

        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(38)
        self.name_input.setPlaceholderText("Введите название сборки")

        # Добавление элементов в секцию названия
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_input)

        # Кнопка создания и уведомление
        self.create_container = QWidget()
        self.create_layout = QVBoxLayout(self.create_container)
        self.create_layout.setContentsMargins(0, 0, 0, 0)
        self.create_layout.setSpacing(UI["spacing_medium"])
        self.create_layout.setAlignment(Qt.AlignCenter)

        # Кнопка создания (заблокированная)
        self.create_button = AnimatedButton("Создать сборку")
        self.create_button.setMinimumHeight(UI["button_height"])
        self.create_button.setMinimumWidth(200)
        self.create_button.setEnabled(False)  # Заблокирована
        self.create_button.clicked.connect(self._show_coming_soon)

        # Уведомление "В разработке"
        self.coming_soon_label = QLabel("Функционал в разработке. Coming soon!")
        self.coming_soon_label.setStyleSheet(f"""
            color: {COLORS['accent_secondary']};
            font-size: {FONTS['sizes']['normal']}px;
            font-style: italic;
        """)
        self.coming_soon_label.setAlignment(Qt.AlignCenter)

        # Добавление элементов в секцию создания
        self.create_layout.addWidget(self.create_button, 0, Qt.AlignCenter)
        self.create_layout.addWidget(self.coming_soon_label)

        # Добавление всех секций в форму
        self.form_layout.addWidget(self.loader_container)

        # Разделитель
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        self.form_layout.addWidget(separator1)

        self.form_layout.addWidget(self.version_container)

        # Разделитель
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        self.form_layout.addWidget(separator2)

        self.form_layout.addWidget(self.name_container)
        self.form_layout.addWidget(self.create_container)

        # Добавление всех элементов в основной layout
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.form_container, 1)

    def _show_coming_soon(self):
        """Показать сообщение, что функция в разработке"""
        # На будущее: здесь можно добавить анимацию или всплывающее окно
        pass
