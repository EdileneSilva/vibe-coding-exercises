#!/usr/bin/env python3
"""
Secrets Detection Hook for Pre-Commit

Scans staged files for potential secrets, API keys, credentials and other
sensitive information before allowing a commit to proceed.

Note: the module is named ``secrets_hook`` (underscore) so it can be imported
by the pre-push hook. Configure git to call it via a small wrapper or directly.
"""

import sys
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

HOOK_NAME = "secrets-detection"
HOOK_VERSION = "1.1.0"

CONFIG_FILE = Path(__file__).parent.parent.parent / "config" / "secrets-hook.json"

# Paths that are EXPECTED to contain secret-like patterns (the detector's own
# rules, documentation examples). Without this allowlist the hook blocks the
# commit of the hook itself — and the docs that show example connection strings.
DEFAULT_EXCLUDED_PATHS = [
    ".vibe/hooks/",
    ".vibe/config/secrets-hook.json",
    "scripts/secrets-scan",
    ".gitleaks.toml",
]

# Patterns use TRIPLE-quoted raw strings so an inner ' or " never terminates
# the literal (this was the bug that made the original file fail to import).
DEFAULT_PATTERNS = [
    # API keys / tokens
    r"""(?i)(api[_-]?key|apikey|api[_-]?token|access[_-]?token|auth[_-]?token|secret[_-]?key|private[_-]?key|client[_-]?secret)["'\s:=]+[A-Za-z0-9_\-.]{20,}""",
    r"""(?i)(Bearer\s+)[A-Za-z0-9_\-.]{20,}""",
    r"""(ghp_[A-Za-z0-9]{36,})""",            # GitHub PAT (classic)
    r"""(github_pat_[A-Za-z0-9_]{22,})""",    # GitHub PAT (fine-grained)
    r"""(sk-[A-Za-z0-9]{20,})""",             # OpenAI / Stripe style
    r"""(xox[baprs]-[A-Za-z0-9-]{10,})""",    # Slack tokens
    # Database credentials
    r"""(?i)(DATABASE_URL|DB_URL|SQLALCHEMY_DATABASE_URI)["'\s:=]+[A-Za-z0-9_\-.:@/]+""",
    r"""(?i)(mysql|postgres|postgresql|mongodb|redis)://[^\s<>"']+:[^\s<>"']+@""",
    # Passwords (require an assignment to cut false positives a bit)
    r"""(?i)(password|passwd|pwd)["'\s:=]{1,3}[A-Za-z0-9_\-!@#$%^&*()]{8,}""",
    # AWS
    r"""(AKIA[0-9A-Z]{16})""",
    r"""(?i)(aws[_-]?secret[_-]?access[_-]?key)["'\s:=]+[A-Za-z0-9/+=]{20,}""",
    # Private keys
    r"""-----BEGIN\s+(RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE\s+KEY-----""",
    # JWT
    r"""eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_.+/=]+""",
]

SCAN_EXTENSIONS = [
    ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".cfg", ".conf",
    ".config", ".env", ".sh", ".bash", ".zsh", ".md", ".txt", ".csv",
    ".html", ".htm", ".xml", ".ini", ".sql",
]

BINARY_SIGNATURES = [
    b"\x89PNG", b"\xFF\xD8\xFF", b"GIF87a", b"GIF89a", b"\x42\x4D",
    b"%PDF", b"\x50\x4B\x03\x04",
]

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class SecretsHook:
    """Detect secrets in files."""

    def __init__(self) -> None:
        self.patterns: List[str] = DEFAULT_PATTERNS.copy()
        self.scan_extensions: List[str] = SCAN_EXTENSIONS.copy()
        self.excluded_paths: List[str] = DEFAULT_EXCLUDED_PATHS.copy()
        self.max_file_size: int = MAX_FILE_SIZE
        self.verbose: bool = False
        self.config: Dict[str, Any] = {}
        self.load_config()
        # Pre-compile patterns once; drop any that fail to compile.
        self.compiled: List[re.Pattern] = []
        for p in self.patterns:
            try:
                self.compiled.append(re.compile(p))
            except re.error as exc:
                if self.verbose:
                    print(f"Skipping invalid pattern: {exc}")

    def load_config(self) -> None:
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                self.patterns.extend(self.config.get("patterns", []))
                self.scan_extensions.extend(self.config.get("extensions", []))
                self.excluded_paths.extend(self.config.get("excluded_paths", []))
                self.max_file_size = self.config.get("max_file_size", self.max_file_size)
                self.verbose = self.config.get("verbose", self.verbose)
        except (IOError, json.JSONDecodeError) as exc:
            if self.verbose:
                print(f"Warning: could not load config: {exc}")

    def is_excluded(self, file_path: Path) -> bool:
        posix = file_path.as_posix()
        return any(excluded in posix for excluded in self.excluded_paths)

    def is_binary(self, file_path: Path) -> bool:
        try:
            with open(file_path, "rb") as f:
                header = f.read(8)
            return any(header.startswith(sig) for sig in BINARY_SIGNATURES)
        except (IOError, OSError):
            return True

    def should_scan(self, file_path: Path) -> bool:
        if self.is_excluded(file_path):
            return False
        if not file_path.exists() or self.is_binary(file_path):
            return False
        try:
            if file_path.stat().st_size > self.max_file_size:
                return False
        except OSError:
            return False
        if file_path.suffix.lower() in self.scan_extensions:
            return True
        return file_path.name == ".env"

    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        if not self.should_scan(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except (UnicodeDecodeError, IOError):
            return []
        findings: List[Dict[str, Any]] = []
        for line_num, line in enumerate(lines, 1):
            for pattern in self.compiled:
                for match in pattern.finditer(line):
                    findings.append({
                        "file": str(file_path),
                        "line": line_num,
                        "match": match.group(),
                        "severity": self.get_severity(pattern.pattern),
                    })
        return findings

    @staticmethod
    def get_severity(pattern: str) -> str:
        p = pattern.lower()
        if any(k in p for k in ["password", "passwd", "pwd", "secret", "private", "akia", "begin"]):
            return "HIGH"
        if any(k in p for k in ["api", "token", "auth", "key", "bearer", "ghp", "github_pat"]):
            return "HIGH"
        if any(k in p for k in ["database", "db_url", "postgres", "mysql"]):
            return "HIGH"
        return "MEDIUM"

    def get_staged_files(self) -> List[Path]:
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                capture_output=True, text=True, cwd=Path.cwd(),
            )
            if result.returncode == 0 and result.stdout.strip():
                return [Path(p.strip()) for p in result.stdout.strip().split("\n") if p.strip()]
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return []

    def run(self) -> int:
        staged = self.get_staged_files()
        if not staged:
            if self.verbose:
                print(f"{HOOK_NAME}: no staged files to scan")
            return 0
        findings: List[Dict[str, Any]] = []
        for file_path in staged:
            findings.extend(self.scan_file(file_path))
        if not findings:
            if self.verbose:
                print(f"{HOOK_NAME}: no secrets detected in {len(staged)} files")
            return 0
        print(f"\n{HOOK_NAME} v{HOOK_VERSION}: potential secrets detected!")
        print("=" * 60)
        for f in findings:
            preview = f["match"][:80] + ("..." if len(f["match"]) > 80 else "")
            print(f"\n[{f['severity']}] {f['file']}:{f['line']}")
            print(f"   Match: {preview}")
        print("\n" + "=" * 60)
        print(f"Commit rejected: {len(findings)} potential secret(s) found.")
        print("\nIf this is a false positive you can:")
        print("  1. git commit --no-verify   (use sparingly)")
        print("  2. add the file to .gitignore")
        print("  3. add an excluded_paths entry in config/secrets-hook.json")
        print("  4. remove the sensitive data from the file")
        return 1


def main() -> None:
    sys.exit(SecretsHook().run())


if __name__ == "__main__":
    main()