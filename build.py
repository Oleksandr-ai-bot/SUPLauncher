#!/usr/bin/env python3
"""
Скрипт для сборки SUPLAUNCHER в исполняемый файл
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def get_platform_info():
    """Получение информации о платформе"""
    system = platform.system().lower()
    architecture = platform.machine().lower()

    if system == "windows":
        return "windows", "exe"
    elif system == "darwin":
        return "macos", "app"
    else:
        return "linux", "bin"


def clean_build():
    """Очистка директорий сборки"""
    print("🧹 Очистка предыдущих сборок...")

    dirs_to_clean = ["build", "dist", "__pycache__"]

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ✓ Удалена директория: {dir_name}")

    # Удаляем .spec файлы
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"   ✓ Удален файл: {spec_file}")


def install_dependencies():
    """Установка зависимостей для сборки"""
    print("📦 Установка зависимостей для сборки...")

    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "pyinstaller", "pillow"
        ], check=True)
        print("   ✓ Зависимости установлены")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Ошибка установки зависимостей: {e}")
        return False

    return True


def create_assets_structure():
    """Создание структуры ресурсов"""
    print("🎨 Подготовка ресурсов...")

    assets_dir = Path("assets")
    if not assets_dir.exists():
        assets_dir.mkdir()
        print("   ✓ Создана директория assets")

    # Создаем поддиректории
    subdirs = ["fonts", "icons", "images", "sounds", "styles"]
    for subdir in subdirs:
        subdir_path = assets_dir / subdir
        if not subdir_path.exists():
            subdir_path.mkdir()
            print(f"   ✓ Создана директория: assets/{subdir}")

    # Создаем файлы-заглушки если они не существуют
    placeholder_files = {
        "icons/app_icon.ico": "placeholder icon",
        "images/logo.png": "placeholder image",
        "fonts/inter.ttf": "placeholder font",
        "styles/main.qss": "/* placeholder styles */"
    }

    for file_path, content in placeholder_files.items():
        full_path = assets_dir / file_path
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            print(f"   ✓ Создан файл-заглушка: assets/{file_path}")


def build_executable():
    """Сборка исполняемого файла"""
    platform_name, extension = get_platform_info()

    print(f"🔨 Сборка для платформы: {platform_name}")

    # Базовые аргументы PyInstaller
    args = [
        sys.executable, "-m", "PyInstaller",
        "--name=SUPLAUNCHER",
        "--windowed",
        "--onedir",  # Создаем директорию вместо одного файла для лучшей производительности
        "--clean",
        "--noconfirm",
        f"--add-data=assets{os.pathsep}assets",
        f"--add-data=src{os.pathsep}src",
    ]

    # Платформо-специфичные настройки
    if platform_name == "windows":
        if os.path.exists("assets/icons/app_icon.ico"):
            args.append("--icon=assets/icons/app_icon.ico")
        args.extend([
            "--console",  # Для отладки, можно убрать для финальной версии
            "--version-file=version.txt"  # Если есть файл версии
        ])

    elif platform_name == "macos":
        if os.path.exists("assets/icons/app_icon.icns"):
            args.append("--icon=assets/icons/app_icon.icns")
        args.extend([
            "--osx-bundle-identifier=ru.villadesup.suplauncher",
        ])

    # Исключения для уменьшения размера
    excludes = [
        "tkinter", "matplotlib", "numpy", "scipy",
        "pandas", "IPython", "jupyter"
    ]

    for exclude in excludes:
        args.extend(["--exclude-module", exclude])

    # Скрытые импорты
    hidden_imports = [
        "PySide6.QtCore",
        "PySide6.QtWidgets",
        "PySide6.QtGui",
        "minecraft_launcher_lib",
        "requests",
        "PIL",
        "rich"
    ]

    for hidden in hidden_imports:
        args.extend(["--hidden-import", hidden])

    # Добавляем main.py
    args.append("main.py")

    print("   Запуск PyInstaller...")
    print(f"   Команда: {' '.join(args)}")

    try:
        subprocess.run(args, check=True)
        print("   ✅ Сборка завершена успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Ошибка сборки: {e}")
        return False


def post_build_cleanup():
    """Очистка после сборки"""
    print("🧹 Финальная очистка...")

    # Удаляем build директорию
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("   ✓ Удалена директория build")

    # Удаляем .spec файл
    spec_files = list(Path(".").glob("*.spec"))
    for spec_file in spec_files:
        spec_file.unlink()
        print(f"   ✓ Удален файл: {spec_file}")


def create_distribution():
    """Создание дистрибутива"""
    print("📦 Создание дистрибутива...")

    platform_name, extension = get_platform_info()
    dist_dir = Path("dist")

    if not dist_dir.exists():
        print("   ❌ Директория dist не найдена")
        return False

    # Находим созданную директорию
    suplauncher_dir = dist_dir / "SUPLAUNCHER"
    if not suplauncher_dir.exists():
        print("   ❌ Собранное приложение не найдено")
        return False

    # Копируем дополнительные файлы
    additional_files = ["README.md", "LICENSE", "requirements.txt"]

    for file_name in additional_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, suplauncher_dir)
            print(f"   ✓ Скопирован файл: {file_name}")

    # Создаем архив
    archive_name = f"SUPLAUNCHER-v1.0.0-{platform_name}"

    if platform_name == "windows":
        # Создаем ZIP архив для Windows
        shutil.make_archive(
            f"dist/{archive_name}",
            "zip",
            "dist",
            "SUPLAUNCHER"
        )
        print(f"   ✅ Создан архив: {archive_name}.zip")

    else:
        # Создаем TAR.GZ архив для Linux/macOS
        shutil.make_archive(
            f"dist/{archive_name}",
            "gztar",
            "dist",
            "SUPLAUNCHER"
        )
        print(f"   ✅ Создан архив: {archive_name}.tar.gz")

    return True


def main():
    """Основная функция сборки"""
    print("🚀 SUPLAUNCHER Build Script")
    print("=" * 50)

    try:
        # Проверяем, что мы в правильной директории
        if not os.path.exists("main.py"):
            print("❌ Не найден файл main.py. Убедитесь, что вы находитесь в корневой директории проекта.")
            return 1

        # Этапы сборки
        steps = [
            ("Очистка", clean_build),
            ("Установка зависимостей", install_dependencies),
            ("Подготовка ресурсов", create_assets_structure),
            ("Сборка исполняемого файла", build_executable),
            ("Создание дистрибутива", create_distribution),
            ("Финальная очистка", post_build_cleanup)
        ]

        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ Ошибка на этапе: {step_name}")
                return 1

        print("\n" + "=" * 50)
        print("🎉 Сборка завершена успешно!")
        print("📁 Результат находится в директории dist/")

        # Показываем размер результата
        dist_dir = Path("dist")
        if dist_dir.exists():
            total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            print(f"📊 Общий размер: {size_mb:.1f} MB")

        return 0

    except KeyboardInterrupt:
        print("\n❌ Сборка прервана пользователем")
        return 1
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Скрипт сборки оптимизирован для Юра
