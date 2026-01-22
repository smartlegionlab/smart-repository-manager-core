# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
import stat
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from smart_repository_manager_core.utils.file_ops import FileOperations


class StructureService:

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            self.base_dir = Path.home() / "smart_repo_manager"
        else:
            self.base_dir = base_dir

    def create_user_structure(self, username: str) -> Dict[str, Path]:
        try:
            user_dir = self.base_dir / username
            user_dir.mkdir(parents=True, exist_ok=True)

            structure = {
                "user": user_dir,
                "repositories": user_dir / "repositories",
                "archives": user_dir / "archives",
                "logs": user_dir / "logs",
                "backups": user_dir / "backups",
                "temp": user_dir / "temp"
            }

            for name, path in structure.items():
                if name != "user":
                    path.mkdir(exist_ok=True)
                    self._set_permissions(path)

            self._create_readme(username, structure)
            return structure

        except Exception as e:
            print(e)
            return {}

    def get_user_structure(self, username: str) -> Dict[str, Path]:
        user_dir = self.base_dir / username

        if not user_dir.exists():
            return {}

        return {
            "user": user_dir,
            "repositories": user_dir / "repositories",
            "archives": user_dir / "archives",
            "logs": user_dir / "logs",
            "backups": user_dir / "backups",
            "temp": user_dir / "temp"
        }

    def get_repository_path(self, username: str, repo_name: str) -> Path:
        structure = self.get_user_structure(username)
        if "repositories" in structure:
            return structure["repositories"] / repo_name
        return self.base_dir / username / "repositories" / repo_name

    def cleanup_temp(self, username: str, max_age_days: int = 7) -> None:
        try:
            temp_dir = self.base_dir / username / "temp"

            if not temp_dir.exists():
                return

            now = datetime.now().timestamp()
            max_age_seconds = max_age_days * 24 * 3600

            for item in temp_dir.iterdir():
                try:
                    stat_info = item.stat()
                    age = now - stat_info.st_mtime

                    if age > max_age_seconds:
                        FileOperations.safe_remove(item)
                except Exception as e:
                    print(e)
                    continue

        except Exception as e:
            print(e)
            pass

    def get_structure_info(self, username: str) -> Dict[str, Dict]:
        structure = self.get_user_structure(username)
        info = {}

        for name, path in structure.items():
            if path.exists():
                try:
                    size = 0
                    count = 0

                    if path.is_dir():
                        for item in path.rglob('*'):
                            if item.is_file():
                                size += item.stat().st_size
                                count += 1

                    info[name] = {
                        "path": str(path),
                        "exists": True,
                        "item_count": count,
                        "size_bytes": size,
                        "size_mb": size / (1024 * 1024)
                    }
                except Exception as e:
                    print(e)
                    info[name] = {
                        "path": str(path),
                        "exists": True,
                        "item_count": 0,
                        "size_bytes": 0,
                        "size_mb": 0
                    }
            else:
                info[name] = {
                    "path": str(path),
                    "exists": False,
                    "item_count": 0,
                    "size_bytes": 0,
                    "size_mb": 0
                }

        return info

    def ensure_user_dir(self, username: str) -> bool:
        try:
            user_dir = self.base_dir / username
            user_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(e)
            return False

    def _set_permissions(self, path: Path) -> None:
        try:
            os.chmod(path, stat.S_IRWXU)
        except Exception as e:
            print(e)
            pass

    def _create_readme(self, username: str, structure: Dict[str, Path]) -> None:
        try:
            readme_path = structure["user"] / "README.md"

            if not readme_path.exists():
                content = f"""# Git Repositories - {username}

Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
User: {username}

## Directory Structure
{username}/
├── repositories/ # Local clones of Git repositories
├── archives/    # Backup archives and snapshots
├── logs/        # Operation logs
├── backups/     # Manual backups
└── temp/        # Temporary files (auto-cleaned)

## Managed by Smart Repository Manager
"""

                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                os.chmod(readme_path, stat.S_IRUSR | stat.S_IWUSR)

        except Exception as e:
            print(e)
            pass
