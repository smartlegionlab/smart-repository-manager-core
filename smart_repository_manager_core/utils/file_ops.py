# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


class FileOperations:

    @staticmethod
    def ensure_dir(path: Path) -> bool:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def read_json(path: Path) -> Tuple[Optional[Dict], bool]:
        try:
            if not path.exists():
                return None, False
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data, True
        except Exception as e:
            print(e)
            return None, False

    @staticmethod
    def write_json(path: Path, data: Dict[str, Any]) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_suffix('.tmp')
            with open(temp, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            shutil.move(temp, path)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def safe_remove(path: Path) -> bool:
        try:
            if path.exists():
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def copy_file(source: Path, destination: Path) -> bool:
        try:
            shutil.copy2(source, destination)
            return True
        except Exception as e:
            print(e)
            return False
