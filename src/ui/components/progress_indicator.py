from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QSizePolicy
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QFontMetrics

from core.config import COLORS, ANIMATIONS, FONTS, UI


class ProgressIndicator(QWidget):
    """Улучшенный индикатор прогресса с анимацией и статусом"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Настройка значений
        self._progress = 0
        self._max_progress = 100
        self._status_text = ""
        self._pulsate = False
        self._pulse_position = 0.0

        # Настройка анимации пульсации
        self._pulse_animation = QPropertyAnimation(self, b"pulse_position")
        self._pulse_animation.setDuration(1200)
        self._pulse_animation.setStartValue(0.0)
        self._pulse_animation.setEndValue(1.0)
        self._pulse_animation.setLoopCount(-1)  # Бесконечное повторение
        self._pulse_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Настройка интерфейса
        self._init_ui()

    def _init_ui(self):
        """Инициализация интерфейса"""
        # Основной layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(UI["spacing_small"])

        # Статусный текст
        self.status_label = QLabel(self._status_text)
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['sizes']['small']}px;
        """)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Индикатор прогресса
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, self._max_progress)
        self.progress_bar.setValue(self._progress)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 4px;
                min-height: 8px;
                max-height: 8px;
            }}

            QProgressBar::chunk {{
                background-color: {COLORS['accent_primary']};
                border-radius: 4px;
            }}
        """)

        # Добавление элементов в layout
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.progress_bar)

    def set_progress(self, value: int):
        """Установка значения прогресса"""
        if value != self._progress:
            self._progress = max(0, min(value, self._max_progress))
            self.progress_bar.setValue(self._progress)

            # Если достигли максимума и была пульсация, останавливаем её
            if self._progress >= self._max_progress and self._pulsate:
                self.set_pulsate(False)

            self.update()

    def set_max_progress(self, value: int):
        """Установка максимального значения прогресса"""
        if value != self._max_progress:
            self._max_progress = max(1, value)
            self.progress_bar.setMaximum(self._max_progress)
            self.update()

    def set_status(self, text: str):
        """Установка статусного текста"""
        if text != self._status_text:
            self._status_text = text
            self.status_label.setText(self._status_text)
            self.update()

    def set_pulsate(self, pulsate: bool):
        """Включение/выключение режима пульсации"""
        if pulsate != self._pulsate:
            self._pulsate = pulsate

            if self._pulsate:
                # Включаем режим неопределенного прогресса
                self.progress_bar.setRange(0, 0)
                self._pulse_animation.start()
            else:
                # Возвращаем обычный режим
                self.progress_bar.setRange(0, self._max_progress)
                self.progress_bar.setValue(self._progress)
                self._pulse_animation.stop()

            self.update()

    def reset(self):
        """Сброс индикатора прогресса"""
        self._progress = 0
        self.progress_bar.setValue(0)
        self._status_text = ""
        self.status_label.setText("")
        self.set_pulsate(False)
        self.update()

    def paintEvent(self, event):
        """Дополнительная отрисовка виджета"""
        super().paintEvent(event)

        # Специальная отрисовка в режиме пульсации
        if self._pulsate and self.progress_bar.isVisible():
            painter = QPainter(self.progress_bar)
            painter.setRenderHint(QPainter.Antialiasing)

            # Создаем градиент для анимации пульсации
            rect = self.progress_bar.rect()
            pulse_width = rect.width() * 0.3

            # Расчет позиции пульсации
            pos = rect.width() * self._pulse_position

            # Отрисовка пульсации
            painter.setPen(Qt.NoPen)

            # Градиент от прозрачного к цвету акцента и обратно
            for x in range(int(pos - pulse_width), int(pos + pulse_width)):
                if 0 <= x < rect.width():
                    distance = abs(x - pos) / pulse_width
                    alpha = 1.0 - distance

                    pulse_color = QColor(COLORS["accent_primary"])
                    pulse_color.setAlphaF(alpha * 0.5)

                    painter.fillRect(
                        x, 0, 1, rect.height(),
                        pulse_color
                    )

    # Свойства для анимации
    def _get_pulse_position(self):
        return self._pulse_position

    def _set_pulse_position(self, pos):
        self._pulse_position = pos
        self.update()

    pulse_position = Property(float, _get_pulse_position, _set_pulse_position)
