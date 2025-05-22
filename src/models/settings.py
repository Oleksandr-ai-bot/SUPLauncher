import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, Any

from core.paths import Paths
from core.logger import Logger
from core.config import DEFAULT_LAUNCHER_SETTINGS

logger = Logger().get_logger()
paths = Paths()


@dataclass
class LauncherSettings:
    """Настройки лаунчера"""

    close_on_launch: bool = DEFAULT_LAUNCHER_SETTINGS["close_on_launch"]
    keep_launcher_open: bool = DEFAULT_LAUNCHER_SETTINGS["keep_launcher_open"]
    check_updates: bool = DEFAULT_LAUNCHER_SETTINGS["check_updates"]
    enable_animations: bool = DEFAULT_LAUNCHER_SETTINGS["enable_animations"]
    enable_sounds: bool = DEFAULT_LAUNCHER_SETTINGS["enable_sounds"]
    language: str = DEFAULT_LAUNCHER_SETTINGS["language"]
    theme: str = DEFAULT_LAUNCHER_SETTINGS["theme"]
    last_selected_profile: Optional[str] = None
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def save(self) -> bool:
        """Сохраняет настройки в файл"""
        try:
            config_path = paths.get_config_file()
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=2)

            logger.info("Настройки лаунчера сохранены")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {str(e)}")
            return False

    @classmethod
    def load(cls) -> 'LauncherSettings':
        """Загружает настройки из файла или возвращает настройки по умолчанию"""
        try:
            config_path = paths.get_config_file()

            if not os.path.exists(config_path):
                logger.info("Файл настроек не найден, используются настройки по умолчанию")
                return cls()

            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            settings = cls(**data)
            logger.info("Настройки лаунчера загружены")
            return settings
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {str(e)}. Используются настройки по умолчанию")
            return cls()
