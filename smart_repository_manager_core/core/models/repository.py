# Copyright (©) 2025, Alexander Suvorov. All rights reserved.
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class Repository:
    id: int
    name: str
    full_name: str
    html_url: str
    description: Optional[str] = None
    language: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    watchers_count: int = 0
    topics: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None
    size: int = 0
    archived: bool = False
    private: bool = False
    fork: bool = False
    license: Optional[Dict[str, Any]] = None
    default_branch: str = "main"
    open_issues_count: int = 0
    has_issues: bool = False
    has_projects: bool = False
    has_wiki: bool = False
    has_pages: bool = False
    homepage: Optional[str] = None
    ssh_url: Optional[str] = None
    clone_url: Optional[str] = None
    local_exists: bool = False
    need_update: bool = True

    def __str__(self) -> str:
        return f"Repository(name={self.name}, private={self.private})"

    @property
    def last_update(self) -> str:
        if not self.pushed_at:
            return "Unknown"
        try:
            dt = datetime.fromisoformat(self.pushed_at.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d")
        except Exception as e:
            print(e)
            return "Invalid date"

    @property
    def created_date(self) -> str:
        if not self.created_at:
            return "Unknown"
        try:
            dt = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d")
        except Exception as e:
            print(e)
            return "Invalid date"

    @property
    def size_mb(self) -> float:
        return self.size / 1024

    @property
    def license_name(self):
        if self.license and 'name' in self.license:
            return self.license['name']
        return "None"

    @property
    def short_description(self) -> str:
        if not self.description:
            return "No description"
        if len(self.description) > 60:
            return self.description[:60] + "..."
        return self.description

    def update_local_status(self, repos_path: Path) -> None:
        repo_folder = repos_path / self.name
        self.local_exists = False

        if repo_folder.exists():
            git_dir = repo_folder / ".git"
            if git_dir.exists() and git_dir.is_dir():
                self.local_exists = True

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "full_name": self.full_name,
            "html_url": self.html_url,
            "description": self.description,
            "language": self.language,
            "stargazers_count": self.stargazers_count,
            "forks_count": self.forks_count,
            "watchers_count": self.watchers_count,
            "topics": self.topics,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "pushed_at": self.pushed_at,
            "size": self.size,
            "archived": self.archived,
            "private": self.private,
            "fork": self.fork,
            "license": self.license,
            "default_branch": self.default_branch,
            "open_issues_count": self.open_issues_count,
            "has_issues": self.has_issues,
            "has_projects": self.has_projects,
            "has_wiki": self.has_wiki,
            "has_pages": self.has_pages,
            "homepage": self.homepage,
            "ssh_url": self.ssh_url,
            "clone_url": self.clone_url,
            "local_exists": self.local_exists,
            "need_update": self.need_update
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Repository':
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            full_name=data.get('full_name', ''),
            html_url=data.get('html_url', ''),
            description=data.get('description'),
            language=data.get('language'),
            stargazers_count=data.get('stargazers_count', 0),
            forks_count=data.get('forks_count', 0),
            watchers_count=data.get('watchers_count', 0),
            topics=data.get('topics', []),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            pushed_at=data.get('pushed_at'),
            size=data.get('size', 0),
            archived=data.get('archived', False),
            private=data.get('private', False),
            fork=data.get('fork', False),
            license=data.get('license'),
            default_branch=data.get('default_branch', 'main'),
            open_issues_count=data.get('open_issues_count', 0),
            has_issues=data.get('has_issues', False),
            has_projects=data.get('has_projects', False),
            has_wiki=data.get('has_wiki', False),
            has_pages=data.get('has_pages', False),
            homepage=data.get('homepage'),
            ssh_url=data.get('ssh_url'),
            clone_url=data.get('clone_url'),
            local_exists=data.get('local_exists', False),
            need_update=data.get('need_update', True)
        )
