# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


@dataclass
class GitHubToken:
    token: str
    username: str
    created_at: str
    scopes: Optional[str] = None
    rate_limit: int = 5000
    rate_remaining: int = 5000
    rate_reset: Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def __str__(self) -> str:
        return f"GitHubToken(username={self.username}, scopes={self.scopes})"

    def update_rate_limits(self, headers: Dict[str, str]) -> None:
        self.rate_limit = int(headers.get('X-RateLimit-Limit', 5000))
        self.rate_remaining = int(headers.get('X-RateLimit-Remaining', 5000))
        self.rate_reset = headers.get('X-RateLimit-Reset')

    def to_dict(self) -> Dict:
        return {
            "token": self.token,
            "username": self.username,
            "created_at": self.created_at,
            "scopes": self.scopes
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GitHubToken':
        return cls(
            token=data.get("token", ""),
            username=data.get("username", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            scopes=data.get("scopes")
        )
