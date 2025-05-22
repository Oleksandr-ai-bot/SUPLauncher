from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, QPoint, QSize, QRect
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QFontMetrics, QPaintEvent

from core.config import COLORS, ANIMATIONS


class AnimatedButton(QPushButton):
    """Кнопка с анимациями и эффектами"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        # Настройка анимации для hover эффекта
        self._hover_animation = QPropertyAnimation(self, b"hover_value")
        self._hover_animation.setDuration(ANIMATIONS["duration_short"])
        self._hover_animation.setEasingCurve(QEasingCurve.OutCubic)

        # Настройка анимации для press эффекта
        self._press_animation = QPropertyAnimation(self, b"press_value")
        self._press_animation.setDuration(ANIMATIONS["duration_short"])
        self._press_animation.setEasingCurve(QEasingCurve.OutCubic)

        # Значения для анимаций
        self._hover_value = 0.0
        self._press_value = 0.0

        # Настройка кнопки
        self.setMinimumHeight(48)
        self.setCursor(Qt.PointingHandCursor)

        # Настройка стилей
        self.setStyleSheet("""
            AnimatedButton {
                border: none;
                background-color: transparent;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)

    def enterEvent(self, event):
        """Курсор наведен на кнопку"""
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_value)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Курсор покинул кнопку"""
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_value)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Кнопка нажата"""
        if event.button() == Qt.LeftButton:
            self._press_animation.stop()
            self._press_animation.setStartValue(self._press_value)
            self._press_animation.setEndValue(1.0)
            self._press_animation.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Кнопка отпущена"""
        if event.button() == Qt.LeftButton:
            self._press_animation.stop()
            self._press_animation.setStartValue(self._press_value)
            self._press_animation.setEndValue(0.0)
            self._press_animation.start()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent):
        """Отрисовка кнопки с эффектами"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Расчет цветов на основе состояний
        if self.isEnabled():
            # Базовый цвет кнопки
            if hasattr(self, 'accent_color') and self.accent_color:
                base_color = QColor(self.accent_color)
            else:
                base_color = QColor(COLORS["bg_secondary"])

            # Расчет цвета для hover
            hover_color = QColor(COLORS["bg_tertiary"])

            # Расчет цвета для нажатия
            press_color = QColor(COLORS["accent_primary"])
            press_color.setAlphaF(0.2)

            # Смешивание цветов на основе значений анимации
            button_color = QColor(base_color)
            if self._hover_value > 0:
                # Интерполяция между базовым и hover цветом
                button_color = self._interpolate_color(base_color, hover_color, self._hover_value)

            # Нарисовать фон кнопки
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(button_color))
            painter.drawRoundedRect(self.rect(), 8, 8)

            # Если кнопка нажата, добавить эффект нажатия
            if self._press_value > 0:
                press_overlay = QColor(press_color)
                press_overlay.setAlphaF(self._press_value * 0.3)  # 30% непрозрачности при полном нажатии
                painter.setBrush(QBrush(press_overlay))
                painter.drawRoundedRect(self.rect(), 8, 8)
        else:
            # Отключенное состояние
            disabled_color = QColor(COLORS["bg_secondary"])
            disabled_color.setAlphaF(0.5)
            painter.setBrush(QBrush(disabled_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect(), 8, 8)

        # Отрисовка текста
        text_color = QColor(COLORS["text_primary"]) if self.isEnabled() else QColor(COLORS["text_disabled"])
        painter.setPen(QPen(text_color))
        painter.setFont(self.font())

        text_rect = self.rect().adjusted(10, 10, -10, -10)
        painter.drawText(text_rect, Qt.AlignCenter, self.text())

    def _interpolate_color(self, color1, color2, factor):
        """Линейная интерполяция между двумя цветами"""
        r = color1.red() + factor * (color2.red() - color1.red())
        g = color1.green() + factor * (color2.green() - color1.green())
        b = color1.blue() + factor * (color2.blue() - color1.blue())
        a = color1.alpha() + factor * (color2.alpha() - color1.alpha())

        result = QColor()
        result.setRed(int(r))
        result.setGreen(int(g))
        result.setBlue(int(b))
        result.setAlpha(int(a))
        return result

    # Свойства для анимации
    def _get_hover_value(self):
        return self._hover_value

    def _set_hover_value(self, value):
        self._hover_value = value
        self.update()

    hover_value = Property(float, _get_hover_value, _set_hover_value)

    def _get_press_value(self):
        return self._press_value

    def _set_press_value(self, value):
        self._press_value = value
        self.update()

    press_value = Property(float, _get_press_value, _set_press_value)

    def set_accent_color(self, color):
        """Установка акцентного цвета кнопки"""
        self.accent_color = color
        self.update()
