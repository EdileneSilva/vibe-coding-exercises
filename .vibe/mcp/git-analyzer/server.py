#!/usr/bin/env python3
"""
Git Analyzer MCP Server

A Model Context Protocol server that provides Git repository analysis
capabilities for the Docker To-Do App project.

This MCP server allows AI agents to:
- Analyze Git commits, branches, and tags
- View diffs and changes between revisions
- Check repository status and history
- Analyze blame information
- Search through Git history
"""

import subprocess
import json
import re
from typing import Any, Optional
from datetime import datetime
from pathlib import Path

# MCP Server metadata
MCP_SERVER_NAME = "git-analyzer"
MCP_SERVER_VERSION = "1.0.0"

# Git commands
GIT_CMD = "git"


class GitAnalyzer:
    """Main git analyzer class that provides Git-related functionality."""
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = repo_path or str(Path(__file__).parent.parent.parent.parent)
    
    def _run_git_command(self, command: list[str]) -> dict[str, Any]:
        """Execute a git command and return the result."""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "command": " ".join(command)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out",
                "command": " ".join(command),
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(command)
            }
    
    def get_repository_info(self) -> dict[str, Any]:
        """Get basic repository information."""
        result = self._run_git_command([GIT_CMD, "remote", "-v"])
        remotes = []
        if result["success"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        remotes.append({
                            "name": parts[0],
                            "url": parts[1]
                        })
        
        return {
            "path": self.repo_path,
            "remotes": remotes,
            "head_commit": self.get_head_commit(),
            "branch": self.get_current_branch(),
            "status": self.get_repository_status()
        }
    
    def get_head_commit(self) -> dict[str, Any]:
        """Get information about the HEAD commit."""
        result = self._run_git_command([GIT_CMD, "rev-parse", "--verify", "HEAD"])
        commit_hash = result["stdout"] if result["success"] else ""
        
        if commit_hash:
            return self.get_commit_info(commit_hash)
        return {}
    
    def get_current_branch(self) -> str:
        """Get the current branch name."""
        result = self._run_git_command([GIT_CMD, "branch", "--show-current"])
        if result["success"]:
            return result["stdout"]
        return ""
    
    def get_repository_status(self) -> dict[str, Any]:
        """Get the repository status (modified, untracked files)."""
        result = self._run_git_command([GIT_CMD, "status", "--porcelain=v2", "--branch"])
        if result["success"]:
            lines = result["stdout"].split('\n')
            status = {
                "branch": "",
                "tracking": "",
                "ahead": 0,
                "behind": 0,
                "modified": [],
                "added": [],
                "deleted": [],
                "renamed": [],
                "copied": [],
                "untracked": [],
                "ignored": []
            }
            
            for line in lines:
                if line.startswith("#"):
                    # Branch information
                    parts = line[1:].split(",")
                    if parts:
                        status["branch"] = parts[0].strip()
                        for part in parts[1:]:
                            if "ahead" in part:
                                status["ahead"] = int(part.split("ahead")[1].strip())
                            elif "behind" in part:
                                status["behind"] = int(part.split("behind")[1].strip())
                elif len(line) >= 3:
                    file_status = line[0:2]
                    file_path = line[3:]
                    
                    if file_status == "1 " or file_status == " M":
                        status["modified"].append(file_path)
                    elif file_status == "A " or file_status == "??":
                        status["added"].append(file_path)
                    elif file_status == "D " or file_status == "AD":
                        status["deleted"].append(file_path)
                    elif file_status == "R " or file_status == "RM":
                        status["renamed"].append(file_path)
                    elif file_status == "C " or file_status == "CM":
                        status["copied"].append(file_path)
                    elif file_status == "!!":
                        status["ignored"].append(file_path)
                    elif file_status == "?":
                        status["untracked"].append(file_path)
            
            return status
        
        return {"error": result.get("stderr", "")}
    
    def list_branches(self, all: bool = False, remotes: bool = False) -> dict[str, Any]:
        """List all branches in the repository.
        
        Args:
            all: Include remote branches
            remotes: Only show remote branches
            
        Returns:
            Dictionary with branch list
        """
        cmd = [GIT_CMD, "branch"]
        if all:
            cmd.append("-a")
        if remotes:
            cmd.append("-r")
        cmd.extend(["--format", "%(refname:short)||%(objectname:short)||%(committerdate:iso)||%(subject)"])
        
        result = self._run_git_command(cmd)
        branches = []
        if result["success"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    parts = line.split("||")
                    if len(parts) >= 4:
                        branches.append({
                            "name": parts[0],
                            "short_hash": parts[1],
                            "date": parts[2],
                            "subject": parts[3]
                        })
        
        return {"branches": branches, "count": len(branches)}
    
    def get_branch_info(self, branch_name: str) -> dict[str, Any]:
        """Get detailed information about a specific branch.
        
        Args:
            branch_name: Name of the branch
            
        Returns:
            Dictionary with branch information
        """
        # Get branch commit count
        result_count = self._run_git_command([GIT_CMD, "rev-list", "--count", branch_name])
        commit_count = int(result_count["stdout"]) if result_count["success"] else 0
        
        # Get latest commit on branch
        result_latest = self._run_git_command([GIT_CMD, "rev-parse", branch_name])
        latest_commit = result_latest["stdout"] if result_latest["success"] else ""
        
        # Get branch remote tracking info
        result_tracking = self._run_git_command([GIT_CMD, "for-each-ref", "--format=%(upstream:track)", branch_name])
        tracking = result_tracking["stdout"] if result_tracking["success"] else ""
        
        commit_info = {}
        if latest_commit:
            commit_info = self.get_commit_info(latest_commit)
        
        return {
            "name": branch_name,
            "commit_count": commit_count,
            "latest_commit": latest_commit,
            "latest_commit_info": commit_info,
            "tracking": tracking,
            "is_current": branch_name == self.get_current_branch()
        }
    
    def list_tags(self, sort: str = "-creatordate") -> dict[str, Any]:
        """List all tags in the repository.
        
        Args:
            sort: Sort order (default: newest first)
            
        Returns:
            Dictionary with tag list
        """
        result = self._run_git_command([GIT_CMD, "tag", "--format", "%(refname:short)||%(objectname:short)||%(creatordate:iso)||%(subject)", 
                                        "--sort", sort])
        tags = []
        if result["success"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    parts = line.split("||")
                    if len(parts) >= 4:
                        tags.append({
                            "name": parts[0],
                            "short_hash": parts[1],
                            "date": parts[2],
                            "subject": parts[3]
                        })
        
        return {"tags": tags, "count": len(tags)}
    
    def get_tag_info(self, tag_name: str) -> dict[str, Any]:
        """Get detailed information about a specific tag.
        
        Args:
            tag_name: Name of the tag
            
        Returns:
            Dictionary with tag information
        """
        # Get tag commit
        result_commit = self._run_git_command([GIT_CMD, "rev-parse", tag_name])
        commit_hash = result_commit["stdout"] if result_commit["success"] else ""
        
        if commit_hash:
            commit_info = self.get_commit_info(commit_hash)
            return {
                "name": tag_name,
                "commit": commit_hash,
                "commit_info": commit_info,
                "type": self._get_tag_type(tag_name)
            }
        
        return {"name": tag_name, "error": "Tag not found"}
    
    def _get_tag_type(self, tag_name: str) -> str:
        """Get the type of a tag (lightweight or annotated)."""
        result = self._run_git_command([GIT_CMD, "cat-file", "-t", tag_name])
        if result["success"]:
            return result["stdout"]
        return "unknown"
    
    def list_commits(self, max_count: int = 20, since: Optional[str] = None, 
                    until: Optional[str] = None, author: Optional[str] = None,
                    grep: Optional[str] = None, branch: Optional[str] = None) -> dict[str, Any]:
        """List commits in the repository.
        
        Args:
            max_count: Maximum number of commits to return
            since: Show commits since this date
            until: Show commits until this date
            author: Filter by author
            grep: Filter by commit message
            branch: Show commits from this branch
            
        Returns:
            Dictionary with commit list
        """
        cmd = [GIT_CMD, "log", f"--max-count={max_count}", "--format=%H||%h||%an||%ae||%ad||%s"]
        
        if since:
            cmd.extend(["--since", since])
        if until:
            cmd.extend(["--until", until])
        if author:
            cmd.extend(["--author", author])
        if grep:
            cmd.extend(["--grep", grep])
        if branch:
            cmd.append(branch)
        
        result = self._run_git_command(cmd)
        commits = []
        if result["success"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    parts = line.split("||")
                    if len(parts) >= 6:
                        commits.append({
                            "hash": parts[0],
                            "short_hash": parts[1],
                            "author_name": parts[2],
                            "author_email": parts[3],
                            "date": parts[4],
                            "subject": parts[5]
                        })
        
        return {"commits": commits, "count": len(commits)}
    
    def get_commit_info(self, commit_hash: str) -> dict[str, Any]:
        """Get detailed information about a specific commit.
        
        Args:
            commit_hash: Hash of the commit
            
        Returns:
            Dictionary with commit information
        """
        # Get commit data
        result = self._run_git_command([GIT_CMD, "cat-file", "-p", commit_hash])
        commit_data = result["stdout"] if result["success"] else ""
        
        if not commit_data:
            return {"hash": commit_hash, "error": "Commit not found"}
        
        # Parse commit data
        info = {
            "hash": commit_hash,
            "short_hash": commit_hash[:7],
            "parents": [],
            "author": {},
            "committer": {},
            "message": "",
            "tree": "",
            "stats": {}
        }
        
        lines = commit_data.split('\n')
        in_message = False
        for line in lines:
            if line.startswith("tree "):
                info["tree"] = line[5:]
            elif line.startswith("parent "):
                info["parents"].append(line[7:])
            elif line.startswith("author "):
                self._parse_person_info(line[7:], info["author"])
            elif line.startswith("committer "):
                self._parse_person_info(line[9:], info["committer"])
            elif line == "":
                in_message = True
            elif in_message:
                info["message"] += line + "\n"
        
        info["message"] = info["message"].strip()
        info["short_message"] = info["message"].split('\n')[0]
        
        # Get commit stats
        result_stats = self._run_git_command([GIT_CMD, "show", "--stat", "--format=", commit_hash])
        if result_stats["success"]:
            info["stats"] = self._parse_commit_stats(result_stats["stdout"])
        
        # Get changed files
        result_files = self._run_git_command([GIT_CMD, "show", "--name-only", "--format=", commit_hash])
        if result_files["success"]:
            info["changed_files"] = [f for f in result_files["stdout"].split('\n') if f.strip()]
        
        return info
    
    def _parse_person_info(self, line: str, target: dict[str, str]) -> None:
        """Parse git person info (author/committer) line."""
        # Format: Name <email> timestamp timezone
        match = re.match(r'(.+?)\s*<([^>]+)>\s+(\d+)\s+([+-]\d{4})', line)
        if match:
            target["name"] = match.group(1).strip()
            target["email"] = match.group(2).strip()
            target["timestamp"] = int(match.group(3))
            target["timezone"] = match.group(4)
            target["date"] = datetime.fromtimestamp(int(match.group(3))).isoformat() + "Z"
    
    def _parse_commit_stats(self, stats_text: str) -> dict[str, Any]:
        """Parse git commit statistics."""
        lines = stats_text.strip().split('\n')
        if len(lines) < 1:
            return {}
        
        # Last line is summary
        summary_line = lines[-1]
        match = re.match(r'(\d+)\s+files?\s+changed', summary_line)
        files_changed = int(match.group(1)) if match else 0
        
        # Parse file changes
        changes = []
        for line in lines[:-1]:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    changes.append({
                        "file": parts[-1],
                        "changes": parts[0].strip()
                    })
        
        return {
            "files_changed": files_changed,
            "changes": changes
        }
    
    def get_diff(self, commit_a: str, commit_b: Optional[str] = None, 
                 path: Optional[str] = None) -> dict[str, Any]:
        """Get the diff between two commits or between commit and working tree.
        
        Args:
            commit_a: First commit or file
            commit_b: Second commit (optional, defaults to working tree)
            path: Optional path to diff
            
        Returns:
            Dictionary with diff information
        """
        cmd = [GIT_CMD, "diff"]
        if commit_b:
            cmd.extend([commit_a, commit_b])
        else:
            cmd.append(commit_a)
        
        if path:
            cmd.append("--")
            cmd.append(path)
        
        cmd.extend(["--format=", "--"])
        
        result = self._run_git_command(cmd)
        return {
            "from": commit_a,
            "to": commit_b or "working tree",
            "path": path or ".",
            "diff": result.get("stdout", ""),
            "success": result.get("success", False),
            "error": result.get("stderr", "")
        }
    
    def get_blame(self, file_path: str, commit: Optional[str] = None) -> dict[str, Any]:
        """Get blame information for a file.
        
        Args:
            file_path: Path to the file
            commit: Optional commit to blame (defaults to HEAD)
            
        Returns:
            Dictionary with blame information
        """
        cmd = [GIT_CMD, "blame", "--line-porcelain"]
        if commit:
            cmd.append(commit)
        cmd.append("--")
        cmd.append(file_path)
        
        result = self._run_git_command(cmd)
        if result["success"]:
            blame = []
            current = {}
            for line in result["stdout"].split('\n'):
                if line.startswith("^"):
                    # New blame entry
                    if current:
                        blame.append(current)
                    parts = line[1:].split()
                    current = {
                        "commit": parts[0] if len(parts) > 0 else "",
                        "line_number": int(parts[1]) if len(parts) > 1 else 0,
                        "original_line_number": int(parts[2]) if len(parts) > 2 else 0,
                        "num_lines": int(parts[3]) if len(parts) > 3 else 0
                    }
                elif line.startswith("author "):
                    current["author"] = line[7:]
                elif line.startswith("author-mail "):
                    current["author_email"] = line[13:].strip('<>')
                elif line.startswith("author-time "):
                    current["author_time"] = int(line[12:].split()[0])
                    current["author_timezone"] = line[12:].split()[1] if len(line[12:].split()) > 1 else ""
                elif line.startswith("committer "):
                    current["committer"] = line[10:]
                elif line.startswith("committer-mail "):
                    current["committer_email"] = line[16:].strip('<>')
                elif line.startswith("committer-time "):
                    current["committer_time"] = int(line[14:].split()[0])
                    current["committer_timezone"] = line[14:].split()[1] if len(line[14:].split()) > 1 else ""
                elif line.startswith("summary "):
                    current["summary"] = line[8:]
                elif line.startswith("boundary"):
                    current["boundary"] = True
                elif line.startswith("filename "):
                    current["filename"] = line[9:]
                elif line and not line.startswith("\t"):
                    # Content line
                    if "content" not in current:
                        current["content"] = ""
                    current["content"] += line + "\n"
            
            if current:
                blame.append(current)
            
            return {"file": file_path, "blame": blame, "count": len(blame)}
        
        return {"file": file_path, "error": result.get("stderr", "File not found")}
    
    def search_commits(self, query: str, max_count: int = 20) -> dict[str, Any]:
        """Search commits by message.
        
        Args:
            query: Search query
            max_count: Maximum number of results
            
        Returns:
            Dictionary with matching commits
        """
        result = self._run_git_command([
            GIT_CMD, "log", 
            f"--max-count={max_count}",
            "--format=%H||%h||%an||%ad||%s",
            "--grep", query, "-i"
        ])
        commits = []
        if result["success"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    parts = line.split("||")
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0],
                            "short_hash": parts[1],
                            "author": parts[2],
                            "date": parts[3],
                            "subject": parts[4]
                        })
        
        return {"commits": commits, "count": len(commits), "query": query}
    
    def search_files(self, query: str, commit: Optional[str] = None) -> dict[str, Any]:
        """Search for a string in files (uses git grep).
        
        Args:
            query: Search query
            commit: Optional commit to search in
            
        Returns:
            Dictionary with matching files and lines
        """
        cmd = [GIT_CMD, "grep", "-n", "--format=%h||%f||%n||%:", query]
        if commit:
            cmd.append(commit)
        
        result = self._run_git_command(cmd)
        matches = []
        if result["success"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    parts = line.split("||")
                    if len(parts) >= 4:
                        matches.append({
                            "commit": parts[0] if parts[0] else "working tree",
                            "file": parts[1],
                            "line_number": int(parts[2]) if parts[2].isdigit() else 0,
                            "line": parts[3]
                        })
        
        return {"matches": matches, "count": len(matches), "query": query}
    
    def get_file_history(self, file_path: str, max_count: int = 20) -> dict[str, Any]:
        """Get the history of changes for a specific file.
        
        Args:
            file_path: Path to the file
            max_count: Maximum number of commits to return
            
        Returns:
            Dictionary with file history
        """
        result = self._run_git_command([
            GIT_CMD, "log", 
            f"--max-count={max_count}",
            "--oneline",
            "--format=%H||%h||%an||%ad||%s",
            "--", file_path
        ])
        commits = []
        if result["success"]:
            for line in result["stdout"].split('\n'):
                if line.strip():
                    parts = line.split("||")
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0],
                            "short_hash": parts[1],
                            "author": parts[2],
                            "date": parts[3],
                            "subject": parts[4]
                        })
        
        return {"file": file_path, "commits": commits, "count": len(commits)}


# Initialize the git analyzer
analyzer = GitAnalyzer()


def get_tools() -> list[dict[str, Any]]:
    """Get the list of MCP tools provided by this server."""
    return [
        {
            "name": "git_get_repository_info",
            "description": "Get basic repository information (remotes, HEAD, branch, status)",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "git_get_current_branch",
            "description": "Get the current branch name",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "git_get_repository_status",
            "description": "Get the repository status (modified, untracked files)",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "git_list_branches",
            "description": "List all branches in the repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean",
                        "description": "Include remote branches",
                        "default": False,
                    },
                    "remotes": {
                        "type": "boolean",
                        "description": "Only show remote branches",
                        "default": False,
                    },
                },
            },
        },
        {
            "name": "git_get_branch_info",
            "description": "Get detailed information about a specific branch",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "branch_name": {
                        "type": "string",
                        "description": "Name of the branch",
                    },
                },
                "required": ["branch_name"],
            },
        },
        {
            "name": "git_list_tags",
            "description": "List all tags in the repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sort": {
                        "type": "string",
                        "description": "Sort order (default: newest first)",
                        "default": "-creatordate",
                    },
                },
            },
        },
        {
            "name": "git_get_tag_info",
            "description": "Get detailed information about a specific tag",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tag_name": {
                        "type": "string",
                        "description": "Name of the tag",
                    },
                },
                "required": ["tag_name"],
            },
        },
        {
            "name": "git_list_commits",
            "description": "List commits in the repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "max_count": {
                        "type": "integer",
                        "description": "Maximum number of commits to return",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 500,
                    },
                    "since": {
                        "type": "string",
                        "description": "Show commits since this date",
                        "default": None,
                    },
                    "until": {
                        "type": "string",
                        "description": "Show commits until this date",
                        "default": None,
                    },
                    "author": {
                        "type": "string",
                        "description": "Filter by author",
                        "default": None,
                    },
                    "grep": {
                        "type": "string",
                        "description": "Filter by commit message",
                        "default": None,
                    },
                    "branch": {
                        "type": "string",
                        "description": "Show commits from this branch",
                        "default": None,
                    },
                },
            },
        },
        {
            "name": "git_get_commit_info",
            "description": "Get detailed information about a specific commit",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "commit_hash": {
                        "type": "string",
                        "description": "Hash of the commit",
                    },
                },
                "required": ["commit_hash"],
            },
        },
        {
            "name": "git_get_head_commit",
            "description": "Get information about the HEAD commit",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "git_get_diff",
            "description": "Get the diff between two commits or between commit and working tree",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "commit_a": {
                        "type": "string",
                        "description": "First commit or file",
                    },
                    "commit_b": {
                        "type": "string",
                        "description": "Second commit (optional, defaults to working tree)",
                        "default": None,
                    },
                    "path": {
                        "type": "string",
                        "description": "Optional path to diff",
                        "default": None,
                    },
                },
                "required": ["commit_a"],
            },
        },
        {
            "name": "git_get_blame",
            "description": "Get blame information for a file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file",
                    },
                    "commit": {
                        "type": "string",
                        "description": "Optional commit to blame (defaults to HEAD)",
                        "default": None,
                    },
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "git_search_commits",
            "description": "Search commits by message",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "max_count": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 500,
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "git_search_files",
            "description": "Search for a string in files",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "commit": {
                        "type": "string",
                        "description": "Optional commit to search in",
                        "default": None,
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "git_get_file_history",
            "description": "Get the history of changes for a specific file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file",
                    },
                    "max_count": {
                        "type": "integer",
                        "description": "Maximum number of commits to return",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 500,
                    },
                },
                "required": ["file_path"],
            },
        },
    ]


def call_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Call an MCP tool by name with arguments.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments
        
    Returns:
        Dictionary with the tool result
    """
    tool_handlers = {
        "git_get_repository_info": lambda args: {
            "info": analyzer.get_repository_info()
        },
        "git_get_current_branch": lambda args: {
            "branch": analyzer.get_current_branch()
        },
        "git_get_repository_status": lambda args: {
            "status": analyzer.get_repository_status()
        },
        "git_list_branches": lambda args: analyzer.list_branches(
            all=args.get("all", False),
            remotes=args.get("remotes", False)
        ),
        "git_get_branch_info": lambda args: analyzer.get_branch_info(
            args.get("branch_name", "")
        ),
        "git_list_tags": lambda args: analyzer.list_tags(
            sort=args.get("sort", "-creatordate")
        ),
        "git_get_tag_info": lambda args: analyzer.get_tag_info(
            args.get("tag_name", "")
        ),
        "git_list_commits": lambda args: analyzer.list_commits(
            max_count=args.get("max_count", 20),
            since=args.get("since"),
            until=args.get("until"),
            author=args.get("author"),
            grep=args.get("grep"),
            branch=args.get("branch")
        ),
        "git_get_commit_info": lambda args: analyzer.get_commit_info(
            args.get("commit_hash", "")
        ),
        "git_get_head_commit": lambda args: {
            "commit": analyzer.get_head_commit()
        },
        "git_get_diff": lambda args: analyzer.get_diff(
            commit_a=args.get("commit_a", ""),
            commit_b=args.get("commit_b"),
            path=args.get("path")
        ),
        "git_get_blame": lambda args: analyzer.get_blame(
            file_path=args.get("file_path", ""),
            commit=args.get("commit")
        ),
        "git_search_commits": lambda args: analyzer.search_commits(
            query=args.get("query", ""),
            max_count=args.get("max_count", 20)
        ),
        "git_search_files": lambda args: analyzer.search_files(
            query=args.get("query", ""),
            commit=args.get("commit")
        ),
        "git_get_file_history": lambda args: analyzer.get_file_history(
            file_path=args.get("file_path", ""),
            max_count=args.get("max_count", 20)
        ),
    }
    
    if tool_name in tool_handlers:
        try:
            return {
                "content": tool_handlers[tool_name](arguments),
                "isError": False,
            }
        except Exception as e:
            return {
                "content": {"error": str(e)},
                "isError": True,
            }
    else:
        return {
            "content": {"error": f"Unknown tool: {tool_name}"},
            "isError": True,
        }


# MCP Server initialization
if __name__ == "__main__":
    print("Git Analyzer MCP Server")
    print(f"Repository path: {analyzer.repo_path}")
    
    # Test connection
    branch = analyzer.get_current_branch()
    print(f"Current branch: {branch}")
    
    commits = analyzer.list_commits(max_count=5)
    print(f"Recent commits: {commits['count']}")
    
    status = analyzer.get_repository_status()
    print(f"Repository status: {status.get('branch', 'unknown')}")
    
    print("Ready!")
