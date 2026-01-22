# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class User:
    username: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    html_url: Optional[str] = None
    bio: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    token: Optional[str] = None

    def __str__(self) -> str:
        return f"User(username={self.username}, repos={self.public_repos})"

    @property
    def created_date(self) -> str:
        if not self.created_at:
            return "Unknown"
        try:
            dt = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d")
        except Exception as e:
            print(e)
            return "Invalid date"

    def update_from_api(self, api_data: Dict[str, Any]) -> None:
        self.name = api_data.get("name")
        self.avatar_url = api_data.get("avatar_url")
        self.html_url = api_data.get("html_url")
        self.bio = api_data.get("bio")
        self.public_repos = api_data.get("public_repos", 0)
        self.followers = api_data.get("followers", 0)
        self.following = api_data.get("following", 0)
        self.created_at = api_data.get("created_at")

    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "name": self.name,
            "avatar_url": self.avatar_url,
            "html_url": self.html_url,
            "bio": self.bio,
            "public_repos": self.public_repos,
            "followers": self.followers,
            "following": self.following,
            "created_at": self.created_at,
            "scopes": self.scopes
        }

    @classmethod
    def from_dict(cls, data: Dict, token: str = None) -> 'User':
        user = cls(
            username=data.get("username", ""),
            name=data.get("name"),
            avatar_url=data.get("avatar_url"),
            html_url=data.get("html_url"),
            bio=data.get("bio"),
            public_repos=data.get("public_repos", 0),
            followers=data.get("followers", 0),
            following=data.get("following", 0),
            created_at=data.get("created_at"),
            scopes=data.get("scopes", []),
            token=token
        )
        return user
