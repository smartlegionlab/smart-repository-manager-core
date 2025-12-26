# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime


class StorageService:

    def __init__(self, base_path: Optional[Path] = None):
        if base_path is None:
            self.base_path = Path.cwd()
        else:
            self.base_path = base_path

        self._ensure_base_path()

    def _ensure_base_path(self) -> bool:
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(e)
            return False

    def save_json(self, filename: str, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        try:
            file_path = self.base_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            temp_path = file_path.with_suffix('.tmp')

            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            shutil.move(temp_path, file_path)
            return True, None

        except Exception as e:
            return False, f"Error saving JSON: {str(e)}"

    def load_json(self, filename: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            file_path = self.base_path / filename

            if not file_path.exists():
                return None, "File does not exist"

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return data, None

        except json.JSONDecodeError as e:
            return None, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return None, f"Error loading JSON: {str(e)}"

    def file_exists(self, filename: str) -> bool:
        file_path = self.base_path / filename
        return file_path.exists()

    def directory_exists(self, directory: str) -> bool:
        dir_path = self.base_path / directory
        return dir_path.exists() and dir_path.is_dir()

    def create_directory(self, directory: str) -> Tuple[bool, Optional[str]]:
        try:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            return True, None
        except Exception as e:
            return False, f"Error creating directory: {str(e)}"

    def list_files(self, directory: str = "", pattern: str = "*") -> Tuple[List[str], Optional[str]]:
        try:
            dir_path = self.base_path / directory

            if not dir_path.exists():
                return [], f"Directory does not exist: {directory}"

            files = [f.name for f in dir_path.glob(pattern) if f.is_file()]
            return files, None

        except Exception as e:
            return [], f"Error listing files: {str(e)}"

    def list_directories(self, directory: str = "") -> Tuple[List[str], Optional[str]]:
        try:
            dir_path = self.base_path / directory

            if not dir_path.exists():
                return [], f"Directory does not exist: {directory}"

            directories = [d.name for d in dir_path.iterdir() if d.is_dir()]
            return directories, None

        except Exception as e:
            return [], f"Error listing directories: {str(e)}"

    def delete_file(self, filename: str) -> Tuple[bool, Optional[str]]:
        try:
            file_path = self.base_path / filename

            if not file_path.exists():
                return False, "File does not exist"

            if file_path.is_dir():
                return False, "Path is a directory, not a file"

            file_path.unlink()
            return True, None

        except Exception as e:
            return False, f"Error deleting file: {str(e)}"

    def delete_directory(self, directory: str, recursive: bool = False) -> Tuple[bool, Optional[str]]:
        try:
            dir_path = self.base_path / directory

            if not dir_path.exists():
                return False, "Directory does not exist"

            if not dir_path.is_dir():
                return False, "Path is not a directory"

            if recursive:
                shutil.rmtree(dir_path)
            else:
                dir_path.rmdir()

            return True, None

        except Exception as e:
            return False, f"Error deleting directory: {str(e)}"

    def get_file_size(self, filename: str) -> Tuple[Optional[int], Optional[str]]:
        try:
            file_path = self.base_path / filename

            if not file_path.exists():
                return None, "File does not exist"

            if file_path.is_dir():
                return None, "Path is a directory, not a file"

            return file_path.stat().st_size, None

        except Exception as e:
            return None, f"Error getting file size: {str(e)}"

    def get_file_modified_time(self, filename: str) -> Tuple[Optional[datetime], Optional[str]]:
        try:
            file_path = self.base_path / filename

            if not file_path.exists():
                return None, "File does not exist"

            if file_path.is_dir():
                return None, "Path is a directory, not a file"

            mtime = file_path.stat().st_mtime
            return datetime.fromtimestamp(mtime), None

        except Exception as e:
            return None, f"Error getting file modified time: {str(e)}"

    def copy_file(self, source: str, destination: str) -> Tuple[bool, Optional[str]]:
        try:
            source_path = self.base_path / source
            dest_path = self.base_path / destination

            if not source_path.exists():
                return False, "Source file does not exist"

            if source_path.is_dir():
                return False, "Source is a directory, not a file"

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)

            return True, None

        except Exception as e:
            return False, f"Error copying file: {str(e)}"

    def move_file(self, source: str, destination: str) -> Tuple[bool, Optional[str]]:
        try:
            source_path = self.base_path / source
            dest_path = self.base_path / destination

            if not source_path.exists():
                return False, "Source file does not exist"

            if source_path.is_dir():
                return False, "Source is a directory, not a file"

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(source_path, dest_path)

            return True, None

        except Exception as e:
            return False, f"Error moving file: {str(e)}"

    def get_file_info(self, filename: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            file_path = self.base_path / filename

            if not file_path.exists():
                return None, "File does not exist"

            stat_info = file_path.stat()

            info = {
                "filename": filename,
                "path": str(file_path),
                "exists": True,
                "is_file": file_path.is_file(),
                "is_dir": file_path.is_dir(),
                "size_bytes": stat_info.st_size,
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat()
            }

            return info, None

        except Exception as e:
            return None, f"Error getting file info: {str(e)}"

    def cleanup_old_files(self, directory: str, max_age_days: int = 7) -> Tuple[int, Optional[str]]:
        try:
            dir_path = self.base_path / directory

            if not dir_path.exists():
                return 0, f"Directory does not exist: {directory}"

            now = datetime.now().timestamp()
            max_age_seconds = max_age_days * 24 * 3600
            deleted_count = 0

            for item in dir_path.iterdir():
                try:
                    if item.is_file():
                        age = now - item.stat().st_mtime

                        if age > max_age_seconds:
                            item.unlink()
                            deleted_count += 1
                except Exception as e:
                    print(e)
                    continue

            return deleted_count, None

        except Exception as e:
            return 0, f"Error cleaning up old files: {str(e)}"

    def ensure_file_structure(self, structure: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        try:
            for key, value in structure.items():
                if isinstance(value, dict):
                    success, error = self.create_directory(key)
                    if not success:
                        return False, f"Failed to create directory {key}: {error}"

                    sub_structure = {f"{key}/{sub_key}": sub_value for sub_key, sub_value in value.items()}
                    success, error = self.ensure_file_structure(sub_structure)
                    if not success:
                        return False, error
                else:
                    if isinstance(value, (dict, list)):
                        success, error = self.save_json(key, value)
                        if not success:
                            return False, f"Failed to create file {key}: {error}"
                    else:
                        file_path = self.base_path / key
                        file_path.parent.mkdir(parents=True, exist_ok=True)

                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(str(value))

            return True, None

        except Exception as e:
            return False, f"Error ensuring file structure: {str(e)}"
