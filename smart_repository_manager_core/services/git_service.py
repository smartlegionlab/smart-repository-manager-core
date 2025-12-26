# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict

from smart_repository_manager_core.core.git_commands import GitCommandResult, GitOperationStatus
from smart_repository_manager_core.core.git_operations import GitCloneOperation, GitPullOperation
from smart_repository_manager_core.core.git_status import GitStatusChecker
from smart_repository_manager_core.core.models.repository import Repository
from smart_repository_manager_core.utils.validators import Validators


class GitService:

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def clone_repository(self, ssh_url: str, target_path: Path) -> GitCommandResult:
        if not Validators.validate_path(target_path)[0]:
            return GitCommandResult(
                success=False,
                error="Invalid target path"
            )

        operation = GitCloneOperation(timeout=self.timeout)
        return operation.execute(ssh_url, target_path)

    def pull_repository(self, repo_path: Path) -> GitCommandResult:
        if not repo_path.exists() or not (repo_path / '.git').exists():
            return GitCommandResult(
                success=False,
                error="Not a git repository"
            )

        operation = GitPullOperation(timeout=self.timeout)
        return operation.execute(repo_path)

    def check_repository_status(self, repo: Repository, repo_path: Path) -> GitOperationStatus:
        status = GitOperationStatus(
            operation="status",
            repo_name=repo.name
        )

        if not repo_path.exists() or not (repo_path / '.git').exists():
            status.message = "Repository not found locally"
            status.success = False
            return status

        try:
            check_result = subprocess.run(
                ['git', '-C', str(repo_path), 'rev-parse', '--git-dir'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )

            if check_result.returncode != 0:
                status.message = "Repository corrupted"
                status.success = False
                return status

            if repo.pushed_at:
                needs_update = GitStatusChecker.needs_update(repo_path, repo.pushed_at)
                if needs_update:
                    status.message = "Needs update"
                else:
                    status.message = "Up to date"
            else:
                status.message = "Unknown remote status"

            status.success = True
            return status

        except Exception as e:
            print(e)
            status.message = "Status check failed"
            status.success = False
            return status

    def get_repository_info(self, repo_path: Path) -> Optional[Dict]:
        if not repo_path.exists() or not (repo_path / '.git').exists():
            return None

        try:
            info = {}

            branch_result = subprocess.run(
                ['git', '-C', str(repo_path), 'rev-parse', '--abbrev-ref', 'HEAD'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )

            if branch_result.returncode == 0:
                info['branch'] = branch_result.stdout.strip()

            date_result = subprocess.run(
                ['git', '-C', str(repo_path), 'log', '-1', '--format=%cI'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )

            if date_result.returncode == 0 and date_result.stdout.strip():
                info['last_commit'] = date_result.stdout.strip()

            count_result = subprocess.run(
                ['git', '-C', str(repo_path), 'rev-list', '--count', 'HEAD'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )

            if count_result.returncode == 0:
                info['commit_count'] = int(count_result.stdout.strip())

            remote_result = subprocess.run(
                ['git', '-C', str(repo_path), 'remote', 'get-url', 'origin'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )

            if remote_result.returncode == 0:
                info['remote_url'] = remote_result.stdout.strip()

            return info

        except Exception as e:
            print(e)
            return None

    def cleanup_repository(self, repo_path: Path) -> bool:
        try:
            if repo_path.exists():
                shutil.rmtree(repo_path, ignore_errors=True)
                return True
            return True
        except Exception as e:
            print(e)
            return False

    def verify_repository(self, repo_path: Path) -> bool:
        return GitStatusChecker.repository_exists(repo_path)
