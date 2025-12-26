# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
import subprocess
import os
import stat
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime

from smart_repository_manager_core.core.models.ssh_models import (
    SSHValidationResult,
    SSHStatus,
    SSHConfig,
    SSHKeyType,
    SSHKey
)


class SSHService:

    def __init__(self, ssh_dir: Optional[Path] = None):
        self.ssh_dir = ssh_dir or Path.home() / ".ssh"
        self.config_file = self.ssh_dir / "config"
        self.known_hosts_file = self.ssh_dir / "known_hosts"
        self.github_host = "github.com"

    def validate_ssh_configuration(self) -> SSHValidationResult:
        try:
            ssh_config = self._collect_ssh_info()
            errors = []
            warnings = []
            recommendations = []
            test_results = {"ssh_dir_exists": self.ssh_dir.exists()}

            if not test_results["ssh_dir_exists"]:
                errors.append(f"SSH directory does not exist: {self.ssh_dir}")
                recommendations.append(f"Create a directory: mkdir -p {self.ssh_dir}")
                recommendations.append("Generate an SSH key: ssh-keygen -t ed25519 -C 'your_email@example.com'")

            if self.ssh_dir.exists():
                test_results["ssh_dir_permissions_valid"] = self._check_dir_permissions(self.ssh_dir)
                if not test_results["ssh_dir_permissions_valid"]:
                    errors.append(f"Incorrect access rights {self.ssh_dir}")
                    recommendations.append(f"Correct permissions: chmod 700 {self.ssh_dir}")

            test_results["has_ssh_keys"] = bool(ssh_config.keys)
            if not test_results["has_ssh_keys"]:
                errors.append("SSH keys not found")
                recommendations.append(
                    "Generate an SSH key with the command: ssh-keygen -t ed25519 -C 'your_email@example.com'")

            for key in ssh_config.keys:
                key_valid = self._validate_key_permissions(key.private_path)
                test_results[f"key_perms_valid_{key.type.value}"] = key_valid
                if not key_valid:
                    errors.append(f"Incorrect key permissions: {key.private_path}")
                    recommendations.append(f"Correct permissions: chmod 600 {key.private_path}")

            test_results["has_ssh_config"] = self.config_file.exists()

            if not test_results["has_ssh_config"]:
                warnings.append(f"SSH config is missing: {self.config_file}")
                recommendations.append(f"Create a config: touch {self.config_file}")

                if not test_results["has_ssh_keys"]:
                    recommendations.append("First, generate an SSH key.")

            if self.config_file.exists():
                try:
                    config_content = self.config_file.read_text()
                    test_results["has_github_in_config"] = self.github_host in config_content.lower()

                    if not test_results["has_github_in_config"]:
                        warnings.append(f"GitHub is not configured in {self.config_file}")
                        recommendations.append("Add GitHub to your SSH configuration")
                except Exception as e:
                    test_results["has_github_in_config"] = False
                    warnings.append(f"Failed to read SSH config: {e}")

            test_results["has_known_hosts"] = self.known_hosts_file.exists()
            if self.known_hosts_file.exists():
                known_hosts_content = self.known_hosts_file.read_text()
                test_results["has_github_in_known_hosts"] = self.github_host in known_hosts_content
                ssh_config.has_github_in_known_hosts = test_results["has_github_in_known_hosts"]

                if not test_results["has_github_in_known_hosts"]:
                    warnings.append("GitHub is not added to known_hosts")
                    recommendations.append("Add GitHub: ssh-keyscan github.com >> ~/.ssh/known_hosts")

            test_results["github_auth_working"] = self._test_github_authentication()
            ssh_config.has_valid_config = test_results["github_auth_working"]

            test_results["git_config_valid"] = self._check_git_config()

            if errors:
                status = SSHStatus.ERROR
            elif warnings or not test_results["github_auth_working"]:
                status = SSHStatus.PARTIAL
            elif test_results["github_auth_working"] and test_results["has_ssh_keys"]:
                status = SSHStatus.VALID
            else:
                status = SSHStatus.NOT_CONFIGURED

            can_clone_with_ssh = (test_results["github_auth_working"] or
                                  (test_results["has_ssh_keys"] and not errors))
            can_pull_with_ssh = test_results["github_auth_working"]

            result = SSHValidationResult(
                status=status,
                ssh_config=ssh_config,
                errors=errors,
                warnings=warnings,
                recommendations=recommendations,
                test_results=test_results,
                can_clone_with_ssh=can_clone_with_ssh,
                can_pull_with_ssh=can_pull_with_ssh,
                github_authentication_working=test_results.get("github_auth_working", False)
            )

            return result

        except Exception as e:
            ssh_config = SSHConfig(
                ssh_dir=self.ssh_dir,
                config_file=self.config_file,
                known_hosts_file=self.known_hosts_file
            )

            return SSHValidationResult(
                status=SSHStatus.ERROR,
                ssh_config=ssh_config,
                errors=[f"SSH verification error: {str(e)}"],
                warnings=[],
                recommendations=["Check SSH configuration manually"],
                test_results={},
                can_clone_with_ssh=False,
                can_pull_with_ssh=False,
                github_authentication_working=False
            )

    def _collect_ssh_info(self) -> SSHConfig:
        ssh_config = SSHConfig(
            ssh_dir=self.ssh_dir,
            config_file=self.config_file,
            known_hosts_file=self.known_hosts_file
        )

        if not self.ssh_dir.exists():
            return ssh_config

        key_patterns = [
            ("id_rsa", SSHKeyType.RSA),
            ("id_ed25519", SSHKeyType.ED25519),
            ("id_ecdsa", SSHKeyType.ECDSA),
            ("id_dsa", SSHKeyType.DSA),
        ]

        for key_prefix, key_type in key_patterns:
            private_key = self.ssh_dir / key_prefix
            public_key = self.ssh_dir / f"{key_prefix}.pub"

            if private_key.exists():
                ssh_key = SSHKey(
                    type=key_type,
                    private_path=private_key,
                    public_path=public_key if public_key.exists() else None
                )

                self._enrich_key_info(ssh_key)
                ssh_config.keys.append(ssh_key)

        return ssh_config

    def _enrich_key_info(self, key: SSHKey) -> None:
        try:
            if key.public_path and key.public_path.exists():
                result = subprocess.run(
                    ['ssh-keygen', '-l', '-f', str(key.public_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    parts = result.stdout.strip().split()
                    if len(parts) >= 4:
                        key.fingerprint = parts[1]
                        key.size = int(parts[0]) if parts[0].isdigit() else None
                        key.comment = ' '.join(parts[3:]) if len(parts) > 3 else None

            if key.private_path.exists():
                content = key.private_path.read_text()
                key.is_encrypted = "ENCRYPTED" in content

            key.is_github_authenticated = self._test_key_with_github(key)

        except Exception as e:
            print(e)
            pass

    def _test_key_with_github(self, key: SSHKey) -> bool:
        try:
            result = subprocess.run(
                ['ssh', '-i', str(key.private_path),
                 '-o', 'BatchMode=yes',
                 '-o', 'ConnectTimeout=10',
                 '-T', f'git@{self.github_host}'],
                capture_output=True,
                text=True,
                timeout=15
            )

            output = result.stderr.lower() + result.stdout.lower()
            return any(phrase in output for phrase in [
                "successfully authenticated",
                "you've successfully authenticated"
            ])

        except Exception as e:
            print(e)
            return False

    def _test_github_authentication(self) -> bool:
        try:
            result = subprocess.run(
                ['ssh', '-T', f'git@{self.github_host}'],
                capture_output=True,
                text=True,
                timeout=15
            )

            output = result.stderr.lower() + result.stdout.lower()
            return any(phrase in output for phrase in [
                "successfully authenticated",
                "you've successfully authenticated"
            ])

        except Exception as e:
            print(e)
            return False

    def _check_dir_permissions(self, path: Path) -> bool:
        try:
            mode = path.stat().st_mode
            return stat.S_IMODE(mode) == 0o700
        except Exception as e:
            print(e)
            return False

    def _validate_key_permissions(self, key_path: Path) -> bool:
        try:
            if not key_path.exists():
                return False

            mode = key_path.stat().st_mode
            perms = stat.S_IMODE(mode)
            return perms in [0o600, 0o400]
        except Exception as e:
            print(e)
            return False

    def _check_git_config(self) -> bool:
        try:
            result_name = subprocess.run(
                ['git', 'config', '--global', 'user.name'],
                capture_output=True,
                text=True
            )

            result_email = subprocess.run(
                ['git', 'config', '--global', 'user.email'],
                capture_output=True,
                text=True
            )

            return (result_name.returncode == 0 and result_name.stdout.strip() and
                    result_email.returncode == 0 and result_email.stdout.strip())

        except Exception as e:
            print(e)
            return False

    def generate_ssh_key(self,
                         key_type: SSHKeyType = SSHKeyType.ED25519,
                         email: Optional[str] = None,
                         key_name: Optional[str] = None) -> Tuple[bool, str, Optional[Path]]:
        try:
            if not self.ssh_dir.exists():
                self.ssh_dir.mkdir(mode=0o700, parents=True)

            if key_name:
                private_key_name = key_name
            else:
                private_key_name = f"id_{key_type.value}"

            key_path = self.ssh_dir / private_key_name

            if key_path.exists():
                return False, f"The key already exists: {key_path}", None

            email_param = email or f"{os.getlogin()}@{os.uname().nodename}"

            cmd = [
                'ssh-keygen',
                '-t', key_type.value,
                '-C', email_param,
                '-f', str(key_path),
                '-N', '',
                '-q'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                key_path.chmod(0o600)

                pub_key_path = key_path.with_suffix('.pub')
                if pub_key_path.exists():
                    pub_key_path.chmod(0o644)
                    public_key = pub_key_path.read_text().strip()
                    return True, "SSH key generated successfully", pub_key_path
                else:
                    return True, "SSH key generated, but public key not found", None
            else:
                return False, f"Generation error: {result.stderr}", None

        except Exception as e:
            return False, f"Error: {str(e)}", None

    def add_github_to_known_hosts(self) -> Tuple[bool, str]:
        try:
            cmd = ['ssh-keyscan', self.github_host]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                self.known_hosts_file.parent.mkdir(parents=True, exist_ok=True)
                if not self.known_hosts_file.exists():
                    self.known_hosts_file.touch()
                    self.known_hosts_file.chmod(0o644)

                with open(self.known_hosts_file, 'a') as f:
                    f.write('\n' + result.stdout.strip())

                return True, "GitHub added to known_hosts"
            else:
                return False, "Failed to get GitHub keys"

        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    def create_ssh_config(self, github_key_path: Optional[Path] = None) -> Tuple[bool, str]:
        try:
            if self.config_file.exists():
                return True, f"SSH config already exists: {self.config_file}"

            if not github_key_path:
                ssh_config = self._collect_ssh_info()
                if ssh_config.keys:
                    github_key_path = ssh_config.keys[0].private_path
                else:
                    success, message, key_path = self.generate_ssh_key()
                    if success and key_path:
                        github_key_path = key_path.with_suffix('')
                    else:
                        return False, "There are no SSH keys and it was not possible to generate a new one."

            config_content = f"""# Smart Repository Manager - GitHub Configuration
# Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Host github.com
    HostName github.com
    User git
    IdentityFile {github_key_path}
    IdentitiesOnly yes
    AddKeysToAgent yes
    PreferredAuthentications publickey
    TCPKeepAlive yes
    ServerAliveInterval 60
    ServerAliveCountMax 5
    ConnectTimeout 30
    LogLevel ERROR
"""

            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            self.config_file.write_text(config_content)

            self.config_file.chmod(0o600)

            return True, f"SSH config created: {self.config_file}"

        except Exception as e:
            return False, f"Error creating SSH config: {str(e)}"

    def fix_permissions(self) -> Tuple[bool, str]:
        try:
            if not self.ssh_dir.exists():
                return False, "SSH directory does not exist"

            self.ssh_dir.chmod(0o700)

            for item in self.ssh_dir.iterdir():
                if item.is_file():
                    if item.name.endswith('.pub'):
                        item.chmod(0o644)
                    else:
                        if item.name.startswith('id_') and not item.name.endswith('.pub'):
                            item.chmod(0o600)
                        else:
                            item.chmod(0o644)

            if self.known_hosts_file.exists():
                self.known_hosts_file.chmod(0o644)

            if self.config_file.exists():
                self.config_file.chmod(0o600)

            return True, "Access rights have been corrected"

        except Exception as e:
            return False, f"Error correcting rights: {str(e)}"

    def get_public_keys(self) -> List[Dict[str, str]]:
        keys = []
        ssh_config = self._collect_ssh_info()

        for key in ssh_config.keys:
            if key.public_path and key.public_path.exists():
                try:
                    content = key.public_path.read_text().strip()
                    keys.append({
                        'type': key.type.value,
                        'path': str(key.public_path),
                        'content': content,
                        'fingerprint': key.fingerprint,
                        'github_working': key.is_github_authenticated
                    })
                except Exception as e:
                    print(e)
                    continue

        return keys

    def test_connection(self, host: str = "github.com", user: str = "git") -> Tuple[bool, str, float]:
        import time

        try:
            start_time = time.time()

            result = subprocess.run(
                ['ssh',
                 '-o', 'BatchMode=yes',
                 '-o', 'ConnectTimeout=10',
                 '-o', 'StrictHostKeyChecking=no',
                 '-T', f'{user}@{host}'],
                capture_output=True,
                text=True,
                timeout=15
            )

            response_time = time.time() - start_time
            output = result.stderr.lower() + result.stdout.lower()

            if any(phrase in output for phrase in [
                "successfully authenticated",
                "you've successfully authenticated",
                "permission denied",
                "connection closed"
            ]):
                return True, "SSH connection is working", response_time
            elif result.returncode == 0:
                return True, "SSH connection established", response_time
            else:
                return False, f"SSH error: {result.stderr[:100]}", response_time

        except subprocess.TimeoutExpired:
            return False, "SSH timeout", 15.0
        except Exception as e:
            return False, f"Error: {str(e)}", 0.0
