"""
Модуль ядра приложения
Содержит базовые классы, конфигурацию и утилиты
"""

# Основные компоненты ядра
from .config import (
    APP_NAME,
    APP_VERSION,
    APP_AUTHOR,
    COLORS,
    UI,
    FONTS,
    ANIMATIONS,
    DEFAULT_GAME_SETTINGS,
    DEFAULT_LAUNCHER_SETTINGS
)
from .logger import Logger
from .paths import Paths
from .exceptions import (
    SuplauncherException,
    ConfigurationError,
    ProfileError,
    ProfileNotFoundError,
    ProfileValidationError,
    MinecraftError,
    MinecraftInstallationError,
    MinecraftLaunchError,
    AuthenticationError,
    NetworkError,
    FileSystemError,
    handle_exception,
    is_critical_error,
    get_recovery_suggestions
)
from .utils import (
    get_system_info,
    get_java_info,
    validate_username,
    validate_memory_settings,
    format_bytes,
    calculate_file_hash,
    safe_remove,
    ensure_directory,
    is_process_running,
    get_available_disk_space,
    open_file_manager,
    open_url,
    is_valid_url,
    compare_versions,
    sanitize_filename,
    create_backup,
    cleanup_old_files,
    get_temp_directory,
    is_admin,
    debounce,
    retry
)

__all__ = [
    # Конфигурация
    "APP_NAME",
    "APP_VERSION",
    "APP_AUTHOR",
    "COLORS",
    "UI",
    "FONTS",
    "ANIMATIONS",
    "DEFAULT_GAME_SETTINGS",
    "DEFAULT_LAUNCHER_SETTINGS",

    # Основные классы
    "Logger",
    "Paths",

    # Исключения
    "SuplauncherException",
    "ConfigurationError",
    "ProfileError",
    "ProfileNotFoundError",
    "ProfileValidationError",
    "MinecraftError",
    "MinecraftInstallationError",
    "MinecraftLaunchError",
    "AuthenticationError",
    "NetworkError",
    "FileSystemError",
    "handle_exception",
    "is_critical_error",
    "get_recovery_suggestions",

    # Утилиты
    "get_system_info",
    "get_java_info",
    "validate_username",
    "validate_memory_settings",
    "format_bytes",
    "calculate_file_hash",
    "safe_remove",
    "ensure_directory",
    "is_process_running",
    "get_available_disk_space",
    "open_file_manager",
    "open_url",
    "is_valid_url",
    "compare_versions",
    "sanitize_filename",
    "create_backup",
    "cleanup_old_files",
    "get_temp_directory",
    "is_admin",
    "debounce",
    "retry"
]