# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any


class SSHKeyType(Enum):
    RSA = "rsa"
    ED25519 = "ed25519"
    ECDSA = "ecdsa"
    DSA = "dsa"


class SSHStatus(Enum):
    NOT_CONFIGURED = "not_configured"
    PARTIAL = "partial"
    VALID = "valid"
    ERROR = "error"


@dataclass
class SSHKey:
    type: SSHKeyType
    private_path: Path
    public_path: Optional[Path] = None
    fingerprint: Optional[str] = None
    size: Optional[int] = None
    comment: Optional[str] = None
    is_encrypted: bool = False
    is_github_authenticated: bool = False

    def __str__(self) -> str:
        return f"SSHKey(type={self.type.value}, path={self.private_path})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "private_path": str(self.private_path),
            "public_path": str(self.public_path) if self.public_path else None,
            "fingerprint": self.fingerprint,
            "size": self.size,
            "comment": self.comment,
            "is_encrypted": self.is_encrypted,
            "is_github_authenticated": self.is_github_authenticated
        }


@dataclass
class SSHConfig:
    ssh_dir: Path
    config_file: Path
    known_hosts_file: Path
    keys: List[SSHKey] = field(default_factory=list)
    has_github_in_config: bool = False
    has_github_in_known_hosts: bool = False
    has_valid_config: bool = False

    def __str__(self) -> str:
        return f"SSHConfig(dir={self.ssh_dir}, keys={len(self.keys)})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ssh_dir": str(self.ssh_dir),
            "config_file": str(self.config_file),
            "known_hosts_file": str(self.known_hosts_file),
            "keys": [key.to_dict() for key in self.keys],
            "has_github_in_config": self.has_github_in_config,
            "has_github_in_known_hosts": self.has_github_in_known_hosts,
            "has_valid_config": self.has_valid_config
        }


@dataclass
class SSHValidationResult:
    status: SSHStatus
    ssh_config: SSHConfig
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)
    can_clone_with_ssh: bool = False
    can_pull_with_ssh: bool = False
    github_authentication_working: bool = False

    def __str__(self) -> str:
        return f"SSHValidationResult(status={self.status.value}, errors={len(self.errors)})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "ssh_config": self.ssh_config.to_dict(),
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "test_results": self.test_results,
            "can_clone_with_ssh": self.can_clone_with_ssh,
            "can_pull_with_ssh": self.can_pull_with_ssh,
            "github_authentication_working": self.github_authentication_working
        }
