# /todo

Manage todo items in the application via the FastAPI backend.

## Usage

```
/todo <action> [args]
```

## Actions

| Action | Description | Example |
|--------|-------------|---------|
| `list` | List all todos | `/todo list` |
| `add <title>` | Create a new todo | `/todo add Buy groceries` |
| `complete <id>` | Mark todo as completed | `/todo complete 3` |
| `delete <id>` | Delete a todo | `/todo delete 3` |
| `update <id> <title>` | Update todo title | `/todo update 3 New title` |
| `status` | Show todo statistics | `/todo status` |
| `reminders <id>` | List reminders for a todo | `/todo reminders 1` |
| `subtasks <id>` | List subtasks for a todo | `/todo subtasks 1` |

## Implementation

When this command is invoked, perform the requested action by calling the appropriate
FastAPI API endpoint at `http://localhost:8000`:

- List: `GET /todos`
- Add: `POST /todos` with `{"title": "<title>"}`
- Complete: `PUT /todos/<id>` with `{"completed": true}`
- Delete: `DELETE /todos/<id>`
- Update: `PUT /todos/<id>` with `{"title": "<new_title>"}`
- Reminders: `GET /todos/<id>/reminders`
- Subtasks: `GET /todos/<id>/subtasks`

Use `curl` or the TypeScript API client in `web/src/lib/api.ts` as a reference.

If the API is not running, suggest starting it with:
```bash
cd api && uv run uvicorn main:app --reload
```
