# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class GitStatusChecker:

    @staticmethod
    def get_local_commit_date(repo_path: Path) -> Optional[datetime]:
        try:
            check_result = subprocess.run(
                ['git', '-C', str(repo_path), 'rev-parse', '--verify', 'HEAD'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )

            if check_result.returncode != 0:
                return None

            cmd = ['git', '-C', str(repo_path), 'log', '-1', '--format=%cI']
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                date_line = result.stdout.strip().split('\n')[0]
                if date_line:
                    date_str_clean = date_line.replace(' +', '+').replace(' -', '-')
                    return datetime.fromisoformat(date_str_clean)
            return None
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def needs_update(repo_path: Path, github_pushed_at: str) -> bool:
        try:
            local_date = GitStatusChecker.get_local_commit_date(repo_path)
            if not local_date:
                return True

            github_date = datetime.fromisoformat(github_pushed_at.replace('Z', '+00:00'))

            local_date_utc = local_date.astimezone(timezone.utc).replace(tzinfo=None)
            github_date_utc = github_date.replace(tzinfo=None)

            time_diff = github_date_utc - local_date_utc
            return time_diff.total_seconds() > 300

        except Exception as e:
            print(e)
            return True

    @staticmethod
    def repository_exists(repo_path: Path) -> bool:
        return repo_path.exists() and (repo_path / '.git').exists()

    @staticmethod
    def get_current_branch(repo_path: Path) -> Optional[str]:
        try:
            result = subprocess.run(
                ['git', '-C', str(repo_path), 'rev-parse', '--abbrev-ref', 'HEAD'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return None
        except Exception as e:
            print(e)
            return None
