from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QScrollArea, QFrame, QSizePolicy, QMessageBox,
                               QSpacerItem, QGridLayout, QPushButton)
from PySide6.QtGui import QIcon, QFont, QPainter, QColor, QBrush, QPen

from core.config import COLORS, UI, FONTS
from core.paths import Paths
from models.profile import Profile
from ui.components.profile_card import ProfileCard
from ui.components.animated_button import AnimatedButton


class ProfilesView(QWidget):
    """Представление для управления профилями"""

    # Сигналы
    profileSelected = Signal(str)  # ID выбранного профиля
    profileDeleted = Signal(str)  # ID удаленного профиля
    profileUpdated = Signal(str, str, str, str, int, bool)  # Обновление профиля
    playProfile = Signal(str)  # Запуск профиля

    def __init__(self, parent=None):
        super().__init__(parent)
        self.paths = Paths()

        # Данные
        self.profiles = {}
        self.profile_cards = {}
        self.selected_profile_id = None

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
        self.header_container = QWidget()
        self.header_layout = QHBoxLayout(self.header_container)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(UI["spacing_medium"])

        # Заголовок текст
        self.title_label = QLabel("Управление Профилями")
        self.title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-family: "{FONTS['secondary']}";
            font-size: {FONTS['sizes']['header']}px;
            font-weight: bold;
        """)

        # Кнопка создания профиля (заглушка)
        self.create_button = AnimatedButton("Создать профиль")
        self.create_button.setMinimumHeight(UI["button_height"])
        self.create_button.setMinimumWidth(160)
        self.create_button.clicked.connect(self._show_create_disabled_message)
        self.create_button.setEnabled(False)  # Заблокировано как заглушка

        # Добавление элементов в заголовок
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch(1)
        self.header_layout.addWidget(self.create_button)

        # Контейнер для профилей
        self.profiles_container = QWidget()
        self.profiles_container.setStyleSheet(f"""
            background-color: {COLORS['bg_secondary']};
            border-radius: {UI['border_radius']}px;
        """)

        # Scroll area для профилей
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

        # Виджет для содержимого scroll area
        self.scroll_widget = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(UI["padding_medium"], UI["padding_medium"],
                                              UI["padding_medium"], UI["padding_medium"])
        self.scroll_layout.setSpacing(UI["spacing_medium"])
        self.scroll_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Устанавливаем виджет в scroll area
        self.scroll_area.setWidget(self.scroll_widget)

        # Сообщение об отсутствии профилей
        self.no_profiles_label = QLabel("Профили не найдены")
        self.no_profiles_label.setAlignment(Qt.AlignCenter)
        self.no_profiles_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: {FONTS['sizes']['large']}px;
            font-style: italic;
            padding: {UI['padding_large']}px;
        """)
        self.no_profiles_label.setVisible(False)

        # Layout для контейнера профилей
        self.profiles_layout = QVBoxLayout(self.profiles_container)
        self.profiles_layout.setContentsMargins(0, 0, 0, 0)
        self.profiles_layout.setSpacing(0)
        self.profiles_layout.addWidget(self.scroll_area)
        self.profiles_layout.addWidget(self.no_profiles_label)

        # Добавление всех элементов в основной layout
        self.layout.addWidget(self.header_container)
        self.layout.addWidget(self.profiles_container, 1)

    def update_profiles(self, profiles: dict):
        """Обновление списка профилей"""
        self.profiles = profiles

        # Очищаем существующие карточки
        self._clear_profile_cards()

        if not profiles:
            # Показываем сообщение об отсутствии профилей
            self.no_profiles_label.setVisible(True)
            self.scroll_area.setVisible(False)
            return

        # Скрываем сообщение и показываем профили
        self.no_profiles_label.setVisible(False)
        self.scroll_area.setVisible(True)

        # Создаем карточки профилей
        row = 0
        col = 0
        max_cols = max(1, (self.scroll_widget.width() - UI["padding_medium"] * 2) // (
                    UI["card_width"] + UI["spacing_medium"]))

        for profile_id, profile in profiles.items():
            # Создаем карточку профиля
            card = ProfileCard(profile)

            # Подключаем сигналы
            card.selected.connect(self._on_profile_selected)
            card.play.connect(self._on_play_profile)
            card.edit.connect(self._on_edit_profile)
            card.delete.connect(self._on_delete_profile)

            # Сохраняем ссылку на карточку
            self.profile_cards[profile_id] = card

            # Добавляем карточку в layout
            self.scroll_layout.addWidget(card, row, col)

            # Обновляем позицию
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Обновляем выделение
        if self.selected_profile_id in self.profile_cards:
            self.profile_cards[self.selected_profile_id].set_selected(True)

    def set_selected_profile(self, profile_id: str):
        """Установка выбранного профиля"""
        # Снимаем выделение с предыдущего профиля
        if self.selected_profile_id and self.selected_profile_id in self.profile_cards:
            self.profile_cards[self.selected_profile_id].set_selected(False)

        # Устанавливаем новое выделение
        self.selected_profile_id = profile_id
        if profile_id in self.profile_cards:
            self.profile_cards[profile_id].set_selected(True)

    def _clear_profile_cards(self):
        """Очистка существующих карточек профилей"""
        for card in self.profile_cards.values():
            card.setParent(None)
            card.deleteLater()

        self.profile_cards.clear()

    def _on_profile_selected(self, profile_id: str):
        """Обработка выбора профиля"""
        self.set_selected_profile(profile_id)
        self.profileSelected.emit(profile_id)

    def _on_play_profile(self, profile_id: str):
        """Обработка запуска профиля"""
        self.playProfile.emit(profile_id)

    def _on_edit_profile(self, profile_id: str):
        """Обработка редактирования профиля (заглушка)"""
        # Показываем сообщение о том, что функция в разработке
        msg = QMessageBox(self)
        msg.setWindowTitle("Функция в разработке")
        msg.setText("Редактирование профилей будет добавлено в следующих версиях.")
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

    def _on_delete_profile(self, profile_id: str):
        """Обработка удаления профиля"""
        if profile_id not in self.profiles:
            return

        profile = self.profiles[profile_id]

        # Показываем диалог подтверждения
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение удаления")
        msg.setText(f"Вы уверены, что хотите удалить профиль '{profile.name}'?")
        msg.setInformativeText("Это действие нельзя отменить.")
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
            self.profileDeleted.emit(profile_id)

    def _show_create_disabled_message(self):
        """Показ сообщения о заблокированной функции создания"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Функция в разработке")
        msg.setText("Создание новых профилей будет добавлено в следующих версиях.")
        msg.setInformativeText("Пока вы можете использовать предустановленный профиль SUPMINE.")
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

    def resizeEvent(self, event):
        """Обработка изменения размера для пересчета сетки профилей"""
        super().resizeEvent(event)

        # Пересчитываем расположение карточек при изменении размера
        if self.profiles:
            # Небольшая задержка для корректного пересчета
            from PySide6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self.update_profiles(self.profiles))

# Представление профилей разработано для Юра
