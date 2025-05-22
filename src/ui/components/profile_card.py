from PySide6.QtCore import Qt, QSize, Signal, QRect, QPoint, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QLinearGradient, QFont

from core.config import COLORS, UI, FONTS
from core.paths import Paths
from models.profile import Profile


class ProfileCard(QWidget):
    """Карточка профиля для отображения в списке"""

    # Сигналы
    selected = Signal(str)  # Сигнал выбора профиля (передает ID)
    play = Signal(str)  # Сигнал запуска профиля (передает ID)
    edit = Signal(str)  # Сигнал редактирования профиля (передает ID)
    delete = Signal(str)  # Сигнал удаления профиля (передает ID)

    def __init__(self, profile: Profile, parent=None):
        super().__init__(parent)
        self.paths = Paths()
        self.profile = profile
        self.is_selected = False

        # Анимационные значения
        self._hover_value = 0.0
        self._animation = QPropertyAnimation(self, b"hover_value")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

        # Настройка размеров
        self.setFixedSize(UI["card_width"], UI["card_height"])
        self.setMouseTracking(True)

        # Инициализация UI
        self._init_ui()

    def _init_ui(self):
        """Инициализация интерфейса карточки"""
        # Основной layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Верхняя часть карточки - основная информация
        self.info_container = QWidget()
        self.info_container.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")
        self.info_layout = QVBoxLayout(self.info_container)
        self.info_layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"], UI["padding_medium"],
                                            UI["padding_medium"])
        self.info_layout.setSpacing(UI["spacing_small"])

        # Иконка версии
        version_icon_container = QWidget()
        version_icon_layout = QHBoxLayout(version_icon_container)
        version_icon_layout.setContentsMargins(0, 0, 0, 0)

        self.version_icon = QLabel()

        # Определение иконки на основе типа загрузчика
        icon_name = "minecraft.svg"
        if self.profile.loader_type == "forge":
            icon_name = "forge.svg"
        elif self.profile.loader_type == "fabric":
            icon_name = "fabric.svg"
        elif self.profile.loader_type == "quilt":
            icon_name = "quilt.svg"

        icon_path = self.paths.get_resource_path("icon", icon_name)
        pixmap = QPixmap(icon_path)
        self.version_icon.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Название версии
        self.version_label = QLabel(self.profile.version_id)
        self.version_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['sizes']['small']}px;
        """)

        version_icon_layout.addWidget(self.version_icon)
        version_icon_layout.addWidget(self.version_label)
        version_icon_layout.addStretch()

        # Название профиля
        self.name_label = QLabel(self.profile.name)
        self.name_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['sizes']['large']}px;
            font-weight: bold;
        """)
        self.name_label.setWordWrap(True)

        # Тип загрузчика
        loader_text = "Vanilla"
        if self.profile.loader_type:
            loader_text = f"{self.profile.loader_type.capitalize()}"
            if self.profile.loader_version:
                loader_text += f" {self.profile.loader_version}"

        self.loader_label = QLabel(loader_text)
        self.loader_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['sizes']['small']}px;
        """)

        # Добавление элементов в layout верхней части
        self.info_layout.addWidget(version_icon_container)
        self.info_layout.addWidget(self.name_label)
        self.info_layout.addWidget(self.loader_label)
        self.info_layout.addStretch()

        # Нижняя часть карточки - кнопки
        self.buttons_container = QWidget()
        self.buttons_container.setStyleSheet(f"background-color: {COLORS['bg_tertiary']};")
        self.buttons_layout = QHBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(UI["padding_medium"], UI["padding_small"], UI["padding_medium"],
                                               UI["padding_small"])
        self.buttons_layout.setSpacing(UI["spacing_small"])

        # Кнопка запуска
        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon(self.paths.get_resource_path("icon", "play.svg")))
        self.play_button.setFixedSize(32, 32)
        self.play_button.setToolTip("Запустить")
        self.play_button.setCursor(Qt.PointingHandCursor)
        self.play_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_primary']};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_primary']}CC;
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent_primary']}99;
            }}
        """)
        self.play_button.clicked.connect(lambda: self.play.emit(self.profile.id))

        # Кнопка редактирования
        self.edit_button = QPushButton()
        self.edit_button.setIcon(QIcon(self.paths.get_resource_path("icon", "edit.svg")))
        self.edit_button.setFixedSize(32, 32)
        self.edit_button.setToolTip("Редактировать")
        self.edit_button.setCursor(Qt.PointingHandCursor)
        self.edit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_primary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['bg_secondary']};
            }}
        """)
        self.edit_button.clicked.connect(lambda: self.edit.emit(self.profile.id))

        # Кнопка удаления
        self.delete_button = QPushButton()
        self.delete_button.setIcon(QIcon(self.paths.get_resource_path("icon", "trash.svg")))
        self.delete_button.setFixedSize(32, 32)
        self.delete_button.setToolTip("Удалить")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_error']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent_error']}99;
            }}
        """)
        self.delete_button.clicked.connect(lambda: self.delete.emit(self.profile.id))

        # Добавление кнопок в layout нижней части
        self.buttons_layout.addWidget(self.play_button)
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.edit_button)
        self.buttons_layout.addWidget(self.delete_button)

        # Добавление контейнеров в основной layout
        self.layout.addWidget(self.info_container, 85)
        self.layout.addWidget(self.buttons_container, 15)

    def enterEvent(self, event):
        """Курсор входит в область виджета"""
        self._animation.stop()
        self._animation.setStartValue(self._hover_value)
        self._animation.setEndValue(1.0)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Курсор покидает область виджета"""
        self._animation.stop()
        self._animation.setStartValue(self._hover_value)
        self._animation.setEndValue(0.0)
        self._animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.profile.id)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool):
        """Установка состояния выбора"""
        self.is_selected = selected
        self.update()

    def paintEvent(self, event):
        """Отрисовка карточки с эффектами"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Отрисовка выделения, если карточка выбрана
        if self.is_selected:
            # Создание градиента для обводки
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(COLORS["accent_primary"]))
            gradient.setColorAt(1, QColor(COLORS["accent_secondary"]))

            # Отрисовка обводки
            pen = QPen()
            pen.setBrush(QBrush(gradient))
            pen.setWidth(2)
            painter.setPen(pen)

            # Отрисовка прямоугольника с закругленными углами
            rect = self.rect().adjusted(1, 1, -1, -1)
            painter.drawRoundedRect(rect, 8, 8)

        # Эффект при наведении
        if self._hover_value > 0:
            # Создание полупрозрачного цвета подсветки
            hover_color = QColor(COLORS["accent_primary"])
            hover_color.setAlphaF(0.1 * self._hover_value)

            # Отрисовка подсветки
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(hover_color))
            painter.drawRoundedRect(self.rect(), 8, 8)

    # Свойство для анимации
    def _get_hover_value(self):
        return self._hover_value

    def _set_hover_value(self, value):
        self._hover_value = value
        self.update()

    hover_value = Property(float, _get_hover_value, _set_hover_value)

    def update_profile_data(self, profile: Profile):
        """Обновление данных профиля"""
        self.profile = profile

        # Обновление отображаемых данных
        self.name_label.setText(self.profile.name)
        self.version_label.setText(self.profile.version_id)

        # Обновление типа загрузчика
        loader_text = "Vanilla"
        if self.profile.loader_type:
            loader_text = f"{self.profile.loader_type.capitalize()}"
            if self.profile.loader_version:
                loader_text += f" {self.profile.loader_version}"
        self.loader_label.setText(loader_text)

        # Обновление иконки
        icon_name = "minecraft.svg"
        if self.profile.loader_type == "forge":
            icon_name = "forge.svg"
        elif self.profile.loader_type == "fabric":
            icon_name = "fabric.svg"
        elif self.profile.loader_type == "quilt":
            icon_name = "quilt.svg"

        icon_path = self.paths.get_resource_path("icon", icon_name)
        pixmap = QPixmap(icon_path)
        self.version_icon.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
