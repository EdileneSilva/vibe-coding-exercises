#!/usr/bin/env python3
"""
File Indexer MCP Server

A Model Context Protocol server that provides file system indexing,
search, and retrieval capabilities for the Docker To-Do App project.

This MCP server allows AI agents to:
- Index and search the project file system
- Retrieve file contents and metadata
- Analyze file relationships and dependencies
- Track changes across files
"""

from typing import Any, Optional
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import mimetypes

# MCP Server metadata
MCP_SERVER_NAME = "file-indexer"
MCP_SERVER_VERSION = "1.0.0"

# Project root directory (auto-detected or configured)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Index storage
INDEX_FILE = PROJECT_ROOT / ".vibe" / "mcp" / "file-indexer" / "index.json"


class FileIndexer:
    """Main file indexer class that manages the file index and provides search capabilities."""
    
    def __init__(self, root_path: Path = PROJECT_ROOT):
        self.root_path = root_path
        self.index: dict[str, Any] = {}
        self.load_index()
    
    def load_index(self) -> None:
        """Load the file index from disk."""
        if INDEX_FILE.exists():
            try:
                with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.index = {}
        else:
            self.index = {}
    
    def save_index(self) -> None:
        """Save the file index to disk."""
        try:
            INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except IOError:
            pass  # Silently fail if we can't save
    
    def build_index(self, force: bool = False) -> dict[str, Any]:
        """Build or rebuild the file index.
        
        Args:
            force: If True, rebuild even if index exists
            
        Returns:
            Dictionary containing the file index
        """
        if not force and self.index:
            return self.index
        
        self.index = {
            "metadata": {
                "built_at": datetime.utcnow().isoformat() + "Z",
                "root_path": str(self.root_path),
                "file_count": 0,
                "directories": [],
            },
            "files": {},
            "extensions": {},
            "mime_types": {},
        }
        
        # Walk the project directory
        for root, dirs, files in os.walk(self.root_path):
            # Skip hidden directories and common non-project directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git', '.vibe']]
            
            rel_root = os.path.relpath(root, self.root_path)
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = Path(root) / file
                rel_path = os.path.join(rel_root, file) if rel_root != '.' else file
                
                try:
                    stat = file_path.stat()
                    file_info = self._get_file_info(file_path, stat, rel_path)
                    self.index["files"][rel_path] = file_info
                    
                    # Update extension stats
                    ext = file.split('.')[-1] if '.' in file else ''
                    if ext:
                        self.index["extensions"][ext] = self.index["extensions"].get(ext, 0) + 1
                    
                    # Update MIME type stats
                    mime_type, _ = mimetypes.guess_type(file)
                    if mime_type:
                        self.index["mime_types"][mime_type] = self.index["mime_types"].get(mime_type, 0) + 1
                        
                except (OSError, PermissionError):
                    continue
        
        self.index["metadata"]["file_count"] = len(self.index["files"])
        self.index["metadata"]["directories"] = self._get_directories()
        self.save_index()
        
        return self.index
    
    def _get_file_info(self, file_path: Path, stat, rel_path: str) -> dict[str, Any]:
        """Extract information about a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                first_line = lines[0] if lines else ''
            except (UnicodeDecodeError, IOError):
                content = None
                lines = []
                first_line = ''
        
        # Calculate file hash
        try:
            file_hash = self._calculate_hash(file_path)
        except (OSError, IOError):
            file_hash = None
        
        # Get MIME type
        mime_type, encoding = mimetypes.guess_type(file_path.name)
        
        return {
            "path": rel_path,
            "absolute_path": str(file_path),
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z",
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat() + "Z",
            "is_dir": False,
            "is_file": True,
            "extension": file_path.suffix.lstrip('.') if file_path.suffix else '',
            "mime_type": mime_type,
            "encoding": encoding,
            "hash": file_hash,
            "lines": len(lines) if content else 0,
            "first_line": first_line.strip() if first_line else '',
            "content_length": len(content) if content else 0,
        }
    
    def _calculate_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _get_directories(self) -> list[str]:
        """Get list of directories in the project."""
        directories = set()
        for file_info in self.index.get("files", {}).values():
            path = file_info["path"]
            dir_path = os.path.dirname(path)
            while dir_path:
                directories.add(dir_path)
                dir_path = os.path.dirname(dir_path)
        return sorted(directories)
    
    def search(self, query: str, path: Optional[str] = None, ext: Optional[str] = None, 
               max_results: int = 50) -> list[dict[str, Any]]:
        """Search for files in the index.
        
        Args:
            query: Search query (file name or content)
            path: Optional path filter
            ext: Optional file extension filter
            max_results: Maximum number of results to return
            
        Returns:
            List of matching file information
        """
        results = []
        query_lower = query.lower()
        
        for file_path, file_info in self.index.get("files", {}).items():
            # Filter by path
            if path and path not in file_path and not file_path.startswith(path + '/'):
                continue
            
            # Filter by extension
            if ext and file_info.get("extension") != ext:
                continue
            
            # Search in file name
            if query_lower in file_path.lower():
                results.append({**file_info, "score": 1.0})
                continue
            
            # Search in first line (for shebang, imports, etc.)
            first_line = file_info.get("first_line", "").lower()
            if query_lower in first_line:
                results.append({**file_info, "score": 0.8})
                continue
        
        # Sort by score and return
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:max_results]
    
    def get_file(self, path: str) -> dict[str, Any]:
        """Get information about a specific file.
        
        Args:
            path: Relative or absolute file path
            
        Returns:
            File information dictionary
        """
        # Normalize path
        if os.path.isabs(path):
            rel_path = os.path.relpath(path, self.root_path)
        else:
            rel_path = path
        
        if rel_path in self.index.get("files", {}):
            return self.index["files"][rel_path]
        
        # File not in index, try to get info directly
        file_path = self.root_path / rel_path
        if file_path.exists():
            try:
                stat = file_path.stat()
                return self._get_file_info(file_path, stat, rel_path)
            except (OSError, PermissionError):
                pass
        
        return {"error": "File not found", "path": path}
    
    def read_file(self, path: str, limit: int = 10000) -> dict[str, Any]:
        """Read the content of a file.
        
        Args:
            path: Relative or absolute file path
            limit: Maximum bytes to read (default: 10KB)
            
        Returns:
            Dictionary with file content and metadata
        """
        # Normalize path
        if os.path.isabs(path):
            file_path = Path(path)
        else:
            file_path = self.root_path / path
        
        if not file_path.exists():
            return {"error": "File not found", "path": str(file_path)}
        
        if not file_path.is_file():
            return {"error": "Not a file", "path": str(file_path)}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(limit)
                if file_path.stat().st_size > limit:
                    truncated = True
                else:
                    truncated = False
        except UnicodeDecodeError:
            # Try as binary
            try:
                with open(file_path, 'rb') as f:
                    content = f.read(limit).decode('latin-1')
                    truncated = file_path.stat().st_size > limit
            except (IOError, OSError):
                return {"error": "Cannot read file", "path": str(file_path)}
        except (IOError, OSError):
            return {"error": "Cannot read file", "path": str(file_path)}
        
        return {
            "path": str(file_path),
            "relative_path": os.path.relpath(file_path, self.root_path),
            "content": content,
            "truncated": truncated,
            "size": file_path.stat().st_size,
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat() + "Z",
        }
    
    def list_files(self, path: str = ".", recursive: bool = True, 
                   include_dirs: bool = False) -> list[dict[str, Any]]:
        """List files in a directory.
        
        Args:
            path: Directory path (relative to project root)
            recursive: Whether to list recursively
            include_dirs: Whether to include directories in results
            
        Returns:
            List of file information dictionaries
        """
        # Normalize path
        if os.path.isabs(path):
            base_path = Path(path)
        else:
            base_path = self.root_path / path
        
        if not base_path.exists():
            return []
        
        results = []
        
        for root, dirs, files in os.walk(base_path):
            rel_root = os.path.relpath(root, self.root_path)
            
            # Add directories if requested
            if include_dirs:
                for d in dirs:
                    if not d.startswith('.'):
                        results.append({
                            "path": os.path.join(rel_root, d) if rel_root != '.' else d,
                            "absolute_path": os.path.join(root, d),
                            "is_dir": True,
                            "is_file": False,
                            "name": d,
                        })
            
            # Add files
            for file in files:
                if not file.startswith('.'):
                    file_path = Path(root) / file
                    try:
                        stat = file_path.stat()
                        results.append({
                            "path": os.path.join(rel_root, file) if rel_root != '.' else file,
                            "absolute_path": str(file_path),
                            "is_dir": False,
                            "is_file": True,
                            "name": file,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
                        })
                    except (OSError, PermissionError):
                        continue
            
            if not recursive:
                break
        
        return results
    
    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the indexed files.
        
        Returns:
            Dictionary with file statistics
        """
        return {
            "total_files": len(self.index.get("files", {})),
            "extensions": self.index.get("extensions", {}),
            "mime_types": self.index.get("mime_types", {}),
            "directories": len(self.index.get("metadata", {}).get("directories", [])),
            "last_updated": self.index.get("metadata", {}).get("built_at", ""),
        }


# Initialize the file indexer
indexer = FileIndexer()


def get_tools() -> list[dict[str, Any]]:
    """Get the list of MCP tools provided by this server."""
    return [
        {
            "name": "file_indexer_search",
            "description": "Search for files in the project by name or content",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (file name or content pattern)",
                    },
                    "path": {
                        "type": "string",
                        "description": "Optional path filter (directory to search in)",
                        "default": None,
                    },
                    "ext": {
                        "type": "string",
                        "description": "Optional file extension filter",
                        "default": None,
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 50,
                        "minimum": 1,
                        "maximum": 500,
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "file_indexer_get_file",
            "description": "Get metadata about a specific file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path (relative or absolute)",
                    },
                },
                "required": ["path"],
            },
        },
        {
            "name": "file_indexer_read_file",
            "description": "Read the content of a file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path (relative or absolute)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum bytes to read (default: 10KB)",
                        "default": 10000,
                        "minimum": 1,
                        "maximum": 1000000,
                    },
                },
                "required": ["path"],
            },
        },
        {
            "name": "file_indexer_list_files",
            "description": "List files in a directory",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path (relative to project root)",
                        "default": ".",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to list recursively",
                        "default": True,
                    },
                    "include_dirs": {
                        "type": "boolean",
                        "description": "Whether to include directories in results",
                        "default": False,
                    },
                },
            },
        },
        {
            "name": "file_indexer_get_stats",
            "description": "Get statistics about indexed files",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "file_indexer_build",
            "description": "Build or rebuild the file index",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "force": {
                        "type": "boolean",
                        "description": "If True, rebuild even if index exists",
                        "default": False,
                    },
                },
            },
        },
    ]


def get_resources() -> list[dict[str, Any]]:
    """Get the list of MCP resources provided by this server."""
    return [
        {
            "uri": f"file://{PROJECT_ROOT}/",
            "name": "Project Root",
            "description": "Root directory of the Docker To-Do App project",
            "mimeType": "text/directory",
        },
        {
            "uri": f"file://{PROJECT_ROOT}/api/",
            "name": "API Directory",
            "description": "FastAPI backend source code",
            "mimeType": "text/directory",
        },
        {
            "uri": f"file://{PROJECT_ROOT}/web/",
            "name": "Web Directory", 
            "description": "SvelteKit frontend source code",
            "mimeType": "text/directory",
        },
        {
            "uri": f"file://{PROJECT_ROOT}/docs/",
            "name": "Docs Directory",
            "description": "Project documentation",
            "mimeType": "text/directory",
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
        "file_indexer_search": lambda args: {
            "results": indexer.search(
                query=args.get("query", ""),
                path=args.get("path"),
                ext=args.get("ext"),
                max_results=args.get("max_results", 50),
            )
        },
        "file_indexer_get_file": lambda args: {
            "file": indexer.get_file(args.get("path", ""))
        },
        "file_indexer_read_file": lambda args: {
            "file": indexer.read_file(
                path=args.get("path", ""),
                limit=args.get("limit", 10000),
            )
        },
        "file_indexer_list_files": lambda args: {
            "files": indexer.list_files(
                path=args.get("path", "."),
                recursive=args.get("recursive", True),
                include_dirs=args.get("include_dirs", False),
            )
        },
        "file_indexer_get_stats": lambda args: indexer.get_stats(),
        "file_indexer_build": lambda args: {
            "index": indexer.build_index(force=args.get("force", False)),
            "message": "Index built successfully",
        },
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
    # This would normally be integrated with the Mistral Vibe MCP server
    # For standalone testing, we can provide a simple interface
    print("File Indexer MCP Server")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Index file: {INDEX_FILE}")
    
    # Build initial index
    print("Building initial index...")
    stats = indexer.build_index()
    print(f"Indexed {stats['metadata']['file_count']} files")
    print("Ready!")
