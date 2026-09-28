"""
FileRiskRanker - Scores files based on security risk signals.

Uses filename patterns and content analysis to assign risk scores,
recommend scan tiers, and identify low-priority files to skip.
"""

import os
import re
from typing import Dict, List, Optional


class FileRiskRanker:
    """Ranks files by security risk to prioritize scanning and tier selection."""

    # Frontend-specific high-risk signals (Failure Mode A — .jsx/.tsx scored too low)
    FRONTEND_HIGH_RISK_SIGNALS = {
        "patterns": [
            "dangerouslySetInnerHTML",
            "innerHTML",
            "document.write",
            "eval(",
            "localStorage.setItem",
            "sessionStorage.setItem",
            "window.location",
            "router.push",
            "router.replace",
            "searchParams.get",
            "query.",  # Next.js query params
        ],
        "filenames": [
            "login", "auth", "redirect", "oauth",
            "comment", "task", "user", "profile",
            "analytics", "tracking", "config",
        ],
    }

    # Risk signals with their score adjustments
    RISK_SIGNALS = [
        # Positive signals (higher risk)
        ("filename", r"(auth|login|register|password|token|session)", 0.30, "auth"),
        ("filename", r"(upload|file|download|export|import)", 0.25, "file_handling"),
        ("filename", r"(admin|dashboard|api|route|handler|view|controller)", 0.25, "api"),
        ("filename", r"(query|db|database|model|repository|dao)", 0.20, "database"),
        ("filename", r"(exec|command|shell|process|subprocess)", 0.30, "command"),
        # High-risk model files (MISS 3 fix - ensure user.py, auth.py get high scores)
        ("filename", r"(user\.py|auth\.py|account\.py|identity\.py)", 0.35, "user_model"),
        ("filepath", r"models[/\\].*\.py$", 0.25, "models_directory"),
        # Secrets/config files (MISS 1 fix - ensure config.py gets scanned)
        ("filename", r"(config\.py|settings\.py|constants\.py|secrets\.py)", 0.30, "config_file"),
        ("content", r"(SECRET_KEY|API_KEY|PASSWORD|TOKEN)\s*=\s*[\"'][^\"']+", 0.40, "hardcoded_secret"),
        ("content", r"eval\s*\(", 0.30, "eval"),
        ("content", r"exec\s*\(", 0.30, "exec"),
        ("content", r"pickle\.loads?\s*\(", 0.30, "pickle"),
        ("content", r"yaml\.load\s*\([^)]*\)(?!.*SafeLoader)", 0.30, "yaml_unsafe"),
        ("content", r"deserializ", 0.30, "deserialize"),
        # SQL construction patterns (MISS 3 fix)
        ("content", r"(SELECT|INSERT|UPDATE|DELETE)\s+.*%\s*\(|\+.*\+|\.format\(|f[\"'].*SELECT", 0.35, "sql_construction"),
        # XSS patterns (MISS 2 fix)
        ("content", r"(request\.args|request\.form|request\.json).*\+.*<\w+|render_template_string", 0.35, "xss_html_output"),
        # Broader taint sources — user input / template rendering (avoids 0.0 for app.py etc.)
        ("content", r"request\.(form|args|json|cookies|headers)\b", 0.25, "user_input_source"),
        ("content", r"render_template\s*\(", 0.20, "template_render"),
        ("content", r"params\.|req\.body|req\.query\b", 0.25, "web_request_source"),
        # Command injection patterns (MISS 4 fix)
        ("content", r"(subprocess\.(getoutput|call|run)|os\.(system|popen))\s*\(", 0.35, "command_injection_sink"),

        # Negative signals (lower risk)
        ("filename", r"(test_|_test|spec_|_spec|\.test\.|\.spec\.)", -0.40, "test_file"),
        ("filename", r"(migration|seed|fixture|mock|factory)", -0.20, "migration"),
    ]

    def __init__(self):
        pass

    # Extensions that are always worth scanning (get base score to avoid skip)
    CODE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".php", ".rb", ".vue", ".svelte", ".html", ".htm"}
    # Config files (secrets, misconfigs) — lower base but still scanned
    CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".env", ".ini", ".cfg"}

    def _detect_language(self, filepath: str) -> Optional[str]:
        """Detect programming language from file extension."""
        ext = os.path.splitext(filepath)[1].lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
        }
        return language_map.get(ext)

    def rank_one(self, filepath: str, content: str) -> Dict:
        """
        Rank a single file by risk.

        Args:
            filepath: Relative path to the file
            content: File content as string

        Returns:
            Dictionary with risk score and recommendations
        """
        score = 0.0
        reasons = []
        ext = os.path.splitext(filepath)[1].lower()
        if ext in self.CODE_EXTENSIONS:
            score = 0.08  # Base score for code files — ensures we never skip them (threshold 0.05)
            reasons.append("code_file")
        elif ext in self.CONFIG_EXTENSIONS:
            score = 0.04  # Config files can contain secrets, misconfigs
            reasons.append("config_file")
        basename = os.path.basename(filepath).lower()
        filepath_lower = filepath.lower()

        # Apply all signals
        for signal_type, pattern, adjustment, reason_code in self.RISK_SIGNALS:
            if signal_type == "filename":
                if re.search(pattern, basename, re.IGNORECASE):
                    score += adjustment
                    reasons.append(reason_code)
            elif signal_type == "filepath":
                if re.search(pattern, filepath_lower, re.IGNORECASE):
                    score += adjustment
                    reasons.append(reason_code)
            elif signal_type == "content":
                if re.search(pattern, content, re.IGNORECASE):
                    score += adjustment
                    reasons.append(reason_code)

        # Frontend high-risk: boost .jsx/.tsx/.js/.ts/.vue/.svelte/.html with XSS/redirect/storage patterns
        ext = os.path.splitext(filepath)[1].lower()
        if ext in {".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".html"}:
            for pat in self.FRONTEND_HIGH_RISK_SIGNALS["patterns"]:
                if pat in content:
                    score += 0.25
                    reasons.append("frontend_risk_pattern")
                    break
            for name_part in self.FRONTEND_HIGH_RISK_SIGNALS["filenames"]:
                if name_part in basename:
                    score += 0.20
                    reasons.append("frontend_risk_filename")
                    break

        # Clamp to [0, 1]
        score = max(0.0, min(1.0, score))

        # Determine recommended tier
        if score > 0.7:
            recommended_tier = 3
        elif score > 0.4:
            recommended_tier = 2
        else:
            recommended_tier = 1

        # Determine if should skip
        skip = score < 0.05

        return {
            "filepath": filepath,
            "risk_score": round(score, 2),
            "recommended_tier": recommended_tier,
            "skip": skip,
            "risk_reasons": reasons,
            "language": self._detect_language(filepath),
        }

    def rank(self, file_list: List[str], project_path: str) -> List[Dict]:
        """
        Rank multiple files by risk.

        Args:
            file_list: List of relative file paths
            project_path: Project root directory

        Returns:
            List of file rankings sorted by risk score (descending)
        """
        rankings = []

        for filepath in file_list:
            full_path = os.path.join(project_path, filepath)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                # If we can't read, give a neutral score
                rankings.append({
                    "filepath": filepath,
                    "risk_score": 0.3,
                    "recommended_tier": 2,
                    "skip": False,
                    "risk_reasons": ["read_error"],
                    "language": None,
                })
                continue

            ranking = self.rank_one(filepath, content)
            rankings.append(ranking)

        # Sort by risk score descending
        rankings.sort(key=lambda x: x["risk_score"], reverse=True)
        return rankings
