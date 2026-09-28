# backend/worker/core/git_context.py
"""
Git Context — Uses git history to identify high-risk files and add developer context.

Signals: churn rate, recently changed files, security-relevant commit messages.
Findings in high-churn or recently-changed files can get confidence boost or
surface first in reports.
"""

import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SECURITY_KEYWORDS = frozenset({"fix", "security", "auth", "sql", "injection", "xss", "cve", "vuln", "patch"})


@dataclass
class GitContext:
    """Git-derived context for the repo."""

    high_churn_files: list[str] = field(default_factory=list)  # e.g. changed >10x in 90 days
    recently_changed_files: list[str] = field(default_factory=list)  # changed in last 30 days
    security_relevant_commits: list[str] = field(default_factory=list)  # commit hashes
    author_concentration: dict[str, int] = field(default_factory=dict)  # file -> unique authors
    repo_path: str = ""


def _run_git(repo_path: str, *args: str) -> str:
    try:
        r = subprocess.run(
            ["git", "-C", repo_path, *args],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=repo_path or None,
        )
        if r.returncode != 0:
            return ""
        return (r.stdout or "").strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        logger.debug("git command failed: %s", e)
        return ""


def get_git_context(
    repo_path: str,
    churn_days: int = 90,
    churn_threshold: int = 10,
    recent_days: int = 30,
) -> GitContext:
    """
    Build GitContext from repo. If repo_path is not a git repo or git is unavailable,
    returns an empty GitContext.
    """
    ctx = GitContext(repo_path=repo_path)
    if not repo_path or not Path(repo_path).exists():
        return ctx
    try:
        # Recently changed files (last N days)
        out = _run_git(repo_path, "log", f"--since={recent_days} days ago", "--name-only", "--pretty=format:")
        if out:
            ctx.recently_changed_files = sorted(set(line.strip() for line in out.splitlines() if line.strip()))

        # Churn: file path -> number of commits in window
        out = _run_git(repo_path, "log", f"--since={churn_days} days ago", "--name-only", "--pretty=format:.")
        if out:
            counts: dict[str, int] = {}
            for line in out.splitlines():
                line = line.strip()
                if line and line != ".":
                    counts[line] = counts.get(line, 0) + 1
            ctx.high_churn_files = [f for f, c in counts.items() if c >= churn_threshold]

        # Security-relevant commits (message contains keyword)
        for kw in SECURITY_KEYWORDS:
            out = _run_git(repo_path, "log", "-E", "--grep=" + kw, "--pretty=format:%H", "-n", "50")
            if out:
                ctx.security_relevant_commits.extend(out.splitlines())
        ctx.security_relevant_commits = list(dict.fromkeys(ctx.security_relevant_commits))[:100]

        # Author concentration per file (unique authors touching file)
        out = _run_git(repo_path, "shortlog", "-sn", "--all", "--no-merges", "--")
        if out:
            for line in out.splitlines()[:500]:
                parts = line.strip().split("\t", 1)
                if len(parts) == 2:
                    try:
                        n = int(parts[0].strip())
                        f = parts[1].strip()
                        if f:
                            ctx.author_concentration[f] = ctx.author_concentration.get(f, 0) + n
                    except ValueError:
                        pass
    except Exception as e:
        logger.warning("get_git_context failed: %s", e)
    return ctx


def confidence_boost_for_file(file_path: str, git_ctx: GitContext) -> float:
    """
    Return a small confidence boost (e.g. 0.0–0.1) if the file is high-churn or
    recently changed, so such findings are prioritized.
    """
    if not git_ctx or not file_path:
        return 0.0
    path_norm = file_path.replace("\\", "/")
    if path_norm in git_ctx.high_churn_files:
        return 0.1
    if path_norm in git_ctx.recently_changed_files:
        return 0.05
    return 0.0
