# File Indexer MCP Server

**Model Context Protocol Server for File System Indexing and Search**

This MCP server provides comprehensive file system indexing, search, and retrieval capabilities for the Docker To-Do App project. It enables AI agents to efficiently navigate, search, and analyze the project's file structure.

---

## 🎯 Overview

The File Indexer MCP Server is designed to:

1. **Index** all project files for fast search and retrieval
2. **Search** files by name, content, extension, or path
3. **Retrieve** file contents and metadata on demand
4. **Analyze** file relationships and project structure
5. **Track** file changes and provide statistics

---

## 📡 Capabilities

### Core Features

| Feature | Description | Use Case |
|---------|-------------|----------|
| **File Indexing** | Builds a comprehensive index of all project files | Fast file lookup and search |
| **File Search** | Search files by name, content patterns, or metadata | Finding specific files or code |
| **File Retrieval** | Read file contents with configurable limits | Reading source code or documentation |
| **Directory Listing** | List files and directories with metadata | Browsing project structure |
| **File Statistics** | Get statistics about file types, extensions, sizes | Understanding project composition |
| **File Metadata** | Get detailed information about files | Understanding file properties |

### Advanced Features

- **Content-Aware Search**: Search not just file names, but also file contents (first line for efficiency)
- **Filtering**: Filter by path, file extension, or other criteria
- **Caching**: Persistent index stored on disk for fast access
- **Hashing**: SHA-256 hashes for file content verification
- **MIME Type Detection**: Automatic detection of file types
- **Change Tracking**: Track when files were modified

---

## 🛠️ Tools

### `file_indexer_search`

Search for files in the project.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query (file name or content pattern) |
| `path` | string | No | null | Optional path filter (directory to search in) |
| `ext` | string | No | null | Optional file extension filter |
| `max_results` | integer | No | 50 | Maximum number of results to return (1-500) |

**Returns:**
```json
{
  "results": [
    {
      "path": "api/main.py",
      "absolute_path": "/path/to/project/api/main.py",
      "size": 1234,
      "created": "2026-06-23T10:00:00Z",
      "modified": "2026-06-23T15:30:00Z",
      "accessed": "2026-06-23T16:00:00Z",
      "is_dir": false,
      "is_file": true,
      "extension": "py",
      "mime_type": "text/x-python",
      "encoding": null,
      "hash": "sha256:abc123...",
      "lines": 45,
      "first_line": "from fastapi import FastAPI",
      "content_length": 1234,
      "score": 1.0
    }
  ]
}
```

**Example Usage:**
```python
# Find all Python files in the api directory
results = call_tool("file_indexer_search", {
    "query": "",
    "path": "api",
    "ext": "py",
    "max_results": 100
})

# Search for files containing "todo" in their name
results = call_tool("file_indexer_search", {
    "query": "todo",
    "max_results": 20
})

# Find files that import fastapi
results = call_tool("file_indexer_search", {
    "query": "from fastapi",
    "max_results": 10
})
```

---

### `file_indexer_get_file`

Get metadata about a specific file.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | Yes | - | File path (relative or absolute) |

**Returns:**
```json
{
  "file": {
    "path": "api/main.py",
    "absolute_path": "/path/to/project/api/main.py",
    "size": 1234,
    "created": "2026-06-23T10:00:00Z",
    "modified": "2026-06-23T15:30:00Z",
    "accessed": "2026-06-23T16:00:00Z",
    "is_dir": false,
    "is_file": true,
    "extension": "py",
    "mime_type": "text/x-python",
    "encoding": null,
    "hash": "sha256:abc123...",
    "lines": 45,
    "first_line": "from fastapi import FastAPI",
    "content_length": 1234
  }
}
```

**Example Usage:**
```python
# Get info about a specific file
file_info = call_tool("file_indexer_get_file", {
    "path": "api/main.py"
})

# Check if a file exists and get its size
file_info = call_tool("file_indexer_get_file", {
    "path": "docs/README.md"
})
```

---

### `file_indexer_read_file`

Read the content of a file.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | Yes | - | File path (relative or absolute) |
| `limit` | integer | No | 10000 | Maximum bytes to read (1-1,000,000) |

**Returns:**
```json
{
  "file": {
    "path": "/path/to/project/api/main.py",
    "relative_path": "api/main.py",
    "content": "from fastapi import FastAPI\n...",
    "truncated": false,
    "size": 1234,
    "modified": "2026-06-23T15:30:00Z"
  }
}
```

**Example Usage:**
```python
# Read a Python file
file_content = call_tool("file_indexer_read_file", {
    "path": "api/main.py",
    "limit": 50000
})

# Read the first part of a large file
partial_content = call_tool("file_indexer_read_file", {
    "path": "web/package.json",
    "limit": 1000
})

# Read a configuration file
config = call_tool("file_indexer_read_file", {
    "path": "docker-compose.yml"
})
```

---

### `file_indexer_list_files`

List files in a directory.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | No | "." | Directory path (relative to project root) |
| `recursive` | boolean | No | true | Whether to list recursively |
| `include_dirs` | boolean | No | false | Whether to include directories in results |

**Returns:**
```json
{
  "files": [
    {
      "path": "api/main.py",
      "absolute_path": "/path/to/project/api/main.py",
      "is_dir": false,
      "is_file": true,
      "name": "main.py",
      "size": 1234,
      "modified": "2026-06-23T15:30:00Z"
    }
  ]
}
```

**Example Usage:**
```python
# List all files in the api directory
files = call_tool("file_indexer_list_files", {
    "path": "api",
    "recursive": false
})

# List all files in the project recursively
all_files = call_tool("file_indexer_list_files", {
    "path": ".",
    "recursive": true
})

# List directories in the project
all_dirs = call_tool("file_indexer_list_files", {
    "path": ".",
    "recursive": true,
    "include_dirs": true
})
```

---

### `file_indexer_get_stats`

Get statistics about indexed files.

**Parameters:** None

**Returns:**
```json
{
  "total_files": 150,
  "extensions": {
    "py": 45,
    "ts": 30,
    "svelte": 15,
    "md": 20,
    "json": 10,
    "yaml": 5,
    "css": 5,
    "html": 5,
    "js": 5,
    "toml": 2,
    "lock": 3,
    "Dockerfile": 2
  },
  "mime_types": {
    "text/x-python": 45,
    "application/typescript": 30,
    "text/markdown": 20,
    "application/json": 10
  },
  "directories": 25,
  "last_updated": "2026-06-23T16:00:00Z"
}
```

**Example Usage:**
```python
# Get project statistics
stats = call_tool("file_indexer_get_stats", {})
print(f"Total files: {stats['total_files']}")
print(f"Python files: {stats['extensions']['py']}")
```

---

### `file_indexer_build`

Build or rebuild the file index.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `force` | boolean | No | false | If True, rebuild even if index exists |

**Returns:**
```json
{
  "index": {
    "metadata": {
      "built_at": "2026-06-23T16:00:00Z",
      "root_path": "/path/to/project",
      "file_count": 150,
      "directories": ["api", "web", "docs", ...]
    },
    "files": { ... },
    "extensions": { ... },
    "mime_types": { ... }
  },
  "message": "Index built successfully"
}
```

**Example Usage:**
```python
# Rebuild the index
result = call_tool("file_indexer_build", {
    "force": true
})

# Build index only if it doesn't exist
result = call_tool("file_indexer_build", {})
```

---

## 📚 Resources

This MCP server also provides static resources that can be accessed directly:

| URI | Name | Description | MIME Type |
|-----|------|-------------|-----------|
| `file:///path/to/project/` | Project Root | Root directory of the Docker To-Do App project | text/directory |
| `file:///path/to/project/api/` | API Directory | FastAPI backend source code | text/directory |
| `file:///path/to/project/web/` | Web Directory | SvelteKit frontend source code | text/directory |
| `file:///path/to/project/docs/` | Docs Directory | Project documentation | text/directory |

---

## 🎯 Use Cases

### 1. Finding Project Files

```python
# Find all test files
result = call_tool("file_indexer_search", {
    "query": "test",
    "max_results": 100
})

# Find all API endpoint files
result = call_tool("file_indexer_search", {
    "path": "api",
    "query": "@app.get\|@app.post\|@app.put\|@app.delete",
    "max_results": 50
})
```

### 2. Reading Source Code

```python
# Read the main API file
content = call_tool("file_indexer_read_file", {
    "path": "api/main.py"
})

# Read a Svelte component
component = call_tool("file_indexer_read_file", {
    "path": "web/src/lib/components/TodoItem.svelte"
})
```

### 3. Understanding Project Structure

```python
# Get project statistics
stats = call_tool("file_indexer_get_stats", {})

# List all Python files in the project
py_files = call_tool("file_indexer_list_files", {
    "path": ".",
    "recursive": true
})
# Filter for .py files
py_files = [f for f in py_files["files"] if f["name"].endswith(".py")]
```

### 4. Analyzing Dependencies

```python
# Find all files that import from fastapi
fastapi_files = call_tool("file_indexer_search", {
    "query": "from fastapi",
    "max_results": 50
})

# Find all files that use SQLAlchemy
sql_files = call_tool("file_indexer_search", {
    "query": "from sqlalchemy",
    "max_results": 50
})
```

---

## 🔧 Configuration

The File Indexer MCP Server can be configured with the following options:

```python
# In server.py
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # Auto-detected
INDEX_FILE = PROJECT_ROOT / ".vibe" / "mcp" / "file-indexer" / "index.json"

# To customize the project root:
# PROJECT_ROOT = Path("/custom/path/to/project")

# To customize the index file location:
# INDEX_FILE = Path("/custom/path/to/index.json")
```

### Index Storage

The index is stored as a JSON file at `.vibe/mcp/file-indexer/index.json`. It contains:
- File metadata (paths, sizes, timestamps)
- File hashes (SHA-256)
- File extensions statistics
- MIME type statistics
- Directory structure

### Performance Considerations

- **Index Building**: Building the initial index can take several seconds for large projects
- **Memory Usage**: The index is kept in memory for fast access
- **Disk I/O**: File hashes are computed when building the index
- **Caching**: The index is saved to disk and loaded on startup

---

## 📁 File Structure

```text
.vibe/mcp/file-indexer/
├── server.py           # Main MCP server implementation
├── README.md          # This documentation file
├── index.json         # Persistent file index (generated)
└── __init__.py        # Package initialization (optional)
```

---

## 🚀 Integration

This MCP server is automatically discovered by Mistral Vibe when placed in the `.vibe/mcp/` directory. It integrates with the AI agent to provide file system capabilities.

### Manual Testing

To test the server manually:

```bash
cd /path/to/project
python .vibe/mcp/file-indexer/server.py
```

This will:
1. Initialize the file indexer
2. Build the index
3. Print statistics
4. Be ready to handle tool calls

### Using with Mistral Vibe

The server is automatically loaded when Mistral Vibe starts. AI agents can then use the provided tools to interact with the project's file system.

---

## 📊 Statistics Example

For the Docker To-Do App project, the indexer will typically find:

- **Total Files**: ~150-200 files
- **Python Files**: ~40-50 files (api/ directory)
- **TypeScript Files**: ~30-40 files (web/ directory)
- **Svelte Files**: ~10-20 files (web/src/)
- **Markdown Files**: ~15-20 files (docs/)
- **Configuration Files**: ~10-15 files (various formats)
- **Directories**: ~20-30 directories

---

## 🔒 Security Considerations

1. **File Access**: The server only indexes and reads files within the project root
2. **No Write Operations**: The server does not modify any files
3. **Path Normalization**: All paths are normalized to prevent directory traversal
4. **Error Handling**: Files that can't be read are silently skipped
5. **Content Limits**: File reading has configurable limits to prevent large file issues

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-23 | Initial release | Full file indexing and search capabilities |

---

## 🎯 Related Files

- [Root AGENTS.md](../../../AGENTS.md) - Main AI assistant guide
- [docker-monitor MCP](../docker-monitor/README.md) - Docker monitoring MCP
- [git-analyzer MCP](../git-analyzer/README.md) - Git analysis MCP
- [docs/AGENTS.md](../../../docs/AGENTS.md) - Documentation standards

---

## 📚 Additional Information

- [Model Context Protocol (MCP) Specification](https://github.com/modelcontextprotocol/specification)
- [Mistral Vibe Documentation](https://docs.mistral.ai/vibe/)
- [Python MCP Server Examples](https://github.com/modelcontextprotocol/servers)

---

*Last updated: 2026-06-23*
*Generated by Mistral Vibe - File Indexer MCP Server*