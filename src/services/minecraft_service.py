from PySide6.QtCore import QThread, Signal, QMutex, QWaitCondition
from typing import Dict, Optional, Any, Callable

import os
import subprocess
import uuid
import minecraft_launcher_lib as mll

from core.logger import Logger
from core.paths import Paths
from models.profile import Profile
from services.auth_service import AuthService


class MinecraftLaunchThread(QThread):
    """Поток для асинхронного запуска Minecraft"""

    # Сигналы
    progressUpdated = Signal(int, int, str)  # текущее, максимум, статус
    launchFinished = Signal(bool)  # успешно ли

    def __init__(self, profile: Profile):
        super().__init__()
        self.logger = Logger().get_logger()
        self.paths = Paths()
        self.auth_service = AuthService()

        self.profile = profile
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.abort = False

        # Параметры для отслеживания прогресса
        self.current_progress = 0
        self.max_progress = 100
        self.current_status = ""

    def run(self):
        """Основной метод потока"""
        self.logger.info(f"Запуск Minecraft для профиля: {self.profile.name}")

        try:
            # Установка всех необходимых файлов
            self._install_minecraft()

            # Проверка на отмену
            if self.abort:
                self.logger.info("Запуск отменен")
                self.launchFinished.emit(False)
                return

            # Запуск Minecraft
            self._launch_minecraft()

            # Считаем запуск успешным
            self.launchFinished.emit(True)
        except Exception as e:
            self.logger.error(f"Ошибка запуска Minecraft: {str(e)}")
            self.launchFinished.emit(False)

    def stop(self):
        """Остановка потока"""
        self.mutex.lock()
        self.abort = True
        self.condition.wakeAll()
        self.mutex.unlock()

    def _emit_progress(self, current: int, maximum: int, status: str):
        """Безопасная отправка сигнала прогресса"""
        if not self.abort:
            self.current_progress = current
            self.max_progress = maximum
            self.current_status = status
            self.progressUpdated.emit(current, maximum, status)

    def _install_minecraft(self):
        """Установка всех необходимых файлов Minecraft"""
        self.logger.info(f"Установка версии: {self.profile.version_id}")

        # Обновляем статус
        self._emit_progress(0, 100, f"Подготовка установки {self.profile.version_id}...")

        try:
            # Создаем директорию для игры, если она не существует
            game_dir = self.profile.game_directory or self.paths.minecraft_dir
            os.makedirs(game_dir, exist_ok=True)

            # Callback для обновления прогресса
            def status_callback(status: str):
                """Обработка изменения статуса"""
                if not self.abort:
                    self._emit_progress(self.current_progress, self.max_progress, status)

            def progress_callback(progress: int):
                """Обработка изменения прогресса"""
                if not self.abort:
                    self._emit_progress(progress, self.max_progress, self.current_status)

            def max_callback(maximum: int):
                """Обработка изменения максимального значения прогресса"""
                if not self.abort:
                    self._emit_progress(self.current_progress, maximum, self.current_status)

            # Определяем тип установки на основе профиля
            if self.profile.loader_type == "forge":
                # Установка Forge
                self._install_forge(game_dir, status_callback, progress_callback, max_callback)
            elif self.profile.loader_type == "fabric":
                # Установка Fabric
                self._install_fabric(game_dir, status_callback, progress_callback, max_callback)
            else:
                # Обычная установка Vanilla
                self._install_vanilla(game_dir, status_callback, progress_callback, max_callback)

            self.logger.info(f"Установка {self.profile.version_id} завершена")

        except Exception as e:
            self.logger.error(f"Ошибка установки: {str(e)}")
            raise

    def _install_vanilla(self, game_dir: str, status_cb: Callable, progress_cb: Callable, max_cb: Callable):
        """Установка vanilla Minecraft"""
        try:
            status_cb(f"Установка Minecraft {self.profile.version_id}...")

            # Создаем callback словарь для minecraft_launcher_lib
            callback_dict = {
                'setStatus': status_cb,
                'setProgress': progress_cb,
                'setMax': max_cb
            }

            # Устанавливаем версию
            mll.install.install_minecraft_version(
                self.profile.version_id,
                game_dir,
                callback=callback_dict
            )

            self.logger.info(f"Установка vanilla {self.profile.version_id} завершена")

        except Exception as e:
            self.logger.error(f"Ошибка установки vanilla: {str(e)}")
            raise

    def _install_forge(self, game_dir: str, status_cb: Callable, progress_cb: Callable, max_cb: Callable):
        """Установка Forge"""
        self.logger.info(f"Установка Forge для {self.profile.version_id}")

        try:
            # Определяем версию Forge
            forge_version = self.profile.loader_version
            if not forge_version:
                status_cb("Поиск версий Forge...")
                forge_versions = mll.forge.find_forge_version(self.profile.version_id)
                if not forge_versions:
                    self.logger.error(f"Не найдены версии Forge для {self.profile.version_id}")
                    raise ValueError(f"Не найдены версии Forge для {self.profile.version_id}")

                forge_version = forge_versions[-1]  # Последняя версия

            # Сначала устанавливаем базовую версию
            status_cb(f"Установка Minecraft {self.profile.version_id}...")
            callback_dict = {
                'setStatus': status_cb,
                'setProgress': lambda p: progress_cb(p // 2),  # Первая половина прогресса
                'setMax': max_cb
            }

            mll.install.install_minecraft_version(
                self.profile.version_id,
                game_dir,
                callback=callback_dict
            )

            # Проверяем отмену
            if self.abort:
                return

            # Затем устанавливаем Forge
            status_cb(f"Установка Forge {forge_version}...")

            def forge_progress_cb(progress):
                # Вторая половина прогресса (50-100%)
                adjusted_progress = 50 + (progress // 2)
                progress_cb(adjusted_progress)

            forge_callback_dict = {
                'setStatus': status_cb,
                'setProgress': forge_progress_cb,
                'setMax': max_cb
            }

            mll.forge.install_forge_version(
                forge_version,
                game_dir,
                callback=forge_callback_dict
            )

            # Обновляем профиль с корректной версией Forge
            if not self.profile.loader_version:
                self.profile.loader_version = forge_version
                self.profile.save()

            self.logger.info(f"Установка Forge {forge_version} завершена")

        except Exception as e:
            self.logger.error(f"Ошибка установки Forge: {str(e)}")
            raise

    def _install_fabric(self, game_dir: str, status_cb: Callable, progress_cb: Callable, max_cb: Callable):
        """Установка Fabric"""
        self.logger.info(f"Установка Fabric для {self.profile.version_id}")

        try:
            # Определяем версию Fabric
            fabric_version = self.profile.loader_version
            if not fabric_version:
                status_cb("Поиск версий Fabric...")
                try:
                    fabric_versions = mll.fabric.get_all_loader_versions()
                    if not fabric_versions:
                        self.logger.error("Не найдены версии Fabric")
                        raise ValueError("Не найдены версии Fabric")

                    fabric_version = fabric_versions[0]["version"]  # Последняя версия
                except Exception as e:
                    # Fallback к предустановленной версии
                    fabric_version = "0.14.21"
                    self.logger.warning(f"Использование fallback версии Fabric: {fabric_version}")

            # Сначала устанавливаем базовую версию
            status_cb(f"Установка Minecraft {self.profile.version_id}...")
            callback_dict = {
                'setStatus': status_cb,
                'setProgress': lambda p: progress_cb(p // 2),  # Первая половина прогресса
                'setMax': max_cb
            }

            mll.install.install_minecraft_version(
                self.profile.version_id,
                game_dir,
                callback=callback_dict
            )

            # Проверяем отмену
            if self.abort:
                return

            # Затем устанавливаем Fabric
            status_cb(f"Установка Fabric {fabric_version}...")

            def fabric_progress_cb(progress):
                # Вторая половина прогресса (50-100%)
                adjusted_progress = 50 + (progress // 2)
                progress_cb(adjusted_progress)

            fabric_callback_dict = {
                'setStatus': status_cb,
                'setProgress': fabric_progress_cb,
                'setMax': max_cb
            }

            mll.fabric.install_fabric(
                self.profile.version_id,
                game_dir,
                fabric_version,
                callback=fabric_callback_dict
            )

            # Обновляем профиль с корректной версией Fabric
            if not self.profile.loader_version:
                self.profile.loader_version = fabric_version
                self.profile.save()

            self.logger.info(f"Установка Fabric {fabric_version} завершена")

        except Exception as e:
            self.logger.error(f"Ошибка установки Fabric: {str(e)}")
            raise

    def _launch_minecraft(self):
        """Запуск Minecraft"""
        self.logger.info(f"Запуск Minecraft с профилем: {self.profile.name}")

        # Обновляем статус
        self._emit_progress(100, 100, "Запуск игры...")

        try:
            # Получаем директорию для игры
            game_dir = self.profile.game_directory or self.paths.minecraft_dir

            # Определяем версию для запуска
            launch_version = self._get_launch_version()

            # Получаем данные аккаунта
            username, uuid_str, access_token = self.auth_service.get_account_for_launch()

            # Настройки запуска
            options = {
                "username": username,
                "uuid": uuid_str,
                "token": access_token,
                "launcherName": "SUPLAUNCHER",
                "launcherVersion": "1.0.0",
                "gameDirectory": game_dir,
            }

            # Добавляем JVM аргументы
            if self.profile.java_args:
                jvm_args = self.profile.java_args.split()
                # Добавляем настройки памяти
                jvm_args.extend([
                    f"-Xms{self.profile.min_ram}M",
                    f"-Xmx{self.profile.max_ram}M"
                ])
                options["jvmArguments"] = jvm_args
            else:
                # Базовые настройки памяти
                options["jvmArguments"] = [
                    f"-Xms{self.profile.min_ram}M",
                    f"-Xmx{self.profile.max_ram}M"
                ]

            # Настройки разрешения
            if not self.profile.fullscreen:
                options["resolutionWidth"] = str(self.profile.resolution_width)
                options["resolutionHeight"] = str(self.profile.resolution_height)

            # Если указан кастомный путь к Java
            if self.profile.java_path and os.path.exists(self.profile.java_path):
                options["executablePath"] = self.profile.java_path

            # Получаем команду запуска
            self._emit_progress(100, 100, "Формирование команды запуска...")

            command = mll.command.get_minecraft_command(
                launch_version,
                game_dir,
                options
            )

            self.logger.info(f"Команда запуска: {' '.join(command[:5])}... (обрезано)")

            # Запускаем процесс
            self._emit_progress(100, 100, "Запуск процесса...")

            # Определяем флаги создания процесса в зависимости от ОС
            creation_flags = 0
            if os.name == 'nt':  # Windows
                creation_flags = subprocess.CREATE_NEW_CONSOLE

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                creationflags=creation_flags,
                cwd=game_dir
            )

            # Обновляем время последнего использования профиля
            self.profile.update_last_used()

            self.logger.info(f"Процесс Minecraft запущен с PID: {process.pid}")

        except Exception as e:
            self.logger.error(f"Ошибка запуска Minecraft: {str(e)}")
            raise

    def _get_launch_version(self) -> str:
        """Определение версии для запуска"""
        if self.profile.loader_type == "forge":
            if self.profile.loader_version:
                # Для Forge используем полное имя версии
                if self.profile.loader_version.startswith(self.profile.version_id):
                    return self.profile.loader_version
                else:
                    return f"{self.profile.version_id}-forge-{self.profile.loader_version}"
            else:
                return self.profile.version_id
        elif self.profile.loader_type == "fabric":
            if self.profile.loader_version:
                # Для Fabric используем fabric-loader формат
                return f"fabric-loader-{self.profile.loader_version}-{self.profile.version_id}"
            else:
                return self.profile.version_id
        else:
            # Vanilla
            return self.profile.version_id

    def _is_version_installed(self, version_id: str, game_dir: str) -> bool:
        """Проверка, установлена ли версия"""
        try:
            version_dir = os.path.join(game_dir, "versions", version_id)
            version_json = os.path.join(version_dir, f"{version_id}.json")
            return os.path.exists(version_json)
        except Exception:
            return False


class MinecraftService:
    """Сервис для управления Minecraft"""

    def __init__(self):
        self.logger = Logger().get_logger()
        self.paths = Paths()
        self.auth_service = AuthService()

    def create_launch_thread(self, profile: Profile) -> MinecraftLaunchThread:
        """Создание потока запуска для профиля"""
        return MinecraftLaunchThread(profile)

    def get_installed_versions(self) -> list:
        """Получение списка установленных версий"""
        try:
            versions_dir = os.path.join(self.paths.minecraft_dir, "versions")
            if not os.path.exists(versions_dir):
                return []

            installed = []
            for item in os.listdir(versions_dir):
                version_dir = os.path.join(versions_dir, item)
                if os.path.isdir(version_dir):
                    version_json = os.path.join(version_dir, f"{item}.json")
                    if os.path.exists(version_json):
                        installed.append(item)

            return sorted(installed)
        except Exception as e:
            self.logger.error(f"Ошибка получения установленных версий: {str(e)}")
            return []

    def is_version_installed(self, version_id: str) -> bool:
        """Проверка, установлена ли версия"""
        try:
            version_dir = os.path.join(self.paths.minecraft_dir, "versions", version_id)
            version_json = os.path.join(version_dir, f"{version_id}.json")
            return os.path.exists(version_json)
        except Exception:
            return False

    def delete_version(self, version_id: str) -> bool:
        """Удаление установленной версии"""
        try:
            version_dir = os.path.join(self.paths.minecraft_dir, "versions", version_id)
            if os.path.exists(version_dir):
                import shutil
                shutil.rmtree(version_dir)
                self.logger.info(f"Версия {version_id} удалена")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Ошибка удаления версии {version_id}: {str(e)}")
            return False

    def get_version_info(self, version_id: str) -> Optional[Dict]:
        """Получение информации о версии"""
        try:
            version_json_path = os.path.join(self.paths.minecraft_dir, "versions", version_id, f"{version_id}.json")
            if os.path.exists(version_json_path):
                import json
                with open(version_json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о версии {version_id}: {str(e)}")
            return None

# Minecraft сервис оптимизирован для Юра
