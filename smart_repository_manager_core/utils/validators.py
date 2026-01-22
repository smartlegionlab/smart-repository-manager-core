# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
from typing import Optional, Tuple
from datetime import datetime
from pathlib import Path


class Validators:

    @staticmethod
    def validate_token(token: str) -> bool:
        if not token or not isinstance(token, str):
            return False
        if len(token) < 20:
            return False
        return all(c.isalnum() or c == '_' for c in token)

    @staticmethod
    def validate_username(username: str) -> bool:
        if not username or not isinstance(username, str):
            return False
        if len(username) < 1 or len(username) > 39:
            return False
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")
        return all(c in valid_chars for c in username)

    @staticmethod
    def validate_repo_name(repo_name: str) -> bool:
        if not repo_name or not isinstance(repo_name, str):
            return False
        if len(repo_name) < 1 or len(repo_name) > 100:
            return False
        if repo_name.startswith('.') or repo_name.endswith('.git'):
            return False
        return True

    @staticmethod
    def validate_path(path: Path) -> Tuple[bool, Optional[str]]:
        if not isinstance(path, Path):
            return False, "Path must be a Path object"

        try:
            parent = path.parent
            if parent.exists() and not parent.is_dir():
                return False, "Parent is not a directory"

            path_str = str(path)
            if '\0' in path_str:
                return False, "Path contains null character"

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def validate_github_date(date_str: str) -> bool:
        try:
            if date_str.endswith('Z'):
                date_str = date_str.replace('Z', '+00:00')
            datetime.fromisoformat(date_str)
            return True
        except Exception as e:
            print(e)
            return False
