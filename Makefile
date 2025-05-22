# SUPLAUNCHER Makefile
# Автоматизация часто используемых команд разработки

# Переменные
PYTHON = python3
PIP = pip3
VENV_DIR = venv
SRC_DIR = src
TEST_DIR = tests
DIST_DIR = dist
BUILD_DIR = build

# Цвета для вывода
COLOR_RESET = \033[0m
COLOR_GREEN = \033[32m
COLOR_YELLOW = \033[33m
COLOR_RED = \033[31m
COLOR_BLUE = \033[34m

# Помощь
.PHONY: help
help:
	@echo "$(COLOR_BLUE)SUPLAUNCHER Development Commands$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_GREEN)Setup:$(COLOR_RESET)"
	@echo "  setup          - Полная настройка среды разработки"
	@echo "  install        - Установка зависимостей"
	@echo "  install-dev    - Установка зависимостей для разработки"
	@echo ""
	@echo "$(COLOR_GREEN)Development:$(COLOR_RESET)"
	@echo "  run            - Запуск приложения"
	@echo "  format         - Форматирование кода (black + isort)"
	@echo "  lint           - Проверка кода (flake8 + mypy)"
	@echo "  test           - Запуск тестов"
	@echo "  test-cov       - Запуск тестов с покрытием"
	@echo ""
	@echo "$(COLOR_GREEN)Build:$(COLOR_RESET)"
	@echo "  build          - Сборка исполняемого файла"
	@echo "  build-all      - Сборка для всех платформ"
	@echo "  package        - Создание пакета для распространения"
	@echo ""
	@echo "$(COLOR_GREEN)Maintenance:$(COLOR_RESET)"
	@echo "  clean          - Очистка временных файлов"
	@echo "  clean-all      - Полная очистка"
	@echo "  update         - Обновление зависимостей"

# Настройка среды разработки
.PHONY: setup
setup: clean install-dev
	@echo "$(COLOR_GREEN)✓ Среда разработки настроена$(COLOR_RESET)"

# Установка зависимостей
.PHONY: install
install:
	@echo "$(COLOR_YELLOW)Установка зависимостей...$(COLOR_RESET)"
	$(PIP) install -r requirements.txt
	@echo "$(COLOR_GREEN)✓ Зависимости установлены$(COLOR_RESET)"

.PHONY: install-dev
install-dev: install
	@echo "$(COLOR_YELLOW)Установка зависимостей для разработки...$(COLOR_RESET)"
	$(PIP) install -e ".[dev,test,build]"
	@echo "$(COLOR_GREEN)✓ Зависимости для разработки установлены$(COLOR_RESET)"

# Запуск приложения
.PHONY: run
run:
	@echo "$(COLOR_YELLOW)Запуск SUPLAUNCHER...$(COLOR_RESET)"
	$(PYTHON) main.py

# Форматирование кода
.PHONY: format
format:
	@echo "$(COLOR_YELLOW)Форматирование кода...$(COLOR_RESET)"
	black $(SRC_DIR) main.py
	isort $(SRC_DIR) main.py
	@echo "$(COLOR_GREEN)✓ Код отформатирован$(COLOR_RESET)"

# Проверка кода
.PHONY: lint
lint:
	@echo "$(COLOR_YELLOW)Проверка кода...$(COLOR_RESET)"
	flake8 $(SRC_DIR) main.py
	mypy $(SRC_DIR) main.py
	@echo "$(COLOR_GREEN)✓ Проверка кода завершена$(COLOR_RESET)"

# Тестирование
.PHONY: test
test:
	@echo "$(COLOR_YELLOW)Запуск тестов...$(COLOR_RESET)"
	pytest $(TEST_DIR) -v
	@echo "$(COLOR_GREEN)✓ Тесты выполнены$(COLOR_RESET)"

.PHONY: test-cov
test-cov:
	@echo "$(COLOR_YELLOW)Запуск тестов с покрытием...$(COLOR_RESET)"
	pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing
	@echo "$(COLOR_GREEN)✓ Тесты с покрытием выполнены$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)Отчет о покрытии: htmlcov/index.html$(COLOR_RESET)"

# Сборка
.PHONY: build
build: clean
	@echo "$(COLOR_YELLOW)Сборка приложения...$(COLOR_RESET)"
	$(PYTHON) build.py
	@echo "$(COLOR_GREEN)✓ Сборка завершена$(COLOR_RESET)"

.PHONY: build-windows
build-windows: clean
	@echo "$(COLOR_YELLOW)Сборка для Windows...$(COLOR_RESET)"
	pyinstaller --name=SUPLAUNCHER \
		--windowed \
		--onedir \
		--icon=assets/icons/app_icon.ico \
		--add-data="assets;assets" \
		--add-data="src;src" \
		--clean \
		--noconfirm \
		main.py
	@echo "$(COLOR_GREEN)✓ Сборка для Windows завершена$(COLOR_RESET)"

.PHONY: build-linux
build-linux: clean
	@echo "$(COLOR_YELLOW)Сборка для Linux...$(COLOR_RESET)"
	pyinstaller --name=SUPLAUNCHER \
		--windowed \
		--onedir \
		--add-data="assets:assets" \
		--add-data="src:src" \
		--clean \
		--noconfirm \
		main.py
	@echo "$(COLOR_GREEN)✓ Сборка для Linux завершена$(COLOR_RESET)"

.PHONY: build-macos
build-macos: clean
	@echo "$(COLOR_YELLOW)Сборка для macOS...$(COLOR_RESET)"
	pyinstaller --name=SUPLAUNCHER \
		--windowed \
		--onedir \
		--icon=assets/icons/app_icon.icns \
		--add-data="assets:assets" \
		--add-data="src:src" \
		--osx-bundle-identifier=ru.villadesup.suplauncher \
		--clean \
		--noconfirm \
		main.py
	@echo "$(COLOR_GREEN)✓ Сборка для macOS завершена$(COLOR_RESET)"

.PHONY: build-all
build-all:
	@echo "$(COLOR_YELLOW)Сборка для всех платформ...$(COLOR_RESET)"
	@echo "$(COLOR_RED)Внимание: Запустите эту команду на каждой целевой платформе$(COLOR_RESET)"
	make build-windows
	make build-linux
	make build-macos

# Создание пакета
.PHONY: package
package: clean
	@echo "$(COLOR_YELLOW)Создание пакета...$(COLOR_RESET)"
	$(PYTHON) -m build
	@echo "$(COLOR_GREEN)✓ Пакет создан в $(DIST_DIR)/$(COLOR_RESET)"

# Очистка
.PHONY: clean
clean:
	@echo "$(COLOR_YELLOW)Очистка временных файлов...$(COLOR_RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf $(BUILD_DIR)
	rm -rf $(DIST_DIR)
	rm -rf *.spec
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	@echo "$(COLOR_GREEN)✓ Временные файлы удалены$(COLOR_RESET)"

.PHONY: clean-all
clean-all: clean
	@echo "$(COLOR_YELLOW)Полная очистка...$(COLOR_RESET)"
	rm -rf $(VENV_DIR)
	rm -rf *.egg-info
	rm -rf .tox
	@echo "$(COLOR_GREEN)✓ Полная очистка выполнена$(COLOR_RESET)"

# Обновление зависимостей
.PHONY: update
update:
	@echo "$(COLOR_YELLOW)Обновление зависимостей...$(COLOR_RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	@echo "$(COLOR_GREEN)✓ Зависимости обновлены$(COLOR_RESET)"

# Создание виртуального окружения
.PHONY: venv
venv:
	@echo "$(COLOR_YELLOW)Создание виртуального окружения...$(COLOR_RESET)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(COLOR_GREEN)✓ Виртуальное окружение создано$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)Активируйте его командой:$(COLOR_RESET)"
	@echo "  source $(VENV_DIR)/bin/activate  # Linux/macOS"
	@echo "  $(VENV_DIR)\\Scripts\\activate     # Windows"

# Проверка стиля кода
.PHONY: check
check: format lint test
	@echo "$(COLOR_GREEN)✓ Все проверки пройдены$(COLOR_RESET)"

# Подготовка к релизу
.PHONY: release-check
release-check: check test-cov
	@echo "$(COLOR_YELLOW)Проверка готовности к релизу...$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)✓ Готово к релизу$(COLOR_RESET)"

# Локальная установка для разработки
.PHONY: develop
develop:
	@echo "$(COLOR_YELLOW)Установка в режиме разработки...$(COLOR_RESET)"
	$(PIP) install -e .
	@echo "$(COLOR_GREEN)✓ Установлено в режиме разработки$(COLOR_RESET)"

# Создание документации
.PHONY: docs
docs:
	@echo "$(COLOR_YELLOW)Генерация документации...$(COLOR_RESET)"
	@echo "$(COLOR_RED)Документация будет добавлена в следующих версиях$(COLOR_RESET)"

# Статистика проекта
.PHONY: stats
stats:
	@echo "$(COLOR_BLUE)Статистика проекта:$(COLOR_RESET)"
	@echo "Строки кода Python:"
	@find $(SRC_DIR) -name "*.py" -exec wc -l {} + | tail -1
	@echo "Файлы Python:"
	@find $(SRC_DIR) -name "*.py" | wc -l
	@echo "Размер проекта:"
	@du -sh . 2>/dev/null || echo "Размер недоступен"

# Проверка безопасности
.PHONY: security
security:
	@echo "$(COLOR_YELLOW)Проверка безопасности...$(COLOR_RESET)"
	@if command -v bandit >/dev/null 2>&1; then \
		bandit -r $(SRC_DIR); \
	else \
		echo "$(COLOR_RED)bandit не установлен. Установите: pip install bandit$(COLOR_RESET)"; \
	fi

# Быстрый старт для новых разработчиков
.PHONY: quickstart
quickstart: venv
	@echo "$(COLOR_BLUE)Быстрый старт для разработки:$(COLOR_RESET)"
	@echo "1. Активируйте виртуальное окружение"
	@echo "2. Запустите: make setup"
	@echo "3. Запустите: make run"

# По умолчанию показываем help
.DEFAULT_GOAL := help

# Makefile создан для автоматизации разработки проекта Юра
