"""
Утилиты и вспомогательные функции для SUPLAUNCHER
"""

import os
import sys
import re
import hashlib
import shutil
import subprocess
import platform
import json
import tempfile
from typing import Optional, Dict, List, Tuple, Any, Union
from pathlib import Path
from datetime import datetime, timedelta

from core.logger import Logger
from core.exceptions import *

logger = Logger().get_logger()


def get_system_info() -> Dict[str, Any]:
    """Получение информации о системе"""
    try:
        import psutil

        # Информация о памяти
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        system_info = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'total_memory_gb': round(memory.total / (1024 ** 3), 2),
            'available_memory_gb': round(memory.available / (1024 ** 3), 2),
            'memory_percent': memory.percent,
            'disk_total_gb': round(disk.total / (1024 ** 3), 2),
            'disk_free_gb': round(disk.free / (1024 ** 3), 2),
            'disk_used_percent': round((disk.used / disk.total) * 100, 1),
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1)
        }

        return system_info
    except ImportError:
        # Fallback если psutil не установлен
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    except Exception as e:
        logger.error(f"Ошибка получения системной информации: {e}")
        return {}


def get_java_info(java_path: Optional[str] = None) -> Optional[Dict[str, str]]:
    """Получение информации о Java"""
    try:
        # Определяем путь к java
        if java_path:
            java_executable = java_path
        else:
            java_executable = shutil.which('java')
            if not java_executable:
                # Попробуем стандартные пути
                possible_paths = []
                if platform.system() == "Windows":
                    possible_paths = [
                        r"C:\Program Files\Java\*\bin\java.exe",
                        r"C:\Program Files (x86)\Java\*\bin\java.exe"
                    ]
                elif platform.system() == "Darwin":  # macOS
                    possible_paths = [
                        "/Library/Java/JavaVirtualMachines/*/Contents/Home/bin/java",
                        "/System/Library/Java/JavaVirtualMachines/*/Contents/Home/bin/java"
                    ]
                else:  # Linux
                    possible_paths = [
                        "/usr/bin/java",
                        "/usr/lib/jvm/*/bin/java"
                    ]

                for path_pattern in possible_paths:
                    if '*' in path_pattern:
                        import glob
                        matches = glob.glob(path_pattern)
                        if matches:
                            java_executable = matches[0]
                            break
                    elif os.path.exists(path_pattern):
                        java_executable = path_pattern
                        break

        if not java_executable or not os.path.exists(java_executable):
            return None

        # Получаем версию Java
        result = subprocess.run(
            [java_executable, '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return None

        # Парсим вывод версии
        version_output = result.stderr  # Java выводит версию в stderr
        version_match = re.search(r'version "([^"]+)"', version_output)

        if not version_match:
            return None

        version_string = version_match.group(1)

        # Определяем основную версию (8, 11, 17, etc.)
        if version_string.startswith('1.'):
            # Старый формат версий (1.8.0_XXX)
            major_version = version_string.split('.')[1]
        else:
            # Новый формат версий (11.0.X, 17.0.X)
            major_version = version_string.split('.')[0]

        # Определяем поставщика Java
        vendor = "Unknown"
        if "OpenJDK" in version_output:
            vendor = "OpenJDK"
        elif "Oracle" in version_output:
            vendor = "Oracle"
        elif "Eclipse" in version_output:
            vendor = "Eclipse Adoptium"
        elif "Azul" in version_output:
            vendor = "Azul Zulu"

        return {
            'path': java_executable,
            'version': version_string,
            'major_version': major_version,
            'vendor': vendor,
            'full_output': version_output.strip()
        }

    except Exception as e:
        logger.error(f"Ошибка получения информации о Java: {e}")
        return None


def validate_username(username: str) -> bool:
    """Валидация имени пользователя Minecraft"""
    if not username:
        return False

    # Длина от 3 до 16 символов
    if len(username) < 3 or len(username) > 16:
        return False

    # Только буквы, цифры и подчеркивания
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False

    return True


def validate_memory_settings(min_ram: int, max_ram: int, system_memory: Optional[int] = None) -> bool:
    """Валидация настроек памяти"""
    # Минимальные требования
    if min_ram < 512:  # Минимум 512 MB
        return False

    if max_ram < 1024:  # Минимум 1 GB
        return False

    # Максимум должен быть больше минимума
    if max_ram <= min_ram:
        return False

    # Проверяем доступную память системы
    if system_memory:
        # Не более 80% от системной памяти
        max_allowed = int(system_memory * 0.8)
        if max_ram > max_allowed:
            return False

    return True


def format_bytes(bytes_size: int) -> str:
    """Форматирование размера в байтах в читаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> Optional[str]:
    """Вычисление хеша файла"""
    try:
        hash_func = hashlib.new(algorithm)

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)

        return hash_func.hexdigest()
    except Exception as e:
        logger.error(f"Ошибка вычисления хеша файла {file_path}: {e}")
        return None


def safe_remove(path: str) -> bool:
    """Безопасное удаление файла или директории"""
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True
    except Exception as e:
        logger.error(f"Ошибка удаления {path}: {e}")
        return False


def ensure_directory(directory: str) -> bool:
    """Создание директории если она не существует"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Ошибка создания директории {directory}: {e}")
        return False


def copy_with_progress(src: str, dst: str, callback: Optional[callable] = None) -> bool:
    """Копирование файла с отчетом о прогрессе"""
    try:
        file_size = os.path.getsize(src)
        copied = 0

        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            while True:
                buf = fsrc.read(64 * 1024)  # 64KB chunks
                if not buf:
                    break

                fdst.write(buf)
                copied += len(buf)

                if callback:
                    progress = int((copied / file_size) * 100)
                    callback(progress, copied, file_size)

        return True
    except Exception as e:
        logger.error(f"Ошибка копирования {src} -> {dst}: {e}")
        return False


def is_process_running(process_name: str) -> bool:
    """Проверка, запущен ли процесс"""
    try:
        import psutil

        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                return True
        return False
    except ImportError:
        # Fallback без psutil
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output(['tasklist'], universal_newlines=True)
                return process_name.lower() in output.lower()
            else:
                output = subprocess.check_output(['ps', 'aux'], universal_newlines=True)
                return process_name.lower() in output.lower()
        except Exception:
            return False
    except Exception as e:
        logger.error(f"Ошибка проверки процесса {process_name}: {e}")
        return False


def kill_process_by_name(process_name: str) -> bool:
    """Завершение процесса по имени"""
    try:
        import psutil

        killed = False
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                    killed = True
                except psutil.TimeoutExpired:
                    proc.kill()
                    killed = True
                except Exception as e:
                    logger.error(f"Ошибка завершения процесса {proc.info['pid']}: {e}")

        return killed
    except ImportError:
        logger.warning("psutil не установлен, завершение процессов недоступно")
        return False
    except Exception as e:
        logger.error(f"Ошибка завершения процесса {process_name}: {e}")
        return False


def get_available_disk_space(path: str) -> Optional[int]:
    """Получение доступного места на диске в байтах"""
    try:
        import psutil
        disk_usage = psutil.disk_usage(path)
        return disk_usage.free
    except ImportError:
        # Fallback без psutil
        try:
            if platform.system() == "Windows":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(path),
                    ctypes.pointer(free_bytes),
                    None,
                    None
                )
                return free_bytes.value
            else:
                stat = os.statvfs(path)
                return stat.f_bavail * stat.f_frsize
        except Exception:
            return None
    except Exception as e:
        logger.error(f"Ошибка получения информации о диске для {path}: {e}")
        return None


def open_file_manager(path: str) -> bool:
    """Открытие файлового менеджера в указанной директории"""
    try:
        if not os.path.exists(path):
            return False

        system = platform.system()

        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])

        return True
    except Exception as e:
        logger.error(f"Ошибка открытия файлового менеджера для {path}: {e}")
        return False


def open_url(url: str) -> bool:
    """Открытие URL в браузере"""
    try:
        import webbrowser
        webbrowser.open(url)
        return True
    except Exception as e:
        logger.error(f"Ошибка открытия URL {url}: {e}")
        return False


def is_valid_url(url: str) -> bool:
    """Проверка валидности URL"""
    url_pattern = re.compile(
        r'^https?://'  # http:// или https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # домен
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # опциональный порт
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(url_pattern.match(url))


def normalize_version(version: str) -> str:
    """Нормализация строки версии для сравнения"""
    # Удаляем все кроме цифр и точек
    normalized = re.sub(r'[^\d.]', '', version)

    # Добавляем .0 если версия состоит из одной цифры
    parts = normalized.split('.')
    while len(parts) < 3:
        parts.append('0')

    return '.'.join(parts)


def compare_versions(version1: str, version2: str) -> int:
    """
    Сравнение версий
    Возвращает: -1 если version1 < version2, 0 если равны, 1 если version1 > version2
    """
    try:
        v1_parts = [int(x) for x in normalize_version(version1).split('.')]
        v2_parts = [int(x) for x in normalize_version(version2).split('.')]

        # Дополняем нулями до одинаковой длины
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))

        for i in range(max_len):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1

        return 0
    except Exception as e:
        logger.error(f"Ошибка сравнения версий {version1} и {version2}: {e}")
        return 0


def sanitize_filename(filename: str) -> str:
    """Очистка имени файла от недопустимых символов"""
    # Удаляем/заменяем недопустимые символы
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Удаляем точки в начале и конце
    filename = filename.strip('.')

    # Ограничиваем длину (255 символов для большинства ФС)
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext

    return filename


def create_backup(file_path: str, backup_dir: Optional[str] = None) -> Optional[str]:
    """Создание резервной копии файла"""
    try:
        if not os.path.exists(file_path):
            return None

        if backup_dir is None:
            backup_dir = os.path.dirname(file_path)

        ensure_directory(backup_dir)

        # Генерируем имя бэкапа с timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)
        backup_name = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(backup_dir, backup_name)

        shutil.copy2(file_path, backup_path)
        logger.info(f"Создана резервная копия: {backup_path}")

        return backup_path
    except Exception as e:
        logger.error(f"Ошибка создания резервной копии {file_path}: {e}")
        return None


def cleanup_old_files(directory: str, max_age_days: int = 30, pattern: str = "*") -> int:
    """Очистка старых файлов в директории"""
    try:
        if not os.path.exists(directory):
            return 0

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0

        import glob
        for file_path in glob.glob(os.path.join(directory, pattern)):
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.debug(f"Удален старый файл: {file_path}")
                    except Exception as e:
                        logger.error(f"Ошибка удаления файла {file_path}: {e}")

        return deleted_count
    except Exception as e:
        logger.error(f"Ошибка очистки директории {directory}: {e}")
        return 0


def get_temp_directory() -> str:
    """Получение временной директории"""
    temp_dir = os.path.join(tempfile.gettempdir(), "suplauncher")
    ensure_directory(temp_dir)
    return temp_dir


def is_admin() -> bool:
    """Проверка, запущено ли приложение с правами администратора"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False


def restart_as_admin() -> bool:
    """Перезапуск приложения с правами администратора"""
    try:
        if platform.system() == "Windows":
            import ctypes
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            return True
        else:
            # Для Unix-подобных систем требуется sudo
            args = ["sudo", sys.executable] + sys.argv
            subprocess.run(args)
            return True
    except Exception as e:
        logger.error(f"Ошибка перезапуска с правами администратора: {e}")
        return False


def debounce(wait_time: float):
    """Декоратор для debounce функций"""

    def decorator(func):
        last_called = [0.0]

        def wrapper(*args, **kwargs):
            import time
            now = time.time()
            if now - last_called[0] >= wait_time:
                last_called[0] = now
                return func(*args, **kwargs)

        return wrapper

    return decorator


# Утилиты разработаны для максимального удобства Юра


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Декоратор для повторных попыток выполнения функции"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay

            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        logger.error(f"Все попытки исчерпаны для {func.__name__}: {e}")
                        raise

                    logger.warning(f"Попытка {attempts} не удалась для {func.__name__}: {e}")
                    import time
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper

    return decorator
