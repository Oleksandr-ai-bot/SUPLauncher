from PySide6.QtCore import Qt, QPoint, Signal, QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtGui import QPixmap, QIcon, QMouseEvent, QFontMetrics

from core.config import COLORS, UI, FONTS
from core.paths import Paths


class CustomTitleBar(QWidget):
    """Кастомная панель заголовка окна"""

    # Сигналы
    minimizeClicked = Signal()
    maximizeClicked = Signal()
    closeClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paths = Paths()

        # Настройка виджета
        self.setFixedHeight(UI["title_bar_height"])
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {COLORS['bg_primary']};")

        # Настройка макета
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(UI["padding_medium"], 0, UI["padding_medium"], 0)
        self.layout.setSpacing(UI["spacing_small"])

        # Логотип
        self.logo_label = QLabel()
        logo_path = self.paths.get_resource_path("image", "logo.png")
        pixmap = QPixmap(logo_path)

        # Масштабирование логотипа
        scaled_height = int(UI["title_bar_height"] * 0.7)
        scaled_width = int(scaled_height * (pixmap.width() / pixmap.height()))
        self.logo_label.setPixmap(
            pixmap.scaled(scaled_width, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setFixedSize(scaled_width, scaled_height)

        # Заголовок
        self.title_label = QLabel("SUPLAUNCHER")
        self.title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-family: "{FONTS['secondary']}";
            font-size: {FONTS['sizes']['large']}px;
            font-weight: bold;
        """)

        # Кнопки управления окном
        # Минимизировать
        self.btn_minimize = QPushButton()
        self.btn_minimize.setIcon(QIcon(self.paths.get_resource_path("icon", "minimize.svg")))
        self.btn_minimize.setFixedSize(32, 32)
        self.btn_minimize.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_tertiary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['bg_secondary']};
            }}
        """)
        self.btn_minimize.clicked.connect(self.minimizeClicked)

        # Максимизировать
        self.btn_maximize = QPushButton()
        self.btn_maximize.setIcon(QIcon(self.paths.get_resource_path("icon", "maximize.svg")))
        self.btn_maximize.setFixedSize(32, 32)
        self.btn_maximize.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_tertiary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['bg_secondary']};
            }}
        """)
        self.btn_maximize.clicked.connect(self.maximizeClicked)

        # Закрыть
        self.btn_close = QPushButton()
        self.btn_close.setIcon(QIcon(self.paths.get_resource_path("icon", "close.svg")))
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_error']};
            }}
            QPushButton:pressed {{
                background-color: #CC3629;
            }}
        """)
        self.btn_close.clicked.connect(self.closeClicked)

        # Добавление элементов в макет
        self.layout.addWidget(self.logo_label)
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.layout.addWidget(self.btn_minimize)
        self.layout.addWidget(self.btn_maximize)
        self.layout.addWidget(self.btn_close)

        # Для перетаскивания окна
        self._dragging = False
        self._drag_position = QPoint()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Обработка нажатия для перетаскивания окна"""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.parent().pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Перетаскивание окна"""
        if self._dragging and event.buttons() & Qt.LeftButton:
            self.parent().move(event.globalPosition().toPoint() - self._drag_position)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Завершение перетаскивания"""
        if event.button() == Qt.LeftButton:
            self._dragging = False

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Двойной клик для максимизации/восстановления окна"""
        if event.button() == Qt.LeftButton:
            self.maximizeClicked.emit()
