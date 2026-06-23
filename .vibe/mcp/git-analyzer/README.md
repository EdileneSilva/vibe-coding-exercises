# Git Analyzer MCP Server

**Model Context Protocol Server for Git Repository Analysis**

This MCP server provides comprehensive Git repository analysis capabilities for the Docker To-Do App project. It enables AI agents to efficiently navigate, analyze, and understand the project's version control history.

---

## 🎯 Overview

The Git Analyzer MCP Server is designed to:

1. **Analyze** commits, branches, and tags
2. **Search** through commit messages and file contents
3. **View** diffs and changes between revisions
4. **Inspect** repository status and history
5. **Track** file changes over time
6. **Blame** code to find who changed what

---

## 📡 Capabilities

### Core Features

| Feature | Description | Use Case |
|---------|-------------|----------|
| **Repository Info** | Get remotes, HEAD, branch, status | Understanding repo state |
| **Branch Management** | List and inspect branches | Navigating branches |
| **Tag Management** | List and inspect tags | Releasing and versioning |
| **Commit Analysis** | List and inspect commits | Understanding history |
| **Diff Generation** | View changes between commits | Reviewing changes |
| **File History** | Track changes to specific files | Understanding file evolution |
| **Blame Analysis** | Find who changed each line | Code attribution |
| **Search** | Search commits and file contents | Finding relevant changes |

---

## 🛠️ Tools

### Repository Information

#### `git_get_repository_info`
Get comprehensive repository information.

**Parameters:** None

**Returns:**
```json
{
  "path": "/path/to/project",
  "remotes": [
    {"name": "origin", "url": "https://github.com/user/repo.git"}
  ],
  "head_commit": { ... },
  "branch": "main",
  "status": {
    "branch": "main",
    "modified": ["api/main.py"],
    "added": [],
    "deleted": [],
    "untracked": ["new_file.txt"]
  }
}
```

#### `git_get_current_branch`
Get the current branch name.

**Parameters:** None

#### `git_get_repository_status`
Get the repository status (modified, untracked files).

**Parameters:** None

---

### Branch Management

#### `git_list_branches`
List all branches in the repository.

**Parameters:**
- `all` (boolean, optional): Include remote branches
- `remotes` (boolean, optional): Only show remote branches

**Returns:**
```json
{
  "branches": [
    {
      "name": "main",
      "short_hash": "abc1234",
      "date": "2026-06-23T10:00:00Z",
      "subject": "Initial commit"
    }
  ],
  "count": 5
}
```

#### `git_get_branch_info`
Get detailed information about a specific branch.

**Parameters:**
- `branch_name` (string, required): Name of the branch

**Returns:**
```json
{
  "name": "main",
  "commit_count": 150,
  "latest_commit": "abc1234...",
  "latest_commit_info": { ... },
  "tracking": "origin/main",
  "is_current": true
}
```

---

### Tag Management

#### `git_list_tags`
List all tags in the repository.

**Parameters:**
- `sort` (string, optional): Sort order (default: "-creatordate" - newest first)

**Returns:** Same format as branches

#### `git_get_tag_info`
Get detailed information about a specific tag.

**Parameters:**
- `tag_name` (string, required): Name of the tag

**Returns:**
```json
{
  "name": "v1.0.0",
  "commit": "abc1234...",
  "commit_info": { ... },
  "type": "tag" | "commit"
}
```

---

### Commit Analysis

#### `git_list_commits`
List commits in the repository.

**Parameters:**
- `max_count` (integer, optional): Maximum number of commits (default: 20)
- `since` (string, optional): Show commits since this date
- `until` (string, optional): Show commits until this date
- `author` (string, optional): Filter by author
- `grep` (string, optional): Filter by commit message
- `branch` (string, optional): Show commits from this branch

**Returns:**
```json
{
  "commits": [
    {
      "hash": "abc1234...",
      "short_hash": "abc1234",
      "author_name": "John Doe",
      "author_email": "john@example.com",
      "date": "2026-06-23T10:00:00Z",
      "subject": "Add new feature"
    }
  ],
  "count": 20
}
```

#### `git_get_commit_info`
Get detailed information about a specific commit.

**Parameters:**
- `commit_hash` (string, required): Hash of the commit

**Returns:**
```json
{
  "hash": "abc1234...",
  "short_hash": "abc1234",
  "parents": ["def5678..."],
  "author": {
    "name": "John Doe",
    "email": "john@example.com",
    "date": "2026-06-23T10:00:00Z"
  },
  "committer": { ... },
  "message": "Add new feature\n\nThis commit adds the new feature as requested in issue #123",
  "short_message": "Add new feature",
  "tree": "xyz9012...",
  "stats": {
    "files_changed": 5,
    "changes": [
      {"file": "api/main.py", "changes": "10 insertions(+), 2 deletions(-)"}
    ]
  },
  "changed_files": ["api/main.py", "api/models.py", ...]
}
```

#### `git_get_head_commit`
Get information about the HEAD commit.

**Parameters:** None

---

### Diff and History

#### `git_get_diff`
Get the diff between two commits or between commit and working tree.

**Parameters:**
- `commit_a` (string, required): First commit or file
- `commit_b` (string, optional): Second commit (defaults to working tree)
- `path` (string, optional): Optional path to diff

**Returns:**
```json
{
  "from": "abc1234",
  "to": "def5678",
  "path": "api/main.py",
  "diff": "diff --git a/api/main.py b/api/main.py\n...",
  "success": true,
  "error": ""
}
```

#### `git_get_blame`
Get blame information for a file.

**Parameters:**
- `file_path` (string, required): Path to the file
- `commit` (string, optional): Optional commit to blame (defaults to HEAD)

**Returns:**
```json
{
  "file": "api/main.py",
  "blame": [
    {
      "commit": "abc1234",
      "line_number": 1,
      "original_line_number": 1,
      "num_lines": 1,
      "author": "John Doe",
      "author_email": "john@example.com",
      "author_time": 1234567890,
      "committer": "Jane Doe",
      "summary": "Add new endpoint"
    }
  ],
  "count": 50
}
```

#### `git_get_file_history`
Get the history of changes for a specific file.

**Parameters:**
- `file_path` (string, required): Path to the file
- `max_count` (integer, optional): Maximum number of commits (default: 20)

**Returns:**
```json
{
  "file": "api/main.py",
  "commits": [
    {
      "hash": "abc1234",
      "short_hash": "abc1234",
      "author": "John Doe",
      "date": "2026-06-23T10:00:00Z",
      "subject": "Add new endpoint"
    }
  ],
  "count": 10
}
```

---

### Search

#### `git_search_commits`
Search commits by message.

**Parameters:**
- `query` (string, required): Search query
- `max_count` (integer, optional): Maximum number of results (default: 20)

**Returns:** Same format as list_commits

#### `git_search_files`
Search for a string in files (uses git grep).

**Parameters:**
- `query` (string, required): Search query
- `commit` (string, optional): Optional commit to search in

**Returns:**
```json
{
  "matches": [
    {
      "commit": "abc1234",
      "file": "api/main.py",
      "line_number": 42,
      "line": "def get_user_by_id(user_id: int) -> User | None:"
    }
  ],
  "count": 5,
  "query": "get_user"
}
```

---

## 🎯 Use Cases

### 1. Understanding Project History

```python
# Get recent commits
commits = call_tool("git_list_commits", {"max_count": 10})

for commit in commits["commits"]:
    print(f"{commit['short_hash']} - {commit['subject']} ({commit['author_name']})")
```

### 2. Finding Relevant Changes

```python
# Search for commits related to authentication
commits = call_tool("git_search_commits", {
    "query": "auth",
    "max_count": 20
})

# Search for files containing "password"
matches = call_tool("git_search_files", {
    "query": "password"
})
```

### 3. Analyzing File Changes

```python
# Get history of a specific file
 history = call_tool("git_get_file_history", {
     "file_path": "api/main.py",
     "max_count": 10
 })

for commit in history["commits"]:
    print(f"{commit['short_hash']} - {commit['subject']}")

# Get blame for a file
blame = call_tool("git_get_blame", {
    "file_path": "api/main.py"
})

# Find who last modified line 42
for entry in blame["blame"]:
    if entry["line_number"] <= 42 < entry["line_number"] + entry["num_lines"]:
        print(f"Line 42 was last changed by {entry['author']} in commit {entry['commit']}")
        break
```

### 4. Viewing Changes

```python
# Get diff between current and previous commit
info = call_tool("git_get_head_commit", {})
previous_commit = info["parents"][0] if info["parents"] else None

diff = call_tool("git_get_diff", {
    "commit_a": previous_commit,
    "commit_b": info["hash"]
})

print(diff["diff"])
```

---

## 🎯 Project-Specific Information

For the Docker To-Do App project:

- **Main Branch**: `main`
- **Default Remote**: `origin`
- **Commit Convention**: Gitmoji or Conventional Commits
- **Branch Strategy**: Feature branches with rebase workflow

---

## 🚀 Integration

This MCP server is automatically discovered by Mistral Vibe when placed in the `.vibe/mcp/` directory.

### Manual Testing

To test the server manually:

```bash
cd /path/to/project
python .vibe/mcp/git-analyzer/server.py
```

This will:
1. Initialize the Git analyzer
2. Detect repository path
3. Check current branch
4. List recent commits
5. Check repository status
6. Be ready to handle tool calls

---

## 🔒 Security Considerations

1. **Repository Access**: Only accesses the project repository
2. **No Write Operations**: Does not modify the repository
3. **Sensitive Data**: Commit messages and file contents may contain sensitive information
4. **Blame Information**: Blame data reveals author information
5. **History Access**: Full repository history is accessible

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-23 | Initial release | Full Git repository analysis capabilities |

---

## 🎯 Related Files

- [Root AGENTS.md](../../../AGENTS.md) - Main AI assistant guide
- [file-indexer MCP](../file-indexer/README.md) - File system indexing MCP
- [docker-monitor MCP](../docker-monitor/README.md) - Docker monitoring MCP
- [docs/AGENTS.md](../../../docs/AGENTS.md) - Documentation standards

---

## 📚 Additional Information

- [Model Context Protocol (MCP) Specification](https://github.com/modelcontextprotocol/specification)
- [Mistral Vibe Documentation](https://docs.mistral.ai/vibe/)
- [Git Documentation](https://git-scm.com/doc)
- [Git CLI Reference](https://git-scm.com/docs)

---

*Last updated: 2026-06-23*
*Generated by Mistral Vibe - Git Analyzer MCP Server*