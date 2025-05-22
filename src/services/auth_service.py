import uuid
import hashlib
import json
import os
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from random_username.generate import generate_username

from core.logger import Logger
from core.paths import Paths


@dataclass
class MinecraftAccount:
    """Класс для представления аккаунта Minecraft"""
    username: str
    uuid: str
    access_token: str = ""
    refresh_token: str = ""
    account_type: str = "offline"  # "offline", "mojang", "microsoft"
    skin_url: Optional[str] = None

    def to_dict(self) -> Dict:
        """Преобразование в словарь для сериализации"""
        return {
            "username": self.username,
            "uuid": self.uuid,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "account_type": self.account_type,
            "skin_url": self.skin_url
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MinecraftAccount':
        """Создание из словаря"""
        return cls(**data)


class AuthService:
    """Сервис для управления аутентификацией Minecraft"""

    def __init__(self):
        self.logger = Logger().get_logger()
        self.paths = Paths()
        self.accounts_file = os.path.join(self.paths.config_dir, "accounts.json")
        self.current_account = None

        # Загружаем сохраненные аккаунты
        self.accounts = self._load_accounts()

        # Устанавливаем аккаунт по умолчанию
        if not self.accounts:
            self._create_default_account()

    def _load_accounts(self) -> Dict[str, MinecraftAccount]:
        """Загрузка сохраненных аккаунтов"""
        try:
            if not os.path.exists(self.accounts_file):
                return {}

            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            accounts = {}
            for account_id, account_data in data.items():
                try:
                    accounts[account_id] = MinecraftAccount.from_dict(account_data)
                except Exception as e:
                    self.logger.error(f"Ошибка загрузки аккаунта {account_id}: {str(e)}")

            self.logger.info(f"Загружено {len(accounts)} аккаунтов")
            return accounts
        except Exception as e:
            self.logger.error(f"Ошибка загрузки аккаунтов: {str(e)}")
            return {}

    def _save_accounts(self) -> bool:
        """Сохранение аккаунтов"""
        try:
            os.makedirs(os.path.dirname(self.accounts_file), exist_ok=True)

            data = {}
            for account_id, account in self.accounts.items():
                data[account_id] = account.to_dict()

            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.info("Аккаунты сохранены")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка сохранения аккаунтов: {str(e)}")
            return False

    def _create_default_account(self):
        """Создание аккаунта по умолчанию"""
        try:
            # Генерируем случайное имя пользователя
            username = generate_username()[0]

            # Создаем аккаунт
            account = self.create_offline_account(username)
            if account:
                self.current_account = account
                self.logger.info(f"Создан аккаунт по умолчанию: {username}")
        except Exception as e:
            self.logger.error(f"Ошибка создания аккаунта по умолчанию: {str(e)}")

            # Fallback - создаем аккаунт с простым именем
            account = self.create_offline_account("Player")
            if account:
                self.current_account = account

    def create_offline_account(self, username: str) -> Optional[MinecraftAccount]:
        """Создание оффлайн аккаунта"""
        try:
            # Проверяем валидность имени пользователя
            if not self._is_valid_username(username):
                self.logger.error(f"Невалидное имя пользователя: {username}")
                return None

            # Генерируем UUID для оффлайн аккаунта
            offline_uuid = self._generate_offline_uuid(username)

            # Создаем аккаунт
            account = MinecraftAccount(
                username=username,
                uuid=offline_uuid,
                account_type="offline"
            )

            # Сохраняем аккаунт
            account_id = f"offline_{username.lower()}"
            self.accounts[account_id] = account
            self._save_accounts()

            self.logger.info(f"Создан оффлайн аккаунт: {username} ({offline_uuid})")
            return account
        except Exception as e:
            self.logger.error(f"Ошибка создания оффлайн аккаунта: {str(e)}")
            return None

    def _generate_offline_uuid(self, username: str) -> str:
        """Генерация UUID для оффлайн аккаунта"""
        # Используем MD5 хеш от имени пользователя для генерации стабильного UUID
        namespace = "OfflinePlayer:"
        hash_input = namespace + username

        md5_hash = hashlib.md5(hash_input.encode('utf-8')).hexdigest()

        # Форматируем как UUID
        uuid_str = f"{md5_hash[:8]}-{md5_hash[8:12]}-{md5_hash[12:16]}-{md5_hash[16:20]}-{md5_hash[20:32]}"

        return uuid_str

    def _is_valid_username(self, username: str) -> bool:
        """Проверка валидности имени пользователя Minecraft"""
        if not username:
            return False

        # Проверяем длину (3-16 символов)
        if len(username) < 3 or len(username) > 16:
            return False

        # Проверяем символы (только буквы, цифры и подчеркивания)
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False

        return True

    def get_current_account(self) -> Optional[MinecraftAccount]:
        """Получение текущего активного аккаунта"""
        return self.current_account

    def set_current_account(self, account_id: str) -> bool:
        """Установка текущего активного аккаунта"""
        if account_id in self.accounts:
            self.current_account = self.accounts[account_id]
            self.logger.info(f"Установлен активный аккаунт: {self.current_account.username}")
            return True

        self.logger.error(f"Аккаунт не найден: {account_id}")
        return False

    def get_all_accounts(self) -> Dict[str, MinecraftAccount]:
        """Получение всех аккаунтов"""
        return self.accounts.copy()

    def remove_account(self, account_id: str) -> bool:
        """Удаление аккаунта"""
        if account_id not in self.accounts:
            self.logger.error(f"Аккаунт для удаления не найден: {account_id}")
            return False

        # Проверяем, не является ли это текущим аккаунтом
        if self.current_account and self.accounts[account_id] == self.current_account:
            # Если это единственный аккаунт, создаем новый по умолчанию
            if len(self.accounts) == 1:
                self._create_default_account()
            else:
                # Выбираем первый доступный аккаунт
                for other_id, other_account in self.accounts.items():
                    if other_id != account_id:
                        self.current_account = other_account
                        break

        # Удаляем аккаунт
        removed_account = self.accounts.pop(account_id)
        self._save_accounts()

        self.logger.info(f"Удален аккаунт: {removed_account.username}")
        return True

    def authenticate_mojang(self, email: str, password: str) -> Optional[MinecraftAccount]:
        """Аутентификация через Mojang (заглушка)"""
        # Эта функция пока не реализована, поскольку Mojang API устарел
        # В будущих версиях может быть добавлена поддержка Microsoft аутентификации
        self.logger.warning("Mojang аутентификация пока не поддерживается")
        return None

    def authenticate_microsoft(self) -> Optional[MinecraftAccount]:
        """Аутентификация через Microsoft (заглушка)"""
        # Эта функция требует сложной OAuth2 интеграции с Microsoft
        # В будущих версиях может быть добавлена
        self.logger.warning("Microsoft аутентификация пока не поддерживается")
        return None

    def refresh_account_token(self, account_id: str) -> bool:
        """Обновление токена аккаунта (заглушка)"""
        # Для оффлайн аккаунтов обновление токенов не требуется
        if account_id in self.accounts:
            account = self.accounts[account_id]
            if account.account_type == "offline":
                return True

        # Для онлайн аккаунтов требуется API интеграция
        self.logger.warning("Обновление токенов пока не поддерживается")
        return False

    def validate_account(self, account_id: str) -> bool:
        """Проверка валидности аккаунта"""
        if account_id not in self.accounts:
            return False

        account = self.accounts[account_id]

        # Для оффлайн аккаунтов всегда валидны
        if account.account_type == "offline":
            return True

        # Для онлайн аккаунтов нужна проверка токенов
        # Пока возвращаем True, в будущем добавим проверку
        return True

    def get_account_for_launch(self, account_id: Optional[str] = None) -> Tuple[str, str, str]:
        """Получение данных аккаунта для запуска игры

        Returns:
            Tuple[username, uuid, access_token]
        """
        if account_id and account_id in self.accounts:
            account = self.accounts[account_id]
        elif self.current_account:
            account = self.current_account
        else:
            # Создаем временный аккаунт
            temp_username = generate_username()[0]
            temp_uuid = self._generate_offline_uuid(temp_username)
            return temp_username, temp_uuid, ""

        return account.username, account.uuid, account.access_token

    def edit_account_username(self, account_id: str, new_username: str) -> bool:
        """Изменение имени пользователя оффлайн аккаунта"""
        if account_id not in self.accounts:
            self.logger.error(f"Аккаунт не найден: {account_id}")
            return False

        account = self.accounts[account_id]

        # Можно изменять только оффлайн аккаунты
        if account.account_type != "offline":
            self.logger.error("Можно изменять только оффлайн аккаунты")
            return False

        # Проверяем валидность нового имени
        if not self._is_valid_username(new_username):
            self.logger.error(f"Невалидное имя пользователя: {new_username}")
            return False

        # Обновляем аккаунт
        old_username = account.username
        account.username = new_username
        account.uuid = self._generate_offline_uuid(new_username)

        # Обновляем ключ в словаре аккаунтов
        del self.accounts[account_id]
        new_account_id = f"offline_{new_username.lower()}"
        self.accounts[new_account_id] = account

        # Сохраняем изменения
        self._save_accounts()

        self.logger.info(f"Изменено имя аккаунта: {old_username} -> {new_username}")
        return True

# Сервис аутентификации безопасно создан для Юра
