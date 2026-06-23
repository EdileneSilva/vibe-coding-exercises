#!/usr/bin/env python3
"""
Secrets Detection Hook for Pre-Commit

This hook scans staged files for potential secrets, API keys, credentials,
and other sensitive information before allowing a commit to proceed.

It is designed to prevent accidental commitment of sensitive data.
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess

# Hook name and version
HOOK_NAME = "secrets-detection"
HOOK_VERSION = "1.0.0"

# Configuration file path
CONFIG_FILE = Path(__file__).parent.parent.parent / "config" / "secrets-hook.json"

# Default secrets patterns (regex)
DEFAULT_PATTERNS = [
    # API Keys and Tokens
    r'(?i)(api[_-]?key|apikey|api[_-]?token|access[_-]?token|auth[_-]?token|secret[_-]?key|private[_-]?key|client[_-]?secret)['"\s:=]+[A-Za-z0-9_\-\.]{20,}' ,
    r'(?i)(Bearer\s+)[A-Za-z0-9_\-\.]{20,}',
    r'(?i)(ghp_[A-Za-z0-9_\-]{36,})',  # GitHub Personal Access Token
    r'(?i)(github_pat_[A-Za-z0-9_\-]{22,})',  # GitHub PAT
    r'(?i)(sk[_-]?[A-Za-z0-9_\-]{20,})',  # Stripe, OpenAI, etc. keys
    r'(?i)(xox[baprs][_-]?[A-Za-z0-9_\-]{20,})',  # Slack tokens
    
    # Database credentials
    r'(?i)(DATABASE_URL|DB_URL|SQLALCHEMY_DATABASE_URI)['"\s:=]+[A-Za-z0-9_\-\.:@/]+',
    r'(?i)(mysql|postgres|postgresql|mongodb|redis|sqlite)://[^\s<>"\']+',
    
    # Passwords
    r'(?i)(password|passwd|pwd)['"\s:=]+[A-Za-z0-9_\-!@#$%^&*()]{6,}',
    r'(?i)(CREATE\s+USER\s+.*IDENTIFIED\s+BY\s+)[\'"`][^\'"`]+[\'"`]',
    r'(?i)(ALTER\s+USER\s+.*WITH\s+PASSWORD\s+)[\'"`][^\'"`]+[\'"`]',
    
    # AWS Credentials
    r'(?i)(AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY)['"\s:=]+[A-Z0-9]{20,}',
    r'(?i)(AKIA[0-9A-Z]{16})',  # AWS Access Key ID pattern
    r'(?i)(aws[_-]?secret[_-]?access[_-]?key)['"\s:=]+[A-Za-z0-9/+=]{20,}',
    
    # Private Keys
    r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
    r'-----BEGIN\s+(EC\s+)?PRIVATE\s+KEY-----',
    r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----',
    
    # Generic Secret Patterns
    r'(?i)(secret|token|credential|key|auth)["\s:=]+[A-Za-z0-9_\-\.]{32,}',
    
    # JSON/Web tokens
    r'eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_.+/=]+',  # JWT
    
    # Heroku
    r'(?i)(heroku[_-]?api[_-]?key)['"\s:=]+[A-Fa-f0-9-]{36}',
    
    # Twilio
    r'(?i)(twilio[_-]?account[_-]?sid|twilio[_-]?auth[_-]?token)['"\s:=]+[A-Za-z0-9]{32,}',
    
    # SendGrid
    r'(?i)(sendgrid[_-]?api[_-]?key|SG\.[A-Za-z0-9_\-]{22,})' ,
    
    # Mailchimp
    r'(?i)(mailchimp[_-]?api[_-]?key)['"\s:=]+[A-Za-z0-9_\-]{32,}',
    
    # Firebase
    r'(?i)(firebase[_-]?api[_-]?key|firebase[_-]?auth[_-]?domain)['"\s:=]+[A-Za-z0-9_\-\.]+',
    
    # NPM
    r'(?i)(npm[_-]?api[_-]?key|npm[_-]?token)['"\s:=]+[A-Za-z0-9_\-]{36,}',
    
    # PyPI
    r'(?i)(pypi[_-]?api[_-]?token)['"\s:=]+pypi-AgEIcHlwaSJ[\w\-]{30,}',
]

# File extensions to scan
SCAN_EXTENSIONS = [
    '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.toml', '.cfg', '.conf',
    '.config', '.env', '.sh', '.bash', '.zsh', '.md', '.txt', '.csv',
    '.html', '.htm', '.xml', '.ini', '.cfm', '.sql', '.dockerfile'
]

# Binary file signatures to skip
BINARY_SIGNATURES = [
    b'\x89PNG', b'\xFF\xD8\xFF', b'GIF87a', b'GIF89a', b'\x42\x4D',
    b'\x00\x00\x01\x00', b'\x00\x00\x02\x00', b'%PDF', b'\x50\x4B\x03\x04'
]

# Maximum file size to scan (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class SecretsHook:
    """Main class for detecting secrets in files."""
    
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
                
                # Update patterns if configured
                if 'patterns' in self.config:
                    self.patterns.extend(self.config['patterns'])
                
                # Update extensions if configured
                if 'extensions' in self.config:
                    self.scan_extensions.extend(self.config['extensions'])
                
                # Update max file size if configured
                if 'max_file_size' in self.config:
                    self.max_file_size = self.config['max_file_size']
                
                # Update verbose setting
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
        # Skip binary files
        if self.is_binary(file_path):
            return False
        
        # Skip files over max size
        if file_path.stat().st_size > self.max_file_size:
            return False
        
        # Check extension
        if file_path.suffix.lower() in self.scan_extensions:
            return True
        
        # Also check .env files without extension
        if file_path.name == '.env':
            return True
        
        return False
    
    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan a file for secrets.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            List of found secrets with details
        """
        if not self.should_scan(file_path):
            return []
        
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                lines = content.splitlines()
        except (UnicodeDecodeError, IOError):
            return []
        
        # Scan each line
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
    
    def get_staged_files(self) -> List[Path]:
        """Get list of staged files."""
        files = []
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'],
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
    
    def run(self) -> int:
        """Run the hook on staged files.
        
        Returns:
            Exit code (0 = success, 1 = failure with secrets found)
        """
        staged_files = self.get_staged_files()
        
        if not staged_files:
            if self.verbose:
                print(f"{HOOK_NAME}: No staged files to scan")
            return 0
        
        all_findings = []
        
        for file_path in staged_files:
            if self.verbose:
                print(f"{HOOK_NAME}: Scanning {file_path}")
            
            findings = self.scan_file(file_path)
            all_findings.extend(findings)
        
        if all_findings:
            print(f"\n{HOOK_NAME} v{HOOK_VERSION}: Potential secrets detected!")
            print("=" * 60)
            
            for finding in all_findings:
                print(f"\n🚨 {finding['severity']} SEVERITY in {finding['file']}:{finding['line']}")
                print(f"   Pattern: {finding['pattern']}")
                print(f"   Match: {finding['match'][:100]}{'...' if len(finding['match']) > 100 else ''}")
            
            print("\n" + "=" * 60)
            print(f"❌ Commit rejected: {len(all_findings)} potential secret(s) found")
            print("\nIf this is a false positive, you can:")
            print("  1. Use git commit --no-verify to bypass this check")
            print("  2. Add the file to .gitignore")
            print("  3. Update the secrets-hook.json config to exclude the pattern")
            print("  4. Remove the sensitive data from the file")
            
            return 1
        else:
            if self.verbose:
                print(f"{HOOK_NAME}: No secrets detected in {len(staged_files)} files")
            return 0


def main():
    """Main entry point for the hook."""
    hook = SecretsHook()
    exit_code = hook.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
