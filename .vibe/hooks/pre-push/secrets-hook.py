#!/usr/bin/env python3
"""
Secrets Detection Hook for Pre-Push

This hook scans all commits being pushed for potential secrets, API keys,
credentials, and other sensitive information before allowing a push to proceed.

It is designed to prevent accidental pushing of sensitive data to remote repositories.
"""

import sys
import os
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Hook name and version
HOOK_NAME = "secrets-detection-pre-push"
HOOK_VERSION = "1.0.0"

# Configuration file path
CONFIG_FILE = Path(__file__).parent.parent.parent / "config" / "secrets-hook.json"

# Import from pre-commit hook to maintain consistency
try:
    # Try to import from pre-commit hook
    sys.path.insert(0, str(Path(__file__).parent.parent / "pre-commit"))
    from secrets_hook import (
        DEFAULT_PATTERNS,
        SCAN_EXTENSIONS,
        BINARY_SIGNATURES,
        MAX_FILE_SIZE
    )
except ImportError:
    # Fallback to redefining
    DEFAULT_PATTERNS = [
        r'(?i)(api[_-]?key|apikey|api[_-]?token|access[_-]?token|auth[_-]?token|secret[_-]?key|private[_-]?key|client[_-]?secret)['"\s:=]+[A-Za-z0-9_\-\.]{20,}' ,
        r'(?i)(Bearer\s+)[A-Za-z0-9_\-\.]{20,}',
        r'(?i)(ghp_[A-Za-z0-9_\-]{36,})',
        r'(?i)(github_pat_[A-Za-z0-9_\-]{22,})',
        r'(?i)(sk[_-]?[A-Za-z0-9_\-]{20,})',
        r'(?i)(xox[baprs][_-]?[A-Za-z0-9_\-]{20,})',
        r'(?i)(DATABASE_URL|DB_URL|SQLALCHEMY_DATABASE_URI)['"\s:=]+[A-Za-z0-9_\-\.:@/]+',
        r'(?i)(mysql|postgres|postgresql|mongodb|redis|sqlite)://[^\s<>"\']+',
        r'(?i)(password|passwd|pwd)['"\s:=]+[A-Za-z0-9_\-!@#$%^&*()]{6,}',
        r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
        r'eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_.+/=]+',
    ]
    
    SCAN_EXTENSIONS = [
        '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.toml', '.cfg', '.conf',
        '.config', '.env', '.sh', '.bash', '.zsh', '.md', '.txt', '.csv',
        '.html', '.htm', '.xml', '.ini', '.cfm', '.sql'
    ]
    
    BINARY_SIGNATURES = [
        b'\x89PNG', b'\xFF\xD8\xFF', b'GIF87a', b'GIF89a', b'\x42\x4D',
        b'\x00\x00\x01\x00', b'\x00\x00\x02\x00', b'%PDF', b'\x50\x4B\x03\x04'
    ]
    
    MAX_FILE_SIZE = 10 * 1024 * 1024


class SecretsPushHook:
    """Main class for detecting secrets in commits being pushed."""
    
    def __init__(self):
        self.patterns: List[str] = DEFAULT_PATTERNS.copy()
        self.scan_extensions: List[str] = SCAN_EXTENSIONS.copy()
        self.max_file_size: int = MAX_FILE_SIZE
        self.verbose: bool = False
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                
                if 'patterns' in self.config:
                    self.patterns.extend(self.config['patterns'])
                
                if 'extensions' in self.config:
                    self.scan_extensions.extend(self.config['extensions'])
                
                if 'max_file_size' in self.config:
                    self.max_file_size = self.config['max_file_size']
                
                if 'verbose' in self.config:
                    self.verbose = self.config['verbose']
                    
        except (IOError, json.JSONDecodeError) as e:
            if self.verbose:
                print(f"Warning: Could not load config: {e}")
    
    def is_binary(self, file_path: Path) -> bool:
        """Check if a file is binary."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                return any(header.startswith(sig) for sig in BINARY_SIGNATURES)
        except (IOError, OSError):
            return True
    
    def should_scan(self, file_path: Path) -> bool:
        """Determine if a file should be scanned."""
        if self.is_binary(file_path):
            return False
        
        if file_path.stat().st_size > self.max_file_size:
            return False
        
        if file_path.suffix.lower() in self.scan_extensions:
            return True
        
        if file_path.name == '.env':
            return True
        
        return False
    
    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan a file for secrets."""
        if not self.should_scan(file_path):
            return []
        
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                lines = content.splitlines()
        except (UnicodeDecodeError, IOError):
            return []
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.patterns:
                try:
                    for match in re.finditer(pattern, line):
                        findings.append({
                            'file': str(file_path),
                            'line': line_num,
                            'match': match.group(),
                            'pattern': pattern[:50] + '...' if len(pattern) > 50 else pattern,
                            'severity': self.get_severity(pattern)
                        })
                except re.error:
                    continue
        
        return findings
    
    def get_severity(self, pattern: str) -> str:
        """Get severity level for a pattern match."""
        pattern_lower = pattern.lower()
        
        if any(keyword in pattern_lower for keyword in ['password', 'passwd', 'pwd', 'secret']):
            return 'HIGH'
        elif any(keyword in pattern_lower for keyword in ['api', 'token', 'auth', 'key']):
            return 'HIGH'
        elif any(keyword in pattern_lower for keyword in ['database', 'db', 'url']):
            return 'HIGH'
        elif any(keyword in pattern_lower for keyword in ['private', 'account', 'credential']):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def get_commits_to_push(self) -> List[Dict[str, Any]]:
        """Get list of commits that would be pushed."""
        commits = []
        try:
            # Get the remote branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', '@{push}'],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            if result.returncode == 0 and result.stdout.strip():
                remote_branch = result.stdout.strip()
                
                # Get commits between local and remote
                result = subprocess.run(
                    ['git', 'log', f'{remote_branch}..HEAD', '--format=%H||%s', '--no-merges'],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd()
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            parts = line.split('||')
                            if len(parts) >= 2:
                                commits.append({
                                    'hash': parts[0],
                                    'subject': parts[1]
                                })
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return commits
    
    def get_changed_files(self, commit_hash: str) -> List[Path]:
        """Get list of files changed in a commit."""
        files = []
        try:
            result = subprocess.run(
                ['git', 'show', '--name-only', '--format=', commit_hash],
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            if result.returncode == 0 and result.stdout.strip():
                for file_path in result.stdout.strip().split('\n'):
                    if file_path.strip():
                        files.append(Path(file_path.strip()))
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return files
    
    def get_all_changed_files(self) -> List[Path]:
        """Get all files changed in commits to be pushed."""
        all_files = set()
        commits = self.get_commits_to_push()
        
        for commit in commits:
            files = self.get_changed_files(commit['hash'])
            all_files.update(files)
        
        return list(all_files)
    
    def run(self) -> int:
        """Run the hook on commits to be pushed.
        
        Returns:
            Exit code (0 = success, 1 = failure with secrets found)
        """
        commits = self.get_commits_to_push()
        
        if not commits:
            if self.verbose:
                print(f"{HOOK_NAME}: No commits to push")
            return 0
        
        if self.verbose:
            print(f"{HOOK_NAME}: Found {len(commits)} commit(s) to scan")
        
        all_findings = []
        scanned_files = set()
        
        # Get all unique files changed across all commits
        all_files = self.get_all_changed_files()
        
        if not all_files:
            if self.verbose:
                print(f"{HOOK_NAME}: No files changed in commits to push")
            return 0
        
        for file_path in all_files:
            if file_path in scanned_files:
                continue
            
            if self.verbose:
                print(f"{HOOK_NAME}: Scanning {file_path}")
            
            # Check if file still exists (might have been deleted)
            if not file_path.exists():
                continue
            
            findings = self.scan_file(file_path)
            all_findings.extend(findings)
            scanned_files.add(file_path)
        
        if all_findings:
            print(f"\n{HOOK_NAME} v{HOOK_VERSION}: Potential secrets detected in push!")
            print("=" * 60)
            
            # Group findings by commit if possible
            commits_info = self.get_commits_to_push()
            commit_map = {}
            for commit in commits_info:
                files = self.get_changed_files(commit['hash'])
                for file_path in files:
                    if str(file_path) not in commit_map:
                        commit_map[str(file_path)] = []
                    commit_map[str(file_path)].append(commit['hash'][:7])
            
            for finding in all_findings:
                file_path = finding['file']
                commits_str = ", ".join(commit_map.get(file_path, ["unknown"]))
                print(f"\n🚨 {finding['severity']} SEVERITY in {file_path}:{finding['line']}")
                print(f"   Commit(s): {commits_str}")
                print(f"   Pattern: {finding['pattern']}")
                print(f"   Match: {finding['match'][:100]}{'...' if len(finding['match']) > 100 else ''}")
            
            print("\n" + "=" * 60)
            print(f"❌ Push rejected: {len(all_findings)} potential secret(s) found")
            print("\nIf this is a false positive, you can:")
            print("  1. Use git push --no-verify to bypass this check")
            print("  2. Amend the commit to remove the sensitive data")
            print("  3. Update the secrets-hook.json config to exclude the pattern")
            print("  4. Add the file to .gitignore")
            
            return 1
        else:
            if self.verbose:
                print(f"{HOOK_NAME}: No secrets detected in {len(all_files)} files across {len(commits)} commits")
            return 0


def main():
    """Main entry point for the hook."""
    hook = SecretsPushHook()
    exit_code = hook.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
