# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
from pathlib import Path
from typing import Optional

from smart_repository_manager_core.core.models.config import AppConfig
from smart_repository_manager_core.utils.file_ops import FileOperations


class ConfigService:

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            self.config_path = Path.home() / "smart_repo_manager" / "config.json"
        else:
            self.config_path = config_path

        self._config: Optional[AppConfig] = None

    def load_config(self) -> AppConfig:
        data, success = FileOperations.read_json(self.config_path)

        if success and data:
            self._config = AppConfig.from_dict(data)
        else:
            self._config = AppConfig()
            self._config.update_last_launch()
            self._save_config()

        return self._config

    def save_config(self) -> bool:
        if self._config is None:
            return False

        return self._save_config()

    def get_config(self) -> AppConfig:
        if self._config is None:
            return self.load_config()
        return self._config

    def update_last_launch(self) -> None:
        config = self.get_config()
        config.update_last_launch()
        self._save_config()

    def add_user(self, username: str, token: str) -> bool:
        config = self.get_config()
        config.add_user(username, token)
        config.set_active_user(username)
        return self._save_config()

    def remove_user(self, username: str) -> bool:
        config = self.get_config()
        config.remove_user(username)
        return self._save_config()

    def set_active_user(self, username: str) -> bool:
        config = self.get_config()
        config.set_active_user(username)
        return self._save_config()

    def get_active_user(self) -> Optional[str]:
        config = self.get_config()
        return config.active_user

    def get_user_token(self, username: str) -> Optional[str]:
        config = self.get_config()
        return config.get_user_token(username)

    def get_users_list(self) -> list:
        config = self.get_config()
        return config.get_users_list()

    def has_users(self) -> bool:
        config = self.get_config()
        return config.has_users()

    def _save_config(self) -> bool:
        if self._config is None:
            return False

        config_dict = self._config.to_dict()
        return FileOperations.write_json(self.config_path, config_dict)
