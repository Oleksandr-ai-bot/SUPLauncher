from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QTimer, QRect, QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtGui import QIcon, QFont, QPainter, QColor, QBrush, QPen, QPixmap

from core.config import COLORS, UI, FONTS, ANIMATIONS
from core.paths import Paths


class Notification(QWidget):
    """Виджет уведомления с анимацией появления/исчезновения"""

    # Типы уведомлений
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

    def __init__(self, title: str, message: str, notification_type: str = INFO,
                 duration: int = 5000, parent=None):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.paths = Paths()
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.duration = duration

        # Настройка виджета
        self.setFixedSize(350, 100)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Анимационные значения
        self._opacity = 0.0
        self._offset = 50

        # Настройка анимаций
        self._setup_animations()

        # Инициализация UI
        self._init_ui()

        # Настройка тени
        self._setup_shadow()

        # Автоматическое скрытие
        if self.duration > 0:
            QTimer.singleShot(self.duration, self.hide_notification)

    def _setup_animations(self):
        """Настройка анимаций"""
        # Анимация прозрачности
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(ANIMATIONS["duration_medium"])
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)

        # Анимация смещения
        self.offset_animation = QPropertyAnimation(self, b"offset")
        self.offset_animation.setDuration(ANIMATIONS["duration_medium"])
        self.offset_animation.setEasingCurve(QEasingCurve.OutCubic)

    def _init_ui(self):
        """Инициализация интерфейса"""
        # Основной layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                       UI["padding_medium"], UI["padding_medium"])
        self.layout.setSpacing(UI["spacing_medium"])

        # Иконка типа уведомления
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # Определяем иконку и цвет по типу
        icon_name, self.accent_color = self._get_type_settings()

        # Загружаем иконку
        icon_path = self.paths.get_resource_path("icon", icon_name)
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                # Окрашиваем иконку в акцентный цвет
                colored_pixmap = self._color_pixmap(pixmap, QColor(self.accent_color))
                self.icon_label.setPixmap(colored_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Контейнер для текста
        self.text_container = QWidget()
        self.text_layout = QVBoxLayout(self.text_container)
        self.text_layout.setContentsMargins(0, 0, 0, 0)
        self.text_layout.setSpacing(2)

        # Заголовок
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['sizes']['normal']}px;
            font-weight: bold;
        """)
        self.title_label.setWordWrap(True)

        # Сообщение
        self.message_label = QLabel(self.message)
        self.message_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['sizes']['small']}px;
        """)
        self.message_label.setWordWrap(True)

        # Добавление элементов в текстовый контейнер
        self.text_layout.addWidget(self.title_label)
        self.text_layout.addWidget(self.message_label)
        self.text_layout.addStretch(1)

        # Кнопка закрытия
        self.close_button = QPushButton()
        self.close_button.setIcon(QIcon(self.paths.get_resource_path("icon", "close.svg")))
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_tertiary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['bg_primary']};
            }}
        """)
        self.close_button.clicked.connect(self.hide_notification)

        # Добавление элементов в основной layout
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_container, 1)
        self.layout.addWidget(self.close_button, 0, Qt.AlignTop)

    def _setup_shadow(self):
        """Настройка тени"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

    def _get_type_settings(self):
        """Получение настроек для типа уведомления"""
        if self.notification_type == self.SUCCESS:
            return "check.svg", COLORS["accent_success"]
        elif self.notification_type == self.WARNING:
            return "warning.svg", COLORS["accent_warning"]
        elif self.notification_type == self.ERROR:
            return "error.svg", COLORS["accent_error"]
        else:  # INFO
            return "info.svg", COLORS["accent_primary"]

    def _color_pixmap(self, pixmap: QPixmap, color: QColor) -> QPixmap:
        """Окрашивание иконки в заданный цвет"""
        colored_pixmap = QPixmap(pixmap.size())
        colored_pixmap.fill(Qt.transparent)

        painter = QPainter(colored_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(colored_pixmap.rect(), color)
        painter.end()

        return colored_pixmap

    def show_notification(self):
        """Показ уведомления с анимацией"""
        # Позиционируем уведомление
        self._position_notification()

        # Показываем виджет
        self.show()

        # Запускаем анимации появления
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()

        self.offset_animation.setStartValue(50)
        self.offset_animation.setEndValue(0)
        self.offset_animation.start()

    def hide_notification(self):
        """Скрытие уведомления с анимацией"""
        # Запускаем анимации исчезновения
        self.opacity_animation.setStartValue(self._opacity)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.finished.connect(self.close)
        self.opacity_animation.start()

        self.offset_animation.setStartValue(self._offset)
        self.offset_animation.setEndValue(-50)
        self.offset_animation.start()

    def _position_notification(self):
        """Позиционирование уведомления на экране"""
        if self.parent():
            # Позиционируем относительно родительского виджета
            parent_rect = self.parent().geometry()
            x = parent_rect.right() - self.width() - 20
            y = parent_rect.top() + 80
        else:
            # Позиционируем в правом верхнем углу экрана
            from PySide6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = screen.width() - self.width() - 20
            y = 80

        self.move(x, y)

    def paintEvent(self, event):
        """Отрисовка уведомления"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Применяем прозрачность
        painter.setOpacity(self._opacity)

        # Применяем смещение
        painter.translate(0, self._offset)

        # Отрисовка фона
        bg_color = QColor(COLORS["bg_secondary"])
        bg_color.setAlpha(int(240 * self._opacity))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(self.rect(), UI["border_radius"], UI["border_radius"])

        # Отрисовка акцентной полосы слева
        accent_color = QColor(self.accent_color)
        accent_color.setAlpha(int(255 * self._opacity))

        painter.setBrush(QBrush(accent_color))
        accent_rect = QRect(0, 0, 4, self.height())
        painter.drawRoundedRect(accent_rect, 2, 2)

    def mousePressEvent(self, event):
        """Обработка клика по уведомлению"""
        if event.button() == Qt.LeftButton:
            self.hide_notification()
        super().mousePressEvent(event)

    # Свойства для анимации
    def _get_opacity(self):
        return self._opacity

    def _set_opacity(self, value):
        self._opacity = value
        self.update()

    opacity = Property(float, _get_opacity, _set_opacity)

    def _get_offset(self):
        return self._offset

    def _set_offset(self, value):
        self._offset = value
        self.update()

    offset = Property(float, _get_offset, _set_offset)


class NotificationManager:
    """Менеджер для управления уведомлениями"""

    def __init__(self, parent=None):
        self.parent = parent
        self.notifications = []
        self.max_notifications = 5
        self.spacing = 10

    def show_notification(self, title: str, message: str,
                          notification_type: str = Notification.INFO,
                          duration: int = 5000):
        """Показ нового уведомления"""
        # Удаляем старые уведомления, если превышен лимит
        while len(self.notifications) >= self.max_notifications:
            old_notification = self.notifications.pop(0)
            old_notification.hide_notification()

        # Создаем новое уведомление
        notification = Notification(title, message, notification_type, duration, self.parent)

        # Позиционируем с учетом существующих уведомлений
        self._position_notification(notification)

        # Добавляем в список и показываем
        self.notifications.append(notification)
        notification.show_notification()

        # Удаляем из списка при закрытии
        notification.destroyed.connect(lambda: self._remove_notification(notification))

        return notification

    def _position_notification(self, notification):
        """Позиционирование уведомления с учетом существующих"""
        if self.parent:
            parent_rect = self.parent.geometry()
            x = parent_rect.right() - notification.width() - 20
            y = parent_rect.top() + 80 + len(self.notifications) * (notification.height() + self.spacing)
        else:
            from PySide6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = screen.width() - notification.width() - 20
            y = 80 + len(self.notifications) * (notification.height() + self.spacing)

        notification.move(x, y)

    def _remove_notification(self, notification):
        """Удаление уведомления из списка"""
        if notification in self.notifications:
            self.notifications.remove(notification)

            # Перепозиционируем оставшиеся уведомления
            self._reposition_notifications()

    def _reposition_notifications(self):
        """Перепозиционирование оставшихся уведомлений"""
        for i, notification in enumerate(self.notifications):
            if self.parent:
                parent_rect = self.parent.geometry()
                x = parent_rect.right() - notification.width() - 20
                y = parent_rect.top() + 80 + i * (notification.height() + self.spacing)
            else:
                from PySide6.QtWidgets import QApplication
                screen = QApplication.primaryScreen().geometry()
                x = screen.width() - notification.width() - 20
                y = 80 + i * (notification.height() + self.spacing)

            # Анимированное перемещение
            from PySide6.QtCore import QPropertyAnimation
            animation = QPropertyAnimation(notification, b"pos")
            animation.setDuration(ANIMATIONS["duration_short"])
            animation.setEndValue(QPoint(x, y))
            animation.start()

    def clear_all(self):
        """Закрытие всех уведомлений"""
        for notification in self.notifications[:]:
            notification.hide_notification()

        self.notifications.clear()

# Система уведомлений создана специально для Юра
