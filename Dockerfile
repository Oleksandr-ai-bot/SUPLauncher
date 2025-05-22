# Dockerfile
FROM python:3.11-slim

# Метаданные
LABEL maintainer="SUP Team <support@villadesup.ru>"
LABEL description="SUPLAUNCHER - Modern Minecraft Launcher"
LABEL version="1.0.0"

# Переменные окружения
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    # Основные инструменты
    curl \
    wget \
    git \
    # GUI зависимости для PySide6
    libgl1-mesa-glx \
    libglib2.0-0 \
    libfontconfig1 \
    libx11-xcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkb-common-x11-0 \
    # Дополнительные зависимости
    libegl1-mesa \
    libxkbcommon-x11-0 \
    libxcb-cursor0 \
    # Java для Minecraft
    openjdk-17-jre-headless \
    # Инструменты для сборки
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN useradd -m -u 1000 suplauncher && \
    mkdir -p /app && \
    chown -R suplauncher:suplauncher /app

# Переключение на пользователя
USER suplauncher

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY --chown=suplauncher:suplauncher requirements.txt pyproject.toml ./

# Установка Python зависимостей
RUN pip install --user --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY --chown=suplauncher:suplauncher . .

# Установка приложения в режиме разработки
RUN pip install --user -e .

# Создание необходимых директорий
RUN mkdir -p /app/data /app/logs /app/cache

# Переменные окружения для приложения
ENV SUPLAUNCHER_DATA_DIR=/app/data
ENV SUPLAUNCHER_LOG_DIR=/app/logs
ENV SUPLAUNCHER_CACHE_DIR=/app/cache

# Открытие портов (если потребуется веб-интерфейс)
EXPOSE 8080

# Точка входа
ENTRYPOINT ["python", "main.py"]

# Команда по умолчанию
CMD ["--help"]

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# =======================================================
# docker-compose.yml
version: '3.8'

services:
  suplauncher:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: suplauncher
    restart: unless-stopped

    # Переменные окружения
    environment:
      - DISPLAY=${DISPLAY}
      - QT_X11_NO_MITSHM=1
      - SUPLAUNCHER_DATA_DIR=/app/data
      - SUPLAUNCHER_LOG_DIR=/app/logs
      - SUPLAUNCHER_CACHE_DIR=/app/cache

    # Монтирование томов
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./cache:/app/cache
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - ${HOME}/.Xauthority:/home/suplauncher/.Xauthority:rw

    # Сетевые настройки
    network_mode: host

    # Ограничения ресурсов
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 512M
          cpus: '0.5'

    # Зависимости
    depends_on:
      - minecraft-server

    # Политика перезапуска
    restart: unless-stopped

    # Проверка здоровья
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Опциональный Minecraft сервер для тестирования
  minecraft-server:
    image: itzg/minecraft-server:latest
    container_name: minecraft-test-server
    environment:
      EULA: "TRUE"
      TYPE: "FORGE"
      VERSION: "1.20.1"
      MEMORY: "2G"
      DIFFICULTY: "peaceful"
      MOTD: "SUPLAUNCHER Test Server"
      OVERRIDE_SERVER_PROPERTIES: "true"
    ports:
      - "25565:25565"
    volumes:
      - minecraft-data:/data
    restart: unless-stopped

    # Ограничения ресурсов
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'

volumes:
  minecraft-data:
    driver: local

networks:
  default:
    driver: bridge

# =======================================================
# .dockerignore
# Git
.git
.gitignore
.gitattributes

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# User data
data/
cache/
profiles/
minecraft/

# Build artifacts
build/
dist/
*.exe
*.app
*.dmg

# Documentation
docs/_build/

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Docker
Dockerfile*
docker-compose*
.dockerignore

# Other
README.md
LICENSE
*.md
.pre-commit-config.yaml

# Docker конфигурация оптимизирована для развертывания проекта Юра
