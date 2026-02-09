"""Repository allow/deny filtering for mining jobs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RepoFilter:
    """Filter owner/name repos by allowlist, denylist, and optional prefixes."""

    allow: set[str] = field(default_factory=set)
    deny: set[str] = field(default_factory=set)
    allow_prefixes: tuple[str, ...] = ()

    def accepts(self, repo: str) -> bool:
        name = repo.strip()
        if not name or "/" not in name:
            return False
        if name in self.deny:
            return False
        if self.allow and name not in self.allow:
            return False
        if self.allow_prefixes and not any(name.startswith(p) for p in self.allow_prefixes):
            return False
        return True

    def apply(self, repos: list[str]) -> list[str]:
        return [r for r in repos if self.accepts(r)]
