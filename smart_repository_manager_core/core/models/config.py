# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class AppConfig:
    app_name: str = "Smart Repository Manager"
    version: str = "1.0.0"
    last_launch: Optional[str] = None
    active_user: Optional[str] = None
    users: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if self.last_launch is None:
            self.last_launch = datetime.now().isoformat()

    def set_version(self, version: str = "1.0.0"):
        self.version = str(version)

    def add_user(self, username: str, token: str) -> None:
        self.users[username] = token

    def remove_user(self, username: str) -> None:
        if username in self.users:
            del self.users[username]
        if self.active_user == username:
            self.active_user = None

    def set_active_user(self, username: str) -> None:
        if username in self.users:
            self.active_user = username

    def get_user_token(self, username: str) -> Optional[str]:
        return self.users.get(username)

    def has_users(self) -> bool:
        return len(self.users) > 0

    def get_users_list(self) -> List[str]:
        return list(self.users.keys())

    def update_last_launch(self) -> None:
        self.last_launch = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "app_name": self.app_name,
            "version": self.version,
            "last_launch": self.last_launch,
            "active_user": self.active_user,
            "users": self.users
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AppConfig':
        return cls(
            app_name=data.get("app_name", "Smart Repository Manager"),
            version=data.get("version", "1.0.0"),
            last_launch=data.get("last_launch"),
            active_user=data.get("active_user"),
            users=data.get("users", {})
        )
