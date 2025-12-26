# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
import os
import shutil
import subprocess
import signal
from pathlib import Path

from smart_repository_manager_core.core.git_commands import GitCommandResult


class GitOperation:

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.process = None

    def _terminate_process(self) -> None:
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process.wait(timeout=5)
            except Exception as e:
                print(e)
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                except Exception as e:
                    print(e)
                    pass

    def _verify_repository_health(self, repo_path: Path) -> bool:
        try:
            result1 = subprocess.run(
                ['git', '-C', str(repo_path), 'rev-parse', '--git-dir'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )

            result2 = subprocess.run(
                ['git', '-C', str(repo_path), 'log', '--oneline', '-1'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )

            return result1.returncode == 0 and result2.returncode == 0
        except Exception as e:
            print(e)
            return False

    def cancel(self) -> None:
        if self.process:
            self._terminate_process()


class GitCloneOperation(GitOperation):

    def execute(self, ssh_url: str, target_path: Path) -> GitCommandResult:
        result = GitCommandResult()

        try:
            if target_path.exists():
                shutil.rmtree(target_path)

            target_path.parent.mkdir(parents=True, exist_ok=True)

            cmd = ['git', 'clone', ssh_url, str(target_path)]

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                start_new_session=True
            )

            try:
                stdout, stderr = self.process.communicate(timeout=self.timeout)
                result.return_code = self.process.returncode
                result.output = stdout
                result.error = stderr
                result.success = self.process.returncode == 0

                if result.success:
                    result.success = self._verify_repository_health(target_path)
                    if not result.success:
                        shutil.rmtree(target_path, ignore_errors=True)

            except subprocess.TimeoutExpired:
                self._terminate_process()
                result.timed_out = True
                result.error = f"Clone timeout after {self.timeout} seconds"
                result.success = False
                if target_path.exists():
                    shutil.rmtree(target_path, ignore_errors=True)

        except Exception as e:
            result.error = f"Clone error: {str(e)}"
            result.success = False
            if target_path.exists():
                shutil.rmtree(target_path, ignore_errors=True)

        finally:
            self.process = None

        return result


class GitPullOperation(GitOperation):

    def execute(self, repo_path: Path) -> GitCommandResult:
        result = GitCommandResult()

        try:
            if not repo_path.exists():
                result.error = "Repository path does not exist"
                return result

            if not (repo_path / '.git').exists():
                result.error = "Not a git repository"
                return result

            branch_result = subprocess.run(
                ['git', '-C', str(repo_path), 'rev-parse', '--abbrev-ref', 'HEAD'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )

            branch = "master"
            if branch_result.returncode == 0:
                branch = branch_result.stdout.strip()

            cmd = ['git', '-C', str(repo_path), 'pull', 'origin', branch]

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                start_new_session=True
            )

            try:
                stdout, stderr = self.process.communicate(timeout=self.timeout)
                result.return_code = self.process.returncode
                result.output = stdout
                result.error = stderr
                result.success = self.process.returncode == 0

                if result.success:
                    result.success = self._verify_repository_health(repo_path)

            except subprocess.TimeoutExpired:
                self._terminate_process()
                result.timed_out = True
                result.error = f"Pull timeout after {self.timeout} seconds"
                result.success = False

        except Exception as e:
            result.error = f"Pull error: {str(e)}"
            result.success = False

        finally:
            self.process = None

        return result
