# Copyright (©) 2026, Alexander Suvorov. All rights reserved.
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple


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
    def needs_update_detailed(repo_path: Path, github_pushed_at: str) -> Tuple[bool, str]:
        try:
            if not repo_path.exists() or not (repo_path / '.git').exists():
                return True, "not_exists"

            local_date = GitStatusChecker.get_local_commit_date(repo_path)
            if not local_date:
                return True, "no_local_commit"

            github_date = datetime.fromisoformat(github_pushed_at.replace('Z', '+00:00'))

            if local_date.tzinfo is None:
                local_date_utc = local_date.replace(tzinfo=timezone.utc)
            else:
                local_date_utc = local_date.astimezone(timezone.utc)

            github_date_utc = github_date.replace(tzinfo=timezone.utc)

            time_diff = github_date_utc - local_date_utc
            diff_seconds = time_diff.total_seconds()

            if diff_seconds <= 300:
                return False, "up_to_date"

            remote_result = subprocess.run(
                ['git', '-C', str(repo_path), 'ls-remote', 'origin', 'HEAD'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )

            if remote_result.returncode != 0:
                err = (remote_result.stderr or '').lower()
                auth_markers = (
                    '403',
                    '401',
                    'authentication failed',
                    'permission denied',
                    'could not read',
                    'invalid username or password',
                    'repository not found',
                )
                if any(marker in err for marker in auth_markers):
                    return False, "auth_error"
                return False, f"network_error: {remote_result.stderr[:80]}"

            remote_data = remote_result.stdout.strip()
            if not remote_data:
                return False, "ls_remote_empty"

            remote_hash = remote_data.split()[0]

            local_hash_result = subprocess.run(
                ['git', '-C', str(repo_path), 'rev-parse', 'HEAD'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=3
            )

            if local_hash_result.returncode != 0:
                return False, "rev_parse_failed"

            local_hash = local_hash_result.stdout.strip()

            if local_hash != remote_hash:
                return True, "behind_remote"
            return False, "up_to_date"

        except subprocess.TimeoutExpired:
            return False, "timeout"
        except Exception as e:
            return False, f"exception: {str(e)[:80]}"

    @staticmethod
    def needs_update(repo_path: Path, github_pushed_at: str) -> bool:
        needs, _reason = GitStatusChecker.needs_update_detailed(
            repo_path, github_pushed_at
        )
        return needs

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
