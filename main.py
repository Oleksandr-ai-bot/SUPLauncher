#!/usr/bin/env python3
"""
SUPLAUNCHER - Современный Minecraft лаунчер
Точка входа в приложение
"""

import sys
import os
import traceback
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
if getattr(sys, 'frozen', False):
    # Если приложение скомпилировано PyInstaller
    application_path = os.path.dirname(sys.executable)
else:
    # Если запускается из исходного кода
    application_path = os.path.dirname(os.path.abspath(__file__))

# Добавляем путь к src директории
src_path = os.path.join(application_path, 'src')
if os.path.exists(src_path):
    sys.path.insert(0, src_path)
else:
    # Если структура директорий отличается, добавляем текущую директорию
    sys.path.insert(0, application_path)

# Проверяем доступность PySide6 перед импортом других модулей
try:
    from PySide6.QtWidgets import QApplication, QMessageBox
    from PySide6.QtCore import Qt, QResource
    from PySide6.QtGui import QFont, QFontDatabase, QIcon
except ImportError as e:
    print(f"Ошибка импорта PySide6: {e}")
    print("Установите PySide6: pip install PySide6")
    sys.exit(1)

# Теперь импортируем модули приложения
try:
    from core.logger import Logger
    from core.paths import Paths
    from core.config import COLORS, APP_NAME, APP_VERSION
    from controllers.app_controller import AppController
    from controllers.profile_controller import ProfileController
    from controllers.minecraft_controller import MinecraftController
    from ui.windows.main_window import MainWindow
except ImportError as e:
    # Если не удается импортировать модули приложения, показываем ошибку
    app = QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Ошибка запуска")
    msg.setText(f"Не удалось загрузить модули приложения: {str(e)}")
    msg.setDetailedText(traceback.format_exc())
    msg.exec_()
    sys.exit(1)


def setup_global_exception_hook():
    """Настройка глобального перехватчика исключений"""
    try:
        logger = Logger().get_logger()
    except:
        # Если логгер не инициализирован, используем print
        def log_error(msg):
            print(f"ERROR: {msg}")

        logger = type('MockLogger', (), {'critical': log_error, 'error': log_error})()

    def exception_hook(exctype, value, tb):
        # Логирование исключения
        logger.critical(f"Необработанное исключение: {exctype.__name__}: {value}")
        logger.critical("Traceback:")
        for line in traceback.format_tb(tb):
            logger.critical(line.strip())

        # Показываем сообщение об ошибке только если есть активное приложение Qt
        if QApplication.instance() is not None:
            try:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Критическая ошибка")
                msg.setText(f"Произошла непредвиденная ошибка: {exctype.__name__}")
                msg.setInformativeText(str(value))
                msg.setDetailedText("".join(traceback.format_tb(tb)))
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
                    QPushButton:pressed {{
                        background-color: {COLORS['accent_primary']};
                    }}
                    QTextEdit {{
                        background-color: {COLORS['bg_secondary']};
                        color: {COLORS['text_primary']};
                        border: 1px solid {COLORS['border_light']};
                    }}
                """)

                msg.exec_()
            except Exception as e:
                print(f"Ошибка показа диалога ошибки: {e}")

        # Вызываем стандартный обработчик исключений
        sys.__excepthook__(exctype, value, tb)

    # Устанавливаем глобальный перехватчик исключений
    sys.excepthook = exception_hook


def load_resources():
    """Загрузка ресурсов (шрифты, стили и т.д.)"""
    try:
        logger = Logger().get_logger()
        paths = Paths()

        # Загрузка шрифтов
        fonts_dir = paths.fonts_dir
        if os.path.exists(fonts_dir):
            font_files = [f for f in os.listdir(fonts_dir) if f.endswith(('.ttf', '.otf'))]
            for font_file in font_files:
                font_path = os.path.join(fonts_dir, font_file)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    logger.info(f"Загружен шрифт: {font_file}")
                else:
                    logger.error(f"Не удалось загрузить шрифт: {font_file}")
        else:
            logger.warning(f"Директория шрифтов не найдена: {fonts_dir}")

        # Загрузка иконки приложения
        try:
            app_icon_path = paths.get_resource_path("icon", "app_icon.ico")
            if os.path.exists(app_icon_path):
                app_icon = QIcon(app_icon_path)
                QApplication.setWindowIcon(app_icon)
                logger.info("Установлена иконка приложения")
            else:
                logger.warning(f"Иконка приложения не найдена: {app_icon_path}")
        except Exception as e:
            logger.error(f"Ошибка загрузки иконки приложения: {str(e)}")

    except Exception as e:
        print(f"Ошибка загрузки ресурсов: {e}")


def apply_global_styles(app: QApplication):
    """Применение глобальных стилей к приложению"""
    try:
        logger = Logger().get_logger()
        paths = Paths()

        # Пытаемся загрузить стили из файла
        styles_to_try = ["main.qss", "dark.qss"]
        style_loaded = False

        for style_file in styles_to_try:
            try:
                style_path = paths.get_resource_path("style", style_file)
                if style_path and os.path.exists(style_path):
                    with open(style_path, 'r', encoding='utf-8') as f:
                        style = f.read()
                    app.setStyleSheet(style)
                    logger.info(f"Применены стили из {style_file}")
                    style_loaded = True
                    break
            except Exception as e:
                logger.warning(f"Не удалось загрузить стили из {style_file}: {str(e)}")

        if not style_loaded:
            logger.warning("Не удалось загрузить внешние стили, применяем стили по умолчанию")

            # Применяем базовые стили напрямую
            app.setStyleSheet(f"""
                QWidget {{
                    background-color: {COLORS['bg_primary']};
                    color: {COLORS['text_primary']};
                    font-family: "Inter", "Segoe UI", sans-serif;
                    font-size: 14px;
                }}

                QPushButton {{
                    background-color: {COLORS['bg_secondary']};
                    border: 1px solid {COLORS['border_light']};
                    border-radius: 8px;
                    padding: 8px 16px;
                    min-height: 32px;
                    font-weight: 600;
                    color: {COLORS['text_primary']};
                }}

                QPushButton:hover {{
                    background-color: {COLORS['bg_tertiary']};
                }}

                QPushButton:pressed {{
                    background-color: {COLORS['accent_primary']};
                }}

                QLineEdit {{
                    background-color: {COLORS['bg_secondary']};
                    border: 1px solid {COLORS['border_light']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: {COLORS['text_primary']};
                }}

                QLineEdit:focus {{
                    border: 2px solid {COLORS['accent_primary']};
                }}

                QComboBox {{
                    background-color: {COLORS['bg_secondary']};
                    border: 1px solid {COLORS['border_light']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: {COLORS['text_primary']};
                }}

                QScrollBar:vertical {{
                    background-color: {COLORS['bg_secondary']};
                    width: 10px;
                    margin: 0px;
                    border-radius: 5px;
                }}

                QScrollBar::handle:vertical {{
                    background-color: {COLORS['bg_tertiary']};
                    border-radius: 5px;
                    min-height: 20px;
                }}

                QScrollBar::handle:vertical:hover {{
                    background-color: {COLORS['text_secondary']};
                }}

                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}

                QToolTip {{
                    background-color: {COLORS['bg_secondary']};
                    color: {COLORS['text_primary']};
                    border: 1px solid {COLORS['border_light']};
                    padding: 4px;
                    border-radius: 4px;
                }}

                QMessageBox {{
                    background-color: {COLORS['bg_primary']};
                    color: {COLORS['text_primary']};
                }}

                QProgressBar {{
                    background-color: {COLORS['bg_secondary']};
                    border: none;
                    border-radius: 4px;
                    text-align: center;
                    min-height: 8px;
                }}

                QProgressBar::chunk {{
                    background-color: {COLORS['accent_primary']};
                    border-radius: 4px;
                }}
            """)
            logger.info("Применены стили по умолчанию")

    except Exception as e:
        print(f"Ошибка применения стилей: {e}")


def check_dependencies():
    """Проверка наличия всех необходимых зависимостей"""
    required_modules = [
        'minecraft_launcher_lib',
        'requests',
        'PIL',  # Pillow
        'rich',
        'yaml',  # PyYAML
        'cryptography',
        'appdirs',
        'dotenv',  # python-dotenv
        'random_username',
        'psutil'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("Отсутствуют необходимые модули:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nУстановите их с помощью:")
        print("pip install -r requirements.txt")
        return False

    return True


def main():
    """Основная функция приложения"""
    # Проверяем зависимости
    if not check_dependencies():
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    # Настройка логирования (делаем это первым)
    try:
        logger = Logger().get_logger()
        logger.info(f"Запуск {APP_NAME} v{APP_VERSION}")
    except Exception as e:
        print(f"Ошибка инициализации логгера: {e}")
        # Продолжаем без логгера
        logger = None

    # Настройка глобального перехватчика исключений
    setup_global_exception_hook()

    # Создание и настройка приложения Qt
    try:
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        app.setApplicationDisplayName(APP_NAME)
        app.setOrganizationName("SUP Team")
        app.setOrganizationDomain("villadesup.ru")

        # Настройки высокого DPI
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

        if logger:
            logger.info("Qt приложение создано")

    except Exception as e:
        print(f"Ошибка создания Qt приложения: {e}")
        sys.exit(1)

    # Загрузка ресурсов
    try:
        load_resources()
    except Exception as e:
        if logger:
            logger.error(f"Ошибка загрузки ресурсов: {str(e)}")
        else:
            print(f"Ошибка загрузки ресурсов: {e}")

    # Применение глобальных стилей
    try:
        apply_global_styles(app)
    except Exception as e:
        if logger:
            logger.error(f"Ошибка применения стилей: {str(e)}")
        else:
            print(f"Ошибка применения стилей: {e}")

    # Создание контроллеров
    try:
        if logger:
            logger.info("Создание контроллеров...")

        app_controller = AppController(app)
        profile_controller = ProfileController()
        minecraft_controller = MinecraftController()

        if logger:
            logger.info("Контроллеры созданы")

    except Exception as e:
        error_msg = f"Ошибка создания контроллеров: {str(e)}"
        if logger:
            logger.critical(error_msg)
        else:
            print(error_msg)

        # Показываем ошибку пользователю
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Ошибка инициализации")
        msg.setText("Не удалось инициализировать контроллеры приложения")
        msg.setDetailedText(str(e))
        msg.exec_()
        sys.exit(1)

    # Создание главного окна
    try:
        if logger:
            logger.info("Создание главного окна...")

        main_window = MainWindow()
        main_window.set_controllers(app_controller, profile_controller, minecraft_controller)

        if logger:
            logger.info("Главное окно создано")

    except Exception as e:
        error_msg = f"Ошибка создания главного окна: {str(e)}"
        if logger:
            logger.critical(error_msg)
        else:
            print(error_msg)

        # Показываем ошибку пользователю
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Ошибка создания окна")
        msg.setText("Не удалось создать главное окно приложения")
        msg.setDetailedText(str(e))
        msg.exec_()
        sys.exit(1)

    # Инициализация приложения
    try:
        if logger:
            logger.info("Инициализация приложения...")

        app_controller.initialize()

        if logger:
            logger.info("Приложение инициализировано")

    except Exception as e:
        error_msg = f"Ошибка инициализации приложения: {str(e)}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)

        # Не прерываем выполнение, так как основное окно уже создано

    # Отображение главного окна
    try:
        if logger:
            logger.info("Отображение главного окна...")

        main_window.show()

        if logger:
            logger.info("Главное окно отображено")

    except Exception as e:
        error_msg = f"Ошибка отображения главного окна: {str(e)}"
        if logger:
            logger.critical(error_msg)
        else:
            print(error_msg)
        sys.exit(1)

    # Запуск цикла обработки событий
    try:
        if logger:
            logger.info("Запуск основного цикла приложения")

        exit_code = app.exec()

        if logger:
            logger.info(f"Завершение работы с кодом: {exit_code}")
        else:
            print(f"Завершение работы с кодом: {exit_code}")

        sys.exit(exit_code)

    except Exception as e:
        error_msg = f"Ошибка в основном цикле приложения: {str(e)}"
        if logger:
            logger.critical(error_msg)
        else:
            print(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Проект создан для Юра
