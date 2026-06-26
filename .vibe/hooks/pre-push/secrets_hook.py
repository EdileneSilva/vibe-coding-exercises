#!/usr/bin/env python3
"""
Secrets Detection Hook for Pre-Push

Scans every file changed in the commits about to be pushed, reusing the
detection logic from the pre-commit module so the two hooks stay consistent.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Import the shared detector. The pre-commit module is named with an underscore
# (secrets_hook.py) precisely so this import works — a hyphenated filename
# cannot be imported with a normal `import` statement.
sys.path.insert(0, str(Path(__file__).parent.parent / "pre-commit"))
from secrets_hook import SecretsHook, HOOK_VERSION  # noqa: E402

HOOK_NAME = "secrets-detection-pre-push"


class SecretsPushHook(SecretsHook):
    """Reuse SecretsHook detection but gather files from commits to be pushed."""

    def get_commits_to_push(self) -> List[str]:
        try:
            upstream = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "@{push}"],
                capture_output=True, text=True, cwd=Path.cwd(),
            )
            if upstream.returncode != 0 or not upstream.stdout.strip():
                return []
            remote_branch = upstream.stdout.strip()
            log = subprocess.run(
                ["git", "log", f"{remote_branch}..HEAD", "--format=%H", "--no-merges"],
                capture_output=True, text=True, cwd=Path.cwd(),
            )
            if log.returncode == 0 and log.stdout.strip():
                return [h.strip() for h in log.stdout.strip().split("\n") if h.strip()]
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return []

    def get_changed_files(self) -> List[Path]:
        files = set()
        for commit in self.get_commits_to_push():
            try:
                result = subprocess.run(
                    ["git", "show", "--name-only", "--format=", commit],
                    capture_output=True, text=True, cwd=Path.cwd(),
                )
                if result.returncode == 0:
                    for fp in result.stdout.strip().split("\n"):
                        if fp.strip():
                            files.add(Path(fp.strip()))
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        return list(files)

    def run(self) -> int:
        commits = self.get_commits_to_push()
        if not commits:
            if self.verbose:
                print(f"{HOOK_NAME}: nothing to push")
            return 0
        findings: List[Dict[str, Any]] = []
        for file_path in self.get_changed_files():
            if file_path.exists():
                findings.extend(self.scan_file(file_path))
        if not findings:
            if self.verbose:
                print(f"{HOOK_NAME}: no secrets across {len(commits)} commit(s)")
            return 0
        print(f"\n{HOOK_NAME} v{HOOK_VERSION}: potential secrets detected in push!")
        print("=" * 60)
        for f in findings:
            preview = f["match"][:80] + ("..." if len(f["match"]) > 80 else "")
            print(f"\n[{f['severity']}] {f['file']}:{f['line']}")
            print(f"   Match: {preview}")
        print("\n" + "=" * 60)
        print(f"Push rejected: {len(findings)} potential secret(s) found.")
        print("\nUse `git push --no-verify` to bypass (sparingly), or remove the data.")
        return 1


def main() -> None:
    sys.exit(SecretsPushHook().run())


if __name__ == "__main__":
    main()