import json
import os
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

import minecraft_launcher_lib as mll

from core.logger import Logger
from core.paths import Paths


@dataclass
class MinecraftVersion:
    """Класс для представления версии Minecraft"""
    id: str
    type: str  # "release", "snapshot", "old_beta", "old_alpha"
    url: str
    time: str
    release_time: str

    def to_dict(self) -> Dict:
        """Преобразование в словарь"""
        return {
            "id": self.id,
            "type": self.type,
            "url": self.url,
            "time": self.time,
            "release_time": self.release_time
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MinecraftVersion':
        """Создание из словаря"""
        return cls(**data)


@dataclass
class LoaderVersion:
    """Класс для представления версии загрузчика (Forge, Fabric, etc.)"""
    id: str
    minecraft_version: str
    loader_type: str  # "forge", "fabric", "quilt"
    loader_version: str
    stable: bool = True

    def to_dict(self) -> Dict:
        """Преобразование в словарь"""
        return {
            "id": self.id,
            "minecraft_version": self.minecraft_version,
            "loader_type": self.loader_type,
            "loader_version": self.loader_version,
            "stable": self.stable
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'LoaderVersion':
        """Создание из словаря"""
        return cls(**data)


class VersionService:
    """Сервис для работы с версиями Minecraft и загрузчиками"""

    def __init__(self):
        self.logger = Logger().get_logger()
        self.paths = Paths()

        # Файлы кэша
        self.versions_cache_file = os.path.join(self.paths.cache_dir, "minecraft_versions.json")
        self.forge_cache_file = os.path.join(self.paths.cache_dir, "forge_versions.json")
        self.fabric_cache_file = os.path.join(self.paths.cache_dir, "fabric_versions.json")

        # Время жизни кэша (24 часа)
        self.cache_lifetime = timedelta(hours=24)

        # Кэш версий
        self._minecraft_versions = None
        self._forge_versions = None
        self._fabric_versions = None

        # Обеспечиваем существование директории кэша
        os.makedirs(self.paths.cache_dir, exist_ok=True)

    def get_minecraft_versions(self, include_snapshots: bool = False) -> List[MinecraftVersion]:
        """Получение списка версий Minecraft"""
        try:
            # Проверяем кэш
            if self._minecraft_versions is None:
                self._minecraft_versions = self._load_minecraft_versions_cache()

            # Если кэш пуст или устарел, обновляем
            if not self._minecraft_versions or self._is_cache_expired(self.versions_cache_file):
                self._update_minecraft_versions_cache()

            # Фильтруем версии
            versions = []
            for version in self._minecraft_versions:
                if version.type == "release":
                    versions.append(version)
                elif include_snapshots and version.type == "snapshot":
                    versions.append(version)

            return versions
        except Exception as e:
            self.logger.error(f"Ошибка получения версий Minecraft: {str(e)}")
            return self._get_fallback_minecraft_versions()

    def get_forge_versions(self, minecraft_version: str) -> List[LoaderVersion]:
        """Получение списка версий Forge для указанной версии Minecraft"""
        try:
            # Проверяем кэш
            if self._forge_versions is None:
                self._forge_versions = self._load_forge_versions_cache()

            # Если кэш пуст или устарел, обновляем
            if not self._forge_versions or self._is_cache_expired(self.forge_cache_file):
                self._update_forge_versions_cache()

            # Фильтруем по версии Minecraft
            versions = []
            for version in self._forge_versions:
                if version.minecraft_version == minecraft_version:
                    versions.append(version)

            return versions
        except Exception as e:
            self.logger.error(f"Ошибка получения версий Forge: {str(e)}")
            return self._get_fallback_forge_versions(minecraft_version)

    def get_fabric_versions(self, minecraft_version: str) -> List[LoaderVersion]:
        """Получение списка версий Fabric для указанной версии Minecraft"""
        try:
            # Проверяем кэш
            if self._fabric_versions is None:
                self._fabric_versions = self._load_fabric_versions_cache()

            # Если кэш пуст или устарел, обновляем
            if not self._fabric_versions or self._is_cache_expired(self.fabric_cache_file):
                self._update_fabric_versions_cache()

            # Фильтруем по версии Minecraft
            versions = []
            for version in self._fabric_versions:
                if version.minecraft_version == minecraft_version:
                    versions.append(version)

            return versions
        except Exception as e:
            self.logger.error(f"Ошибка получения версий Fabric: {str(e)}")
            return self._get_fallback_fabric_versions(minecraft_version)

    def get_latest_release_version(self) -> Optional[str]:
        """Получение последней релизной версии Minecraft"""
        try:
            versions = self.get_minecraft_versions(include_snapshots=False)
            if versions:
                return versions[0].id
            return None
        except Exception as e:
            self.logger.error(f"Ошибка получения последней версии: {str(e)}")
            return "1.20.1"  # Fallback

    def get_latest_forge_version(self, minecraft_version: str) -> Optional[str]:
        """Получение последней версии Forge для указанной версии Minecraft"""
        try:
            versions = self.get_forge_versions(minecraft_version)

            # Ищем стабильные версии сначала
            stable_versions = [v for v in versions if v.stable]
            if stable_versions:
                return stable_versions[0].id

            # Если нет стабильных, возвращаем первую доступную
            if versions:
                return versions[0].id

            return None
        except Exception as e:
            self.logger.error(f"Ошибка получения последней версии Forge: {str(e)}")
            return None

    def get_latest_fabric_version(self, minecraft_version: str) -> Optional[str]:
        """Получение последней версии Fabric для указанной версии Minecraft"""
        try:
            versions = self.get_fabric_versions(minecraft_version)

            # Ищем стабильные версии сначала
            stable_versions = [v for v in versions if v.stable]
            if stable_versions:
                return stable_versions[0].id

            # Если нет стабильных, возвращаем первую доступную
            if versions:
                return versions[0].id

            return None
        except Exception as e:
            self.logger.error(f"Ошибка получения последней версии Fabric: {str(e)}")
            return None

    def is_version_installed(self, version_id: str) -> bool:
        """Проверка, установлена ли версия"""
        try:
            version_dir = os.path.join(self.paths.versions_dir, version_id)
            version_json = os.path.join(version_dir, f"{version_id}.json")
            version_jar = os.path.join(version_dir, f"{version_id}.jar")

            return os.path.exists(version_json) and os.path.exists(version_jar)
        except Exception as e:
            self.logger.error(f"Ошибка проверки установки версии: {str(e)}")
            return False

    def get_installed_versions(self) -> List[str]:
        """Получение списка установленных версий"""
        try:
            if not os.path.exists(self.paths.versions_dir):
                return []

            installed = []
            for item in os.listdir(self.paths.versions_dir):
                version_dir = os.path.join(self.paths.versions_dir, item)
                if os.path.isdir(version_dir):
                    version_json = os.path.join(version_dir, f"{item}.json")
                    if os.path.exists(version_json):
                        installed.append(item)

            return installed
        except Exception as e:
            self.logger.error(f"Ошибка получения установленных версий: {str(e)}")
            return []

    def _load_minecraft_versions_cache(self) -> List[MinecraftVersion]:
        """Загрузка кэша версий Minecraft"""
        try:
            if not os.path.exists(self.versions_cache_file):
                return []

            with open(self.versions_cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            versions = []
            for version_data in data.get("versions", []):
                try:
                    versions.append(MinecraftVersion.from_dict(version_data))
                except Exception as e:
                    self.logger.error(f"Ошибка загрузки версии из кэша: {str(e)}")

            self.logger.info(f"Загружено {len(versions)} версий Minecraft из кэша")
            return versions
        except Exception as e:
            self.logger.error(f"Ошибка загрузки кэша версий Minecraft: {str(e)}")
            return []

    def _update_minecraft_versions_cache(self):
        """Обновление кэша версий Minecraft"""
        try:
            self.logger.info("Обновление кэша версий Minecraft...")

            # Используем minecraft_launcher_lib для получения версий
            versions_data = mll.utils.get_version_list()

            versions = []
            for version_info in versions_data:
                try:
                    version = MinecraftVersion(
                        id=version_info["id"],
                        type=version_info["type"],
                        url=version_info["url"],
                        time=version_info["time"],
                        release_time=version_info["releaseTime"]
                    )
                    versions.append(version)
                except Exception as e:
                    self.logger.error(f"Ошибка обработки версии {version_info.get('id', 'unknown')}: {str(e)}")

            # Сохраняем в кэш
            cache_data = {
                "updated": datetime.now().isoformat(),
                "versions": [v.to_dict() for v in versions]
            }

            with open(self.versions_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            self._minecraft_versions = versions
            self.logger.info(f"Обновлен кэш: {len(versions)} версий Minecraft")
        except Exception as e:
            self.logger.error(f"Ошибка обновления кэша версий Minecraft: {str(e)}")

    def _load_forge_versions_cache(self) -> List[LoaderVersion]:
        """Загрузка кэша версий Forge"""
        try:
            if not os.path.exists(self.forge_cache_file):
                return []

            with open(self.forge_cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            versions = []
            for version_data in data.get("versions", []):
                try:
                    versions.append(LoaderVersion.from_dict(version_data))
                except Exception as e:
                    self.logger.error(f"Ошибка загрузки версии Forge из кэша: {str(e)}")

            self.logger.info(f"Загружено {len(versions)} версий Forge из кэша")
            return versions
        except Exception as e:
            self.logger.error(f"Ошибка загрузки кэша версий Forge: {str(e)}")
            return []

    def _update_forge_versions_cache(self):
        """Обновление кэша версий Forge"""
        try:
            self.logger.info("Обновление кэша версий Forge...")

            versions = []

            # Получаем основные версии Minecraft для поиска Forge
            minecraft_versions = ["1.20.1", "1.19.4", "1.18.2", "1.17.1", "1.16.5", "1.15.2", "1.14.4", "1.12.2"]

            for mc_version in minecraft_versions:
                try:
                    forge_versions = mll.forge.find_forge_version(mc_version)
                    if forge_versions:
                        for forge_version in forge_versions:
                            version = LoaderVersion(
                                id=forge_version,
                                minecraft_version=mc_version,
                                loader_type="forge",
                                loader_version=forge_version.split('-')[-1] if '-' in forge_version else forge_version,
                                stable=True  # Предполагаем, что все версии стабильные
                            )
                            versions.append(version)
                except Exception as e:
                    self.logger.error(f"Ошибка получения версий Forge для {mc_version}: {str(e)}")

            # Сохраняем в кэш
            cache_data = {
                "updated": datetime.now().isoformat(),
                "versions": [v.to_dict() for v in versions]
            }

            with open(self.forge_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            self._forge_versions = versions
            self.logger.info(f"Обновлен кэш: {len(versions)} версий Forge")
        except Exception as e:
            self.logger.error(f"Ошибка обновления кэша версий Forge: {str(e)}")

    def _load_fabric_versions_cache(self) -> List[LoaderVersion]:
        """Загрузка кэша версий Fabric"""
        try:
            if not os.path.exists(self.fabric_cache_file):
                return []

            with open(self.fabric_cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            versions = []
            for version_data in data.get("versions", []):
                try:
                    versions.append(LoaderVersion.from_dict(version_data))
                except Exception as e:
                    self.logger.error(f"Ошибка загрузки версии Fabric из кэша: {str(e)}")

            self.logger.info(f"Загружено {len(versions)} версий Fabric из кэша")
            return versions
        except Exception as e:
            self.logger.error(f"Ошибка загрузки кэша версий Fabric: {str(e)}")
            return []

    def _update_fabric_versions_cache(self):
        """Обновление кэша версий Fabric"""
        try:
            self.logger.info("Обновление кэша версий Fabric...")

            versions = []

            # Получаем версии загрузчика Fabric
            try:
                loader_versions = mll.fabric.get_all_loader_versions()
                minecraft_versions = mll.fabric.get_all_minecraft_versions()

                # Создаем комбинации версий
                for mc_version in minecraft_versions[:10]:  # Ограничиваем количество
                    mc_version_id = mc_version["version"]

                    for loader in loader_versions[:5]:  # Берем только последние 5 версий загрузчика
                        loader_version = loader["version"]

                        version_id = f"fabric-loader-{loader_version}-{mc_version_id}"

                        version = LoaderVersion(
                            id=version_id,
                            minecraft_version=mc_version_id,
                            loader_type="fabric",
                            loader_version=loader_version,
                            stable=loader.get("stable", True)
                        )
                        versions.append(version)
            except Exception as e:
                self.logger.error(f"Ошибка получения версий Fabric через API: {str(e)}")

            # Сохраняем в кэш
            cache_data = {
                "updated": datetime.now().isoformat(),
                "versions": [v.to_dict() for v in versions]
            }

            with open(self.fabric_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            self._fabric_versions = versions
            self.logger.info(f"Обновлен кэш: {len(versions)} версий Fabric")
        except Exception as e:
            self.logger.error(f"Ошибка обновления кэша версий Fabric: {str(e)}")

    def _is_cache_expired(self, cache_file: str) -> bool:
        """Проверка, истек ли кэш"""
        try:
            if not os.path.exists(cache_file):
                return True

            # Проверяем время модификации файла
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            return datetime.now() - file_time > self.cache_lifetime
        except Exception as e:
            self.logger.error(f"Ошибка проверки времени кэша: {str(e)}")
            return True

    def _get_fallback_minecraft_versions(self) -> List[MinecraftVersion]:
        """Fallback список версий Minecraft"""
        fallback_versions = [
            {"id": "1.20.1", "type": "release"},
            {"id": "1.19.4", "type": "release"},
            {"id": "1.18.2", "type": "release"},
            {"id": "1.17.1", "type": "release"},
            {"id": "1.16.5", "type": "release"},
            {"id": "1.15.2", "type": "release"},
            {"id": "1.14.4", "type": "release"},
            {"id": "1.12.2", "type": "release"},
        ]

        versions = []
        for v in fallback_versions:
            version = MinecraftVersion(
                id=v["id"],
                type=v["type"],
                url="",
                time="",
                release_time=""
            )
            versions.append(version)

        return versions

    def _get_fallback_forge_versions(self, minecraft_version: str) -> List[LoaderVersion]:
        """Fallback список версий Forge"""
        # Предопределенные версии Forge для популярных версий Minecraft
        fallback_forge = {
            "1.20.1": ["47.2.0", "47.1.0"],
            "1.19.4": ["45.1.0", "45.0.66"],
            "1.18.2": ["40.2.0", "40.1.0"],
            "1.17.1": ["37.1.1", "37.1.0"],
            "1.16.5": ["36.2.39", "36.2.0"],
            "1.15.2": ["31.2.57", "31.2.0"],
            "1.14.4": ["28.2.26", "28.2.0"],
            "1.12.2": ["14.23.5.2859", "14.23.5.2854"],
        }

        versions = []
        if minecraft_version in fallback_forge:
            for forge_version in fallback_forge[minecraft_version]:
                version_id = f"{minecraft_version}-forge-{forge_version}"
                version = LoaderVersion(
                    id=version_id,
                    minecraft_version=minecraft_version,
                    loader_type="forge",
                    loader_version=forge_version,
                    stable=True
                )
                versions.append(version)

        return versions

    def _get_fallback_fabric_versions(self, minecraft_version: str) -> List[LoaderVersion]:
        """Fallback список версий Fabric"""
        # Предопределенные версии Fabric
        fallback_fabric = {
            "1.20.1": ["0.14.21", "0.14.20"],
            "1.19.4": ["0.14.19", "0.14.18"],
            "1.18.2": ["0.14.17", "0.14.16"],
            "1.17.1": ["0.14.15", "0.14.14"],
            "1.16.5": ["0.14.13", "0.14.12"],
        }

        versions = []
        if minecraft_version in fallback_fabric:
            for fabric_version in fallback_fabric[minecraft_version]:
                version_id = f"fabric-loader-{fabric_version}-{minecraft_version}"
                version = LoaderVersion(
                    id=version_id,
                    minecraft_version=minecraft_version,
                    loader_type="fabric",
                    loader_version=fabric_version,
                    stable=True
                )
                versions.append(version)

        return versions

    def clear_cache(self):
        """Очистка всех кэшей"""
        try:
            cache_files = [self.versions_cache_file, self.forge_cache_file, self.fabric_cache_file]

            for cache_file in cache_files:
                if os.path.exists(cache_file):
                    os.remove(cache_file)

            # Очищаем кэш в памяти
            self._minecraft_versions = None
            self._forge_versions = None
            self._fabric_versions = None

            self.logger.info("Кэш версий очищен")
        except Exception as e:
            self.logger.error(f"Ошибка очистки кэша: {str(e)}")

    def force_update_cache(self):
        """Принудительное обновление всех кэшей"""
        self.logger.info("Принудительное обновление кэша версий...")

        # Очищаем существующий кэш
        self.clear_cache()

        # Обновляем кэши
        self._update_minecraft_versions_cache()
        self._update_forge_versions_cache()
        self._update_fabric_versions_cache()

        self.logger.info("Обновление кэша завершено")

# Версионный сервис оптимизирован для проекта Юра
