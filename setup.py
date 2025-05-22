#!/usr/bin/env python3
"""
Setup script для SUPLAUNCHER
"""

from setuptools import setup, find_packages
import os
import sys
from pathlib import Path

# Читаем версию из config.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
try:
    from core.config import APP_VERSION, APP_NAME
except ImportError:
    APP_NAME = "SUPLAUNCHER"
    APP_VERSION = "1.0.0"

# Читаем описание из README
README_PATH = Path(__file__).parent / "README.md"
if README_PATH.exists():
    with open(README_PATH, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Современный Minecraft лаунчер с минималистичным дизайном"

# Читаем зависимости из requirements.txt
REQUIREMENTS_PATH = Path(__file__).parent / "requirements.txt"
requirements = []
if REQUIREMENTS_PATH.exists():
    with open(REQUIREMENTS_PATH, "r", encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f.readlines()
            if line.strip() and not line.startswith("#")
        ]

# Дополнительные зависимости для разработки
dev_requirements = [
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.5.0",
    "pytest>=7.4.0",
    "pytest-qt>=4.2.0",
    "pre-commit>=3.0.0",
    "flake8>=6.0.0",
    "coverage>=7.0.0"
]

# Зависимости для сборки
build_requirements = [
    "pyinstaller>=5.13.0",
    "pillow>=10.0.0",
    "wheel>=0.41.0"
]

setup(
    name=APP_NAME.lower(),
    version=APP_VERSION,
    author="SUP Team",
    author_email="support@villadesup.ru",
    description="Современный Minecraft лаунчер с минималистичным дизайном",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/suplauncher",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/suplauncher/issues",
        "Source": "https://github.com/yourusername/suplauncher",
        "Documentation": "https://github.com/yourusername/suplauncher/wiki",
        "Official Site": "https://villadesup.ru"
    },

    packages=find_packages(where="src"),
    package_dir={"": "src"},

    # Включаем дополнительные файлы
    include_package_data=True,
    package_data={
        "": [
            "assets/**/*",
            "*.qss",
            "*.json",
            "*.txt",
            "*.md"
        ]
    },

    # Точка входа
    entry_points={
        "console_scripts": [
            "suplauncher=main:main",
        ],
        "gui_scripts": [
            "suplauncher-gui=main:main",
        ]
    },

    # Зависимости
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "build": build_requirements,
        "all": dev_requirements + build_requirements
    },

    # Метаданные
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Natural Language :: Russian",
        "Natural Language :: English"
    ],

    # Требования к Python
    python_requires=">=3.9",

    # Ключевые слова
    keywords="minecraft launcher gaming mods forge fabric",

    # Zip безопасность
    zip_safe=False,

    # Платформы
    platforms=["Windows", "macOS", "Linux"],

    # Лицензия
    license="MIT",

    # Дополнительные настройки
    options={
        "build_exe": {
            "packages": [
                "PySide6",
                "minecraft_launcher_lib",
                "requests",
                "PIL",
                "rich",
                "cryptography",
                "appdirs",
                "psutil"
            ],
            "include_files": [
                ("assets/", "assets/"),
                ("README.md", "README.md"),
                ("LICENSE", "LICENSE")
            ],
            "excludes": [
                "tkinter",
                "matplotlib",
                "numpy",
                "scipy",
                "pandas",
                "IPython",
                "jupyter"
            ]
        }
    }
)

