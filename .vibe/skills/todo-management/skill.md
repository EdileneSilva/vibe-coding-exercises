# Todo Management Skill

**Auto-triggered Skill for Todo-Related Tasks**

This skill is automatically triggered when the user mentions todo-related tasks, todo items, task management, or similar concepts.

---

## 🎯 Purpose

The `todo-management` skill provides specialized assistance for:
- Creating, reading, updating, and deleting todo items
- Managing task lists and projects
- Organizing workflows
- Tracking task status and progress
- Prioritizing and categorizing tasks

---

## 🔍 Trigger Patterns

This skill activates when the user message contains:

### Primary Triggers (High Confidence)
- "todo" or "todos" or "to-do" or "to do"
- "task" or "tasks"
- "create task", "add task", "new task"
- "list tasks", "show tasks", "get tasks"
- "update task", "edit task", "modify task"
- "delete task", "remove task"
- "complete task", "finish task", "mark done"
- "priority", "due date", "deadline"

### Secondary Triggers (Medium Confidence)
- "workflow"
- "backlog"
- "sprint"
- "kanban"
- "agile"
- "scrum"
- "project management"
- "checklist"

### Contextual Triggers
- User is in a project directory with todo-related files
- User mentions specific task management tools (Jira, Trello, etc.)
- User asks about organizing work

---

## 🚀 Capabilities

### Task Creation
- Help create new todo items with proper structure
- Suggest appropriate fields (title, description, priority, due date)
- Validate task data
- Generate task templates

### Task Management
- List and filter tasks
- Update task status, priority, or details
- Delete or archive tasks
- Search for specific tasks
- Bulk operations on tasks

### Task Organization
- Categorize tasks by type, priority, or project
- Create task hierarchies (epics, stories, subtasks)
- Manage task dependencies
- Organize tasks into projects or boards

### Workflow Assistance
- Suggest workflow improvements
- Help implement task automation
- Provide task management best practices
- Integrate with project management tools

---

## 📋 Workflows

### Workflow 1: Create a New Task

**Trigger:** User says "add a new task" or "create todo"

**Steps:**
1. Parse user request for task details
2. Prompt for missing required information (title)
3. Suggest optional fields (description, priority, due date)
4. Generate task structure
5. Provide code to create the task
6. Offer to save to a specific file or database

**Example Interaction:**
```
User: "Add a new task to fix the login bug"

AI (todo-management skill active):
- Title: "Fix login bug"
- Priority: High (bug fix)
- Description: "Investigate and fix the authentication issue reported by users"
- Due date: [Today + 2 days]
- Status: Todo

Would you like me to:
1. Create this as a GitHub issue?
2. Add it to your local task list?
3. Save it to a specific file?
4. Create a branch for this task?

User: "Create a GitHub issue"

AI: [Creates GitHub issue with proper labels and milestone]
```

### Workflow 2: List and Filter Tasks

**Trigger:** User says "list my tasks" or "show todos"

**Steps:**
1. Identify task storage location
2. Retrieve tasks from the appropriate source
3. Filter based on user criteria (priority, status, due date)
4. Format and display results
5. Offer additional filtering or sorting options

**Example Interaction:**
```
User: "Show me all high priority tasks"

AI (todo-management skill active):
Here are your high priority tasks:

1. [Fix login bug] - Due: 2026-06-25 - Status: In Progress
2. [Update documentation] - Due: 2026-06-24 - Status: Todo
3. [Refactor API endpoints] - Due: 2026-06-30 - Status: Todo

Would you like to:
- See details for a specific task?
- Update a task status?
- Filter by another criteria?
```

### Workflow 3: Task Status Update

**Trigger:** User says "mark task as complete" or "update task status"

**Steps:**
1. Identify which task to update
2. Parse new status or changes
3. Validate the update
4. Apply the update to the task storage
5. Confirm the change
6. Offer next steps

**Example Interaction:**
```
User: "Mark task #1 as completed"

AI (todo-management skill active):
- Updating task "Fix login bug" (ID: 1) to status: Completed
- ✅ Task marked as completed

Would you like to:
- Assign this to someone for review?
- Move to the next task?
- View completed tasks?
```

---

## 🛠️ Tools Integration

### File-Based Task Storage
- Read and write task lists from markdown files
- Support YAML or JSON task storage
- Integrate with project-specific task files

### GitHub Integration
- Create, update, and manage GitHub issues
- Work with GitHub Projects
- Manage labels, milestones, and assignees

### Database Integration
- Connect to local databases for task storage
- Support SQLite, PostgreSQL, and other databases
- CRUD operations on task data

### Project Management Tools
- Jira integration
- Trello integration
- Notion integration
- Linear integration

---

## 🎨 Templates

### Task Template
```markdown
## Task: [Title]

**ID:** [auto-generated]
**Status:** Todo | In Progress | Done | Blocked
**Priority:** Low | Medium | High | Critical
**Due Date:** [YYYY-MM-DD]
**Created:** [YYYY-MM-DD]
**Updated:** [YYYY-MM-DD]

### Description
[Detailed description of the task]

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### Notes
[Additional notes, dependencies, or context]

### Checklist
- [ ] Task started
- [ ] Implementation complete
- [ ] Code reviewed
- [ ] Tests written
- [ ] Documentation updated
```

### Project Template
```markdown
# Project: [Project Name]

**Status:** Not Started | In Progress | Completed | On Hold
**Priority:** Low | Medium | High | Critical
**Due Date:** [YYYY-MM-DD]
**Lead:** [Assignee]

## Overview
[Project description and goals]

## Epics
- [Epic 1](#epic-1)
- [Epic 2](#epic-2)

## Tasks

### Epic 1
- [ ] Task 1
- [ ] Task 2

### Epic 2
- [ ] Task 3
- [ ] Task 4

## Dependencies
- [Dependency 1]
- [Dependency 2]

## Notes
[Additional context or resources]
```

---

## 📊 Task Fields

### Standard Fields
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | string | Yes | - | Short, descriptive title |
| `status` | enum | No | Todo | Task state (Todo, In Progress, Done, Blocked) |
| `priority` | enum | No | Medium | Priority level (Low, Medium, High, Critical) |
| `due_date` | date | No | - | ISO 8601 date string |
| `description` | string | No | - | Detailed task description |

### Extended Fields
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `assignee` | string | No | - | Person assigned to the task |
| `labels` | string[] | No | [] | Tags or categories for the task |
| `project` | string | No | - | Project this task belongs to |
| `epic` | string | No | - | Epic this task belongs to |
| `story_points` | number | No | - | Estimate of effort (1-13 for Fibonacci) |
| `dependencies` | string[] | No | [] | Task IDs this task depends on |

---

## 🔧 Configuration

### Skill Configuration

```yaml
# .vibe/skills/todo-management/config.yaml
name: todo-management
version: 1.0.0
description: Todo management and task organization skill
author: Mistral Vibe
enabled: true

triggers:
  primary:
    - todo
    - todos
    - "to-do"
    - task
    - tasks
  secondary:
    - workflow
    - backlog
    - sprint
    - kanban
    - project

settings:
  default_task_status: Todo
  default_priority: Medium
  date_format: YYYY-MM-DD
  storage:
    default: markdown
    supported: [markdown, yaml, json, github, database]
```

---

## 📝 Examples

### Example 1: Simple Task Creation
```
User: "Create a todo to update the README"

AI Response:
Created new task:
- Title: Update README
- Status: Todo
- Priority: Medium

Task saved to todos.md. Would you like to add more details or set a due date?
```

### Example 2: Complex Task with Details
```
User: "Add authentication to the API with JWT tokens, high priority, due Friday"

AI Response:
Created new task:
- Title: Add JWT authentication to API
- Status: Todo
- Priority: High
- Due Date: 2026-06-26 (Friday)
- Description: Implement JWT token-based authentication for all API endpoints
- Labels: [api, authentication, security]
- Story Points: 5

Acceptance Criteria:
- [ ] JWT token generation on login
- [ ] Token validation middleware
- [ ] Protected endpoints require valid token
- [ ] Token refresh mechanism
- [ ] Logout functionality

Would you like me to create a branch for this task or break it down into subtasks?
```

### Example 3: Task List Management
```
User: "Show me all tasks due this week, sorted by priority"

AI Response:
## Tasks Due This Week (Sorted by Priority)

### 🔴 High Priority
1. [Add JWT authentication to API] - Due: 2026-06-26
   - Status: Todo | Story Points: 5
2. [Fix login bug] - Due: 2026-06-25
   - Status: In Progress | Story Points: 3

### 🟡 Medium Priority
3. [Update README] - Due: 2026-06-27
   - Status: Todo | Story Points: 2
4. [Refactor database queries] - Due: 2026-06-28
   - Status: Todo | Story Points: 3

### 🟢 Low Priority
5. [Clean up old code] - Due: 2026-06-27
   - Status: Todo | Story Points: 1

Total: 5 tasks | High: 2 | Medium: 2 | Low: 1
```

---

## 🎯 Best Practices

### Task Creation
- Use clear, actionable titles (start with a verb)
- Include acceptance criteria for complex tasks
- Break large tasks into smaller subtasks
- Estimate effort (story points or time)
- Set realistic due dates

### Task Management
- Regularly review and update task status
- Prioritize tasks based on business value
- Track dependencies between tasks
- Use labels for categorization
- Archive completed tasks

### Workflow Optimization
- Limit work in progress (WIP limits)
- Use pull requests for task completion
- Automate repetitive task management
- Regularly groom the backlog

---

## 🔍 Related Files

- [Root AGENTS.md](../../../AGENTS.md) - Main AI assistant guide
- [api/AGENTS.md](../../../api/AGENTS.md) - API-specific context
- [web/AGENTS.md](../../../web/AGENTS.md) - Frontend-specific context
- [docs/TASKS.md](../../../docs/TASKS.md) - Project task tracking
- [docs/FEATURES.md](../../../docs/FEATURES.md) - Feature management

---

*Last updated: 2026-06-23*
*Generated by Mistral Vibe - Todo Management Skill*