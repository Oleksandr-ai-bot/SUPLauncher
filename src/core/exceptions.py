"""
Кастомные исключения для SUPLAUNCHER
"""


class SuplauncherException(Exception):
    """Базовое исключение для всех ошибок SUPLAUNCHER"""
    pass


class ConfigurationError(SuplauncherException):
    """Ошибки конфигурации"""
    pass


class ProfileError(SuplauncherException):
    """Ошибки работы с профилями"""
    pass


class ProfileNotFoundError(ProfileError):
    """Профиль не найден"""

    def __init__(self, profile_id: str):
        self.profile_id = profile_id
        super().__init__(f"Профиль с ID '{profile_id}' не найден")


class ProfileValidationError(ProfileError):
    """Ошибка валидации профиля"""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Ошибка валидации поля '{field}': {message}")


class MinecraftError(SuplauncherException):
    """Ошибки запуска Minecraft"""
    pass


class MinecraftInstallationError(MinecraftError):
    """Ошибка установки Minecraft"""

    def __init__(self, version: str, message: str):
        self.version = version
        self.message = message
        super().__init__(f"Ошибка установки версии '{version}': {message}")


class MinecraftLaunchError(MinecraftError):
    """Ошибка запуска Minecraft"""

    def __init__(self, profile_name: str, message: str):
        self.profile_name = profile_name
        self.message = message
        super().__init__(f"Ошибка запуска профиля '{profile_name}': {message}")


class AuthenticationError(SuplauncherException):
    """Ошибки аутентификации"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Неверные учетные данные"""
    pass


class AccountNotFoundError(AuthenticationError):
    """Аккаунт не найден"""

    def __init__(self, account_id: str):
        self.account_id = account_id
        super().__init__(f"Аккаунт с ID '{account_id}' не найден")


class NetworkError(SuplauncherException):
    """Ошибки сети"""
    pass


class APIError(NetworkError):
    """Ошибки API"""

    def __init__(self, endpoint: str, status_code: int, message: str):
        self.endpoint = endpoint
        self.status_code = status_code
        self.message = message
        super().__init__(f"Ошибка API {endpoint} (HTTP {status_code}): {message}")


class DownloadError(NetworkError):
    """Ошибка загрузки файлов"""

    def __init__(self, url: str, message: str):
        self.url = url
        self.message = message
        super().__init__(f"Ошибка загрузки '{url}': {message}")


class FileSystemError(SuplauncherException):
    """Ошибки файловой системы"""
    pass


class DirectoryNotFoundError(FileSystemError):
    """Директория не найдена"""

    def __init__(self, directory: str):
        self.directory = directory
        super().__init__(f"Директория не найдена: {directory}")


class InsufficientPermissionsError(FileSystemError):
    """Недостаточно прав доступа"""

    def __init__(self, path: str, operation: str):
        self.path = path
        self.operation = operation
        super().__init__(f"Недостаточно прав для операции '{operation}' с '{path}'")


class InsufficientSpaceError(FileSystemError):
    """Недостаточно места на диске"""

    def __init__(self, required_space: int, available_space: int):
        self.required_space = required_space
        self.available_space = available_space
        super().__init__(
            f"Недостаточно места на диске. "
            f"Требуется: {required_space // (1024 * 1024)} MB, "
            f"доступно: {available_space // (1024 * 1024)} MB"
        )


class VersionError(SuplauncherException):
    """Ошибки работы с версиями"""
    pass


class UnsupportedVersionError(VersionError):
    """Неподдерживаемая версия"""

    def __init__(self, version: str, supported_versions: list):
        self.version = version
        self.supported_versions = supported_versions
        super().__init__(
            f"Версия '{version}' не поддерживается. "
            f"Поддерживаемые версии: {', '.join(supported_versions)}"
        )


class VersionNotFoundError(VersionError):
    """Версия не найдена"""

    def __init__(self, version: str, version_type: str = "Minecraft"):
        self.version = version
        self.version_type = version_type
        super().__init__(f"{version_type} версия '{version}' не найдена")


class LoaderError(SuplauncherException):
    """Ошибки загрузчиков модов"""
    pass


class UnsupportedLoaderError(LoaderError):
    """Неподдерживаемый загрузчик"""

    def __init__(self, loader: str, supported_loaders: list):
        self.loader = loader
        self.supported_loaders = supported_loaders
        super().__init__(
            f"Загрузчик '{loader}' не поддерживается. "
            f"Поддерживаемые загрузчики: {', '.join(supported_loaders)}"
        )


class LoaderCompatibilityError(LoaderError):
    """Ошибка совместимости загрузчика"""

    def __init__(self, loader: str, loader_version: str, minecraft_version: str):
        self.loader = loader
        self.loader_version = loader_version
        self.minecraft_version = minecraft_version
        super().__init__(
            f"Загрузчик {loader} {loader_version} "
            f"несовместим с Minecraft {minecraft_version}"
        )


class UIError(SuplauncherException):
    """Ошибки пользовательского интерфейса"""
    pass


class ThemeError(UIError):
    """Ошибка темы оформления"""

    def __init__(self, theme_name: str, message: str):
        self.theme_name = theme_name
        self.message = message
        super().__init__(f"Ошибка темы '{theme_name}': {message}")


class ResourceError(UIError):
    """Ошибка загрузки ресурсов"""

    def __init__(self, resource_path: str, resource_type: str):
        self.resource_path = resource_path
        self.resource_type = resource_type
        super().__init__(f"Не удалось загрузить {resource_type}: {resource_path}")


class ValidationError(SuplauncherException):
    """Ошибки валидации"""

    def __init__(self, field: str, value: any, message: str):
        self.field = field
        self.value = value
        self.message = message
        super().__init__(f"Ошибка валидации поля '{field}' (значение: {value}): {message}")


class CacheError(SuplauncherException):
    """Ошибки кэша"""
    pass


class CacheCorruptedError(CacheError):
    """Поврежденный кэш"""

    def __init__(self, cache_name: str):
        self.cache_name = cache_name
        super().__init__(f"Кэш '{cache_name}' поврежден и будет пересоздан")


class UpdateError(SuplauncherException):
    """Ошибки обновления"""
    pass


class UpdateCheckError(UpdateError):
    """Ошибка проверки обновлений"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Ошибка проверки обновлений: {message}")


class UpdateDownloadError(UpdateError):
    """Ошибка загрузки обновления"""

    def __init__(self, version: str, message: str):
        self.version = version
        self.message = message
        super().__init__(f"Ошибка загрузки обновления {version}: {message}")


class JavaError(SuplauncherException):
    """Ошибки Java"""
    pass


class JavaNotFoundError(JavaError):
    """Java не найдена"""

    def __init__(self, java_path: str = None):
        self.java_path = java_path
        if java_path:
            super().__init__(f"Java не найдена по пути: {java_path}")
        else:
            super().__init > ("Java не найдена в системе")


class UnsupportedJavaVersionError(JavaError):
    """Неподдерживаемая версия Java"""

    def __init__(self, found_version: str, required_version: str):
        self.found_version = found_version
        self.required_version = required_version
        super().__init__(
            f"Неподдерживаемая версия Java: {found_version}. "
            f"Требуется: {required_version} или выше"
        )


class MemoryError(SuplauncherException):
    """Ошибки памяти"""
    pass


class InsufficientMemoryError(MemoryError):
    """Недостаточно памяти"""

    def __init__(self, requested: int, available: int):
        self.requested = requested
        self.available = available
        super().__init__(
            f"Недостаточно памяти. "
            f"Запрошено: {requested} MB, доступно: {available} MB"
        )


class InvalidMemoryConfigurationError(MemoryError):
    """Неверная конфигурация памяти"""

    def __init__(self, min_ram: int, max_ram: int):
        self.min_ram = min_ram
        self.max_ram = max_ram
        super().__init__(
            f"Неверная конфигурация памяти: "
            f"минимум ({min_ram} MB) больше максимума ({max_ram} MB)"
        )


# Вспомогательные функции для работы с исключениями

def handle_exception(exception: Exception, context: str = None) -> str:
    """
    Обработка исключения и возврат пользовательского сообщения

    Args:
        exception: Исключение для обработки
        context: Контекст, в котором произошло исключение

    Returns:
        Пользовательское сообщение об ошибке
    """
    if isinstance(exception, SuplauncherException):
        # Для наших кастомных исключений возвращаем сообщение как есть
        return str(exception)

    # Для системных исключений возвращаем более дружелюбное сообщение
    error_messages = {
        FileNotFoundError: "Файл не найден",
        PermissionError: "Недостаточно прав доступа",
        OSError: "Ошибка операционной системы",
        ConnectionError: "Ошибка соединения",
        TimeoutError: "Превышено время ожидания",
        MemoryError: "Недостаточно памяти",
        KeyboardInterrupt: "Операция прервана пользователем"
    }

    error_type = type(exception)
    user_message = error_messages.get(error_type, "Произошла неожиданная ошибка")

    if context:
        user_message = f"{user_message} в контексте: {context}"

    return user_message


def is_critical_error(exception: Exception) -> bool:
    """
    Определяет, является ли ошибка критической

    Args:
        exception: Исключение для проверки

    Returns:
        True, если ошибка критическая
    """
    critical_errors = (
        ConfigurationError,
        InsufficientSpaceError,
        InsufficientPermissionsError,
        JavaNotFoundError,
        InsufficientMemoryError
    )

    return isinstance(exception, critical_errors) or isinstance(exception, (
        MemoryError,
        SystemError,
        OSError
    ))


def get_recovery_suggestions(exception: Exception) -> list:
    """
    Получение предложений по восстановлению после ошибки

    Args:
        exception: Исключение

    Returns:
        Список предложений по исправлению
    """
    suggestions = []

    if isinstance(exception, JavaNotFoundError):
        suggestions.extend([
            "Установите Java 8 или выше",
            "Укажите путь к Java в настройках",
            "Перезапустите лаунчер после установки Java"
        ])

    elif isinstance(exception, InsufficientMemoryError):
        suggestions.extend([
            "Закройте другие приложения",
            "Уменьшите выделяемую память в настройках профиля",
            "Перезагрузите компьютер"
        ])

    elif isinstance(exception, InsufficientSpaceError):
        suggestions.extend([
            "Освободите место на диске",
            "Удалите ненужные файлы",
            "Выберите другую директорию для игры"
        ])

    elif isinstance(exception, NetworkError):
        suggestions.extend([
            "Проверьте интернет-соединение",
            "Отключите VPN или прокси",
            "Попробуйте позже"
        ])

    elif isinstance(exception, ProfileValidationError):
        suggestions.extend([
            "Проверьте правильность заполнения полей",
            "Используйте допустимые символы в названии",
            "Выберите существующую версию игры"
        ])

    elif isinstance(exception, LoaderCompatibilityError):
        suggestions.extend([
            "Выберите совместимую версию загрузчика",
            "Обновите версию Minecraft",
            "Проверьте официальную документацию загрузчика"
        ])

    else:
        suggestions.extend([
            "Перезапустите лаунчер",
            "Проверьте логи для получения дополнительной информации",
            "Обратитесь в службу поддержки"
        ])

    return suggestions

# Система исключений продумана для безопасности проекта Юра