# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
from datetime import datetime, timezone, timedelta
from typing import Dict, List


class Helpers:

    @staticmethod
    def format_duration(seconds: float) -> str:
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    @staticmethod
    def format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f}KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f}MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"

    @staticmethod
    def parse_github_date(date_str: str) -> datetime:
        if date_str.endswith('Z'):
            date_str = date_str.replace('Z', '+00:00')

        dt = datetime.fromisoformat(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt

    @staticmethod
    def calculate_time_difference(github_date: str, local_date: datetime) -> timedelta:
        github_dt = Helpers.parse_github_date(github_date)
        if local_date.tzinfo is not None:
            local_dt = local_date.astimezone(timezone.utc)
        else:
            local_dt = local_date.replace(tzinfo=timezone.utc)

        return github_dt - local_dt

    @staticmethod
    def deduplicate_list(items: List[Dict], key: str = 'id') -> List[Dict]:
        seen = set()
        unique = []

        for item in items:
            item_key = item.get(key)
            if item_key and item_key not in seen:
                seen.add(item_key)
                unique.append(item)

        return unique

    @staticmethod
    def get_timestamp() -> str:
        return datetime.now().isoformat()
