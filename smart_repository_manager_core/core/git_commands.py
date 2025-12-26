# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
from dataclasses import dataclass
from typing import Optional


@dataclass
class GitCommandResult:
    success: bool = False
    output: str = ""
    error: str = ""
    return_code: int = 0
    timed_out: bool = False

    def __str__(self) -> str:
        status = "✅ Success" if self.success else "❌ Failed"
        return f"GitCommandResult({status}, code={self.return_code})"


@dataclass
class GitOperationStatus:
    operation: str
    repo_name: str
    started: bool = False
    completed: bool = False
    success: Optional[bool] = None
    message: str = ""
    duration: float = 0.0

    def __str__(self) -> str:
        return f"GitOperation({self.operation} on {self.repo_name})"
