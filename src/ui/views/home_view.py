from PySide6.QtCore import Qt, Signal, QSize, QRect, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QPushButton, QSpacerItem, QSizePolicy,
                               QFrame, QScrollArea)
from PySide6.QtGui import QPixmap, QIcon, QFont, QPainter, QColor, QBrush, QPen

from core.config import COLORS, UI, FONTS, ANIMATIONS
from core.paths import Paths
from models.profile import Profile
from ui.components.animated_button import AnimatedButton
from ui.components.progress_indicator import ProgressIndicator


class HomeView(QWidget):
    """Главный экран лаунчера"""

    # Сигналы
    playClicked = Signal(str)  # Сигнал запуска игры (с ID профиля)
    profileSelectionChanged = Signal(str)  # Сигнал изменения выбранного профиля

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paths = Paths()

        # Состояние
        self.selected_profile_id = None
        self.profiles = {}
        self.is_launching = False

        # Инициализация UI
        self._init_ui()

    def _init_ui(self):
        """Инициализация интерфейса главного экрана"""
        # Основной layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(UI["padding_large"], UI["padding_large"],
                                       UI["padding_large"], UI["padding_large"])
        self.layout.setSpacing(UI["spacing_large"])

        # Верхняя секция: логотип и заголовок
        self.header_container = QWidget()
        self.header_layout = QVBoxLayout(self.header_container)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(UI["spacing_medium"])
        self.header_layout.setAlignment(Qt.AlignCenter)

        # Логотип
        self.logo_label = QLabel()
        logo_path = self.paths.get_resource_path("image", "logo.png")
        pixmap = QPixmap(logo_path)

        # Масштабирование логотипа для корректного отображения
        max_width = 400
        if pixmap.width() > max_width:
            pixmap = pixmap.scaledToWidth(max_width, Qt.SmoothTransformation)

        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)

        # Заголовок (опционально, если логотип не содержит текст)
        self.title_label = QLabel("SUPLAUNCHER")
        self.title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-family: "{FONTS['secondary']}";
            font-size: {FONTS['sizes']['header']}px;
            font-weight: bold;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)

        # Добавление элементов в заголовок
        self.header_layout.addWidget(self.logo_label)
        # self.header_layout.addWidget(self.title_label)  # Раскомментировать, если нужен отдельный заголовок

        # Средняя секция: выбор профиля и кнопка запуска
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(UI["spacing_medium"])

        # Контейнер для выбора профиля
        self.profile_selection_container = QWidget()
        self.profile_selection_layout = QHBoxLayout(self.profile_selection_container)
        self.profile_selection_layout.setContentsMargins(0, 0, 0, 0)
        self.profile_selection_layout.setSpacing(UI["spacing_medium"])

        # Выбор профиля
        self.profile_label = QLabel("Профиль:")
        self.profile_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: {FONTS['sizes']['large']}px;
            font-weight: bold;
        """)

        self.profile_combobox = QComboBox()
        self.profile_combobox.setMinimumWidth(300)
        self.profile_combobox.setMinimumHeight(38)
        self.profile_combobox.currentIndexChanged.connect(self._on_profile_selection_changed)

        # Добавление элементов в контейнер выбора профиля
        self.profile_selection_layout.addWidget(self.profile_label)
        self.profile_selection_layout.addWidget(self.profile_combobox, 1)

        # Кнопка запуска
        self.play_button = AnimatedButton("ИГРАТЬ")
        self.play_button.set_accent_color(COLORS["accent_primary"])
        self.play_button.setMinimumHeight(UI["button_height"] * 1.5)
        self.play_button.setMinimumWidth(300)
        self.play_button.setFont(QFont(FONTS["accent"], FONTS["sizes"]["xl"], QFont.Bold))
        self.play_button.clicked.connect(self._on_play_clicked)

        # Добавление элементов в среднюю секцию
        self.main_layout.addWidget(self.profile_selection_container)
        self.main_layout.addWidget(self.play_button, 0, Qt.AlignCenter)

        # Нижняя секция: индикатор прогресса и статус
        self.footer_container = QWidget()
        self.footer_layout = QVBoxLayout(self.footer_container)
        self.footer_layout.setContentsMargins(0, 0, 0, 0)
        self.footer_layout.setSpacing(UI["spacing_small"])

        # Индикатор прогресса
        self.progress_indicator = ProgressIndicator()
        self.progress_indicator.setVisible(False)

        # Статусная строка
        self.status_container = QWidget()
        self.status_layout = QHBoxLayout(self.status_container)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_layout.setSpacing(UI["spacing_small"])

        self.status_label = QLabel("Готов к запуску")
        self.status_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['sizes']['small']}px;
        """)

        # Ссылка на веб-сайт
        self.website_link = QLabel('<a href="https://villadesup.ru" style="color: ' +
                                   COLORS['accent_primary'] + ';">VillaDeSUP.ru</a>')
        self.website_link.setOpenExternalLinks(True)
        self.website_link.setStyleSheet(f"""
            font-size: {FONTS['sizes']['small']}px;
        """)

        # Добавление элементов в статусную строку
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addStretch(1)
        self.status_layout.addWidget(self.website_link)

        # Добавление элементов в нижнюю секцию
        self.footer_layout.addWidget(self.progress_indicator)
        self.footer_layout.addWidget(self.status_container)

        # Добавление всех секций в основной layout
        self.layout.addWidget(self.header_container)
        self.layout.addStretch(1)
        self.layout.addWidget(self.main_container)
        self.layout.addStretch(1)
        self.layout.addWidget(self.footer_container)

    def update_profiles(self, profiles: dict):
        """Обновление списка профилей"""
        self.profiles = profiles

        # Запоминаем текущий выбранный профиль
        current_profile_id = self.selected_profile_id

        # Обновляем combobox
        self.profile_combobox.clear()

        if not profiles:
            self.profile_combobox.addItem("Нет доступных профилей")
            self.play_button.setEnabled(False)
            self.selected_profile_id = None
            return

        # Заполняем combobox и восстанавливаем выбор
        selected_index = 0
        for i, (profile_id, profile) in enumerate(profiles.items()):
            self.profile_combobox.addItem(profile.name, profile_id)

            if profile_id == current_profile_id:
                selected_index = i

        # Если был выбран профиль, восстанавливаем выбор
        if current_profile_id in profiles:
            self.profile_combobox.setCurrentIndex(selected_index)
        else:
            # Иначе выбираем первый профиль
            self.profile_combobox.setCurrentIndex(0)
            self._on_profile_selection_changed(0)

        self.play_button.setEnabled(True)

    def set_launching_state(self, is_launching: bool):
        """Устанавливает состояние запуска игры"""
        self.is_launching = is_launching

        # Обновляем UI в зависимости от состояния
        self.play_button.setEnabled(not is_launching)
        self.profile_combobox.setEnabled(not is_launching)
        self.progress_indicator.setVisible(is_launching)

        if is_launching:
            self.status_label.setText("Подготовка к запуску...")
            self.progress_indicator.set_status("Инициализация...")
            self.progress_indicator.set_pulsate(True)
        else:
            self.status_label.setText("Готов к запуску")
            self.progress_indicator.reset()

    def update_progress(self, current: int, maximum: int, status: str):
        """Обновляет индикатор прогресса"""
        if self.is_launching:
            self.progress_indicator.set_pulsate(False)
            self.progress_indicator.set_max_progress(maximum)
            self.progress_indicator.set_progress(current)
            self.progress_indicator.set_status(status)
            self.status_label.setText(f"Запуск: {status}")

    def _on_profile_selection_changed(self, index: int):
        """Обработчик изменения выбранного профиля"""
        if index >= 0 and self.profile_combobox.count() > 0:
            self.selected_profile_id = self.profile_combobox.itemData(index)
            if self.selected_profile_id:
                self.profileSelectionChanged.emit(self.selected_profile_id)

    def _on_play_clicked(self):
        """Обработчик нажатия кнопки запуска"""
        if self.selected_profile_id and not self.is_launching:
            self.playClicked.emit(self.selected_profile_id)

    def paintEvent(self, event):
        """Отрисовка фоновых эффектов"""
        super().paintEvent(event)

        # Отрисовка фонового паттерна
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Создаем полупрозрачный градиент для фона
        bg_color1 = QColor(COLORS["bg_primary"])
        bg_color2 = QColor(COLORS["bg_primary"])
        bg_color2.setAlpha(150)

        # Отрисовка тонкой линии-разделителя под заголовком
        pen = QPen(QColor(COLORS["border_light"]))
        pen.setWidth(1)
        painter.setPen(pen)

        header_bottom = self.header_container.mapTo(self,
                                                    QPoint(0, self.header_container.height())).y() + UI[
                            "spacing_medium"]

        painter.drawLine(UI["padding_large"], header_bottom,
                         self.width() - UI["padding_large"], header_bottom)
