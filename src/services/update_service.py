import requests
from typing import Optional
import json
import os

from core.logger import Logger
from core.paths import Paths
from core.config import APP_VERSION


class UpdateService:
    """Сервис для проверки и установки обновлений"""

    def __init__(self):
        self.logger = Logger().get_logger()
        self.paths = Paths()

        # URL API для проверки обновлений
        self.api_url = "https://villadesup.ru/api/launcher/updates"

    def check_for_updates(self) -> Optional[str]:
        """Проверка наличия обновлений"""
        try:
            self.logger.info("Проверка обновлений...")

            # Запрос к API
            response = requests.get(self.api_url, timeout=5)
            if response.status_code != 200:
                self.logger.error(f"Ошибка API: {response.status_code}")
                return None

            # Парсинг ответа
            data = response.json()
            latest_version = data.get("latest_version")

            if not latest_version:
                self.logger.error("В ответе API отсутствует информация о последней версии")
                return None

            # Сравнение версий
            if self._compare_versions(latest_version, APP_VERSION) > 0:
                self.logger.info(f"Доступно обновление: {latest_version} (текущая: {APP_VERSION})")
                return latest_version

            self.logger.info(f"Обновлений нет. Текущая версия: {APP_VERSION}")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка проверки обновлений: {str(e)}")
            return None

    def get_update_info(self, version: str) -> Optional[dict]:
        """Получение информации об обновлении"""
        try:
            self.logger.info(f"Запрос информации о версии {version}...")

            # Запрос к API
            response = requests.get(f"{self.api_url}/{version}", timeout=5)
            if response.status_code != 200:
                self.logger.error(f"Ошибка API: {response.status_code}")
                return None

            # Парсинг ответа
            data = response.json()

            if not data:
                self.logger.error("В ответе API отсутствует информация об обновлении")
                return None

            return data
        except Exception as e:
            self.logger.error(f"Ошибка получения информации об обновлении: {str(e)}")
            return None

    def download_update(self, version: str, output_path: str) -> bool:
        """Загрузка обновления"""
        try:
            self.logger.info(f"Загрузка обновления {version}...")

            # Получаем информацию об обновлении
            update_info = self.get_update_info(version)
            if not update_info:
                return False

            # URL для загрузки
            download_url = update_info.get("download_url")
            if not download_url:
                self.logger.error("В информации об обновлении отсутствует URL для загрузки")
                return False

            # Загрузка файла
            response = requests.get(download_url, stream=True, timeout=60)
            if response.status_code != 200:
                self.logger.error(f"Ошибка загрузки: {response.status_code}")
                return False

            # Сохранение файла
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.logger.info(f"Обновление загружено в {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка загрузки обновления: {str(e)}")
            return False

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Сравнение версий

        Возвращает:
            1, если version1 > version2
            0, если version1 == version2
            -1, если version1 < version2
        """
        try:
            # Разбиваем версии на компоненты
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]

            # Дополняем нулями до одинаковой длины
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            # Сравниваем поэлементно
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1

            return 0
        except Exception as e:
            self.logger.error(f"Ошибка сравнения версий: {str(e)}")
            return 0
