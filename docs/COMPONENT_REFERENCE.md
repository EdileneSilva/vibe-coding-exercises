# Component Reference

Complete technical reference for API endpoints, data models, and Svelte components.

## Table of Contents

- [API Endpoints](#api-endpoints)
- [Health Check Endpoints](#health-check-endpoints)
- [Data Models](#data-models)
- [Svelte Components](#svelte-components)

---

## API Endpoints

Base URL: `http://localhost:8000` (proxied via `/api` from the SvelteKit dev server in development).

### Health Check Endpoints

The API provides monitoring endpoints for observability:

#### GET /health

Basic service health check.

**Response** `200 OK`:
```json
{
  "status": "healthy",
  "timestamp": "2026-06-26T10:00:00Z",
  "service": "todo-api",
  "version": "0.1.0"
}
```

#### GET /health/db

Database connectivity health check.

**Response** `200 OK`:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-06-26T10:00:00Z"
}
```

**Response** `503 Service Unavailable`:
```json
{
  "detail": "Database connection failed: <error_message>"
}
```

#### GET /metrics

Application metrics and statistics.

**Response** `200 OK`:
```json
{
  "metrics": {
    "todos_total": 5,
    "api_uptime": "up"
  },
  "timestamp": "2026-06-26T10:00:00Z"
}
```

---

### Todo CRUD Endpoints

### GET /todos

List all tasks.

| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| - | - | - | No parameters |

**Response** `200 OK`:

```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-04-25T10:00:00Z",
    "updated_at": null
  }
]
```

---

### GET /todos/{todo_id}

Get a specific task by ID.

| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| `todo_id` | `int` | Path | Task ID |

**Response** `200 OK`: Single todo object.

**Response** `404 Not Found`:

```json
{ "detail": "Todo not found" }
```

---

### POST /todos

Create a new task.

**Request body**:

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | Yes | - | Task title (max 200 chars) |
| `description` | `string` | No | `null` | Task description (max 500 chars) |
| `completed` | `boolean` | No | `false` | Task completion status |

**Response** `201 Created`: Created todo object.

---

### PUT /todos/{todo_id}

Update an existing task.

| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| `todo_id` | `int` | Path | Task ID |

**Request body** (all fields optional):

```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```

**Response** `200 OK`: Updated todo object.

**Response** `404 Not Found`:

```json
{ "detail": "Todo not found" }
```

---

### DELETE /todos/{todo_id}

Delete a task.

| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| `todo_id` | `int` | Path | Task ID |

**Response** `204 No Content`: Task deleted (no body).

**Response** `404 Not Found`:

```json
{ "detail": "Todo not found" }
```

---

## Data Models

### SQLAlchemy Model (Todo)

```python
class Todo(Base):
    __tablename__ = "todos"

    id: int              # Primary key, auto-increment
    title: str           # Max 200 chars, not null
    description: str     # Max 500 chars, nullable
    completed: bool      # Default: False
    created_at: datetime # Auto-set on creation
    updated_at: datetime # Auto-set on update
```

### Pydantic Schemas

#### TodoCreate (Request)

```python
class TodoCreate(BaseModel):
    title: str                       # Required, 1..200 chars
    description: str | None = None   # Optional, max 500 chars
    completed: bool = False          # Default: False
```

#### TodoUpdate (Request)

```python
class TodoUpdate(BaseModel):
    title: str | None = None         # Optional
    description: str | None = None   # Optional
    completed: bool | None = None    # Optional
```

#### TodoResponse (Response)

```python
class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
```

### TypeScript Types (`web/src/lib/types.ts`)

```ts
export interface Todo {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface TodoCreate {
  title: string;
  description?: string | null;
  completed?: boolean;
}

export interface TodoUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
}

export type Filter = 'all' | 'active' | 'completed';
```

---

## Svelte Components

### Page Layout (`web/src/routes/+page.svelte`)

The main page owns the list state and orchestrates filters, the create form, and per-item actions.

```svelte
<script lang="ts">
  import { api } from '$lib/api';
  import TodoItem from '$lib/components/TodoItem.svelte';
  import type { Filter, Todo, TodoUpdate } from '$lib/types';

  let todos = $state<Todo[]>([]);
  let filter = $state<Filter>('all');
  let newTitle = $state('');

  const visibleTodos = $derived.by(() => {
    if (filter === 'active') return todos.filter((t) => !t.completed);
    if (filter === 'completed') return todos.filter((t) => t.completed);
    return todos;
  });

  async function createTodo(e: Event) {
    e.preventDefault();
    const title = newTitle.trim();
    if (!title) return;
    const created = await api.createTodo({ title });
    todos = [created, ...todos];
    newTitle = '';
  }

  async function toggleTodo(id: number, completed: boolean) {
    todos = todos.map((t) => (t.id === id ? { ...t, completed } : t));
    await api.updateTodo(id, { completed });
  }

  async function deleteTodo(id: number) {
    todos = todos.filter((t) => t.id !== id);
    await api.deleteTodo(id);
  }

  $effect(() => {
    api.listTodos().then((list) => (todos = list));
  });
</script>

<form onsubmit={createTodo}>
  <input bind:value={newTitle} placeholder="What needs to be done?" required />
  <button type="submit">Add</button>
</form>

<ul>
  {#each visibleTodos as todo (todo.id)}
    <TodoItem
      {todo}
      onToggle={toggleTodo}
      onSave={(id, patch) => api.updateTodo(id, patch)}
      onDelete={deleteTodo}
    />
  {/each}
</ul>
```

### Task Row (`web/src/lib/components/TodoItem.svelte`)

Owns the inline-edit state for a single task. Receives the parent's mutation callbacks via `$props`.

```svelte
<script lang="ts">
  import type { Todo, TodoUpdate } from '$lib/types';

  interface Props {
    todo: Todo;
    onToggle: (id: number, completed: boolean) => void | Promise<void>;
    onSave: (id: number, patch: TodoUpdate) => void | Promise<void>;
    onDelete: (id: number) => void | Promise<void>;
  }

  let { todo, onToggle, onSave, onDelete }: Props = $props();

  let editing = $state(false);
  let titleDraft = $state('');
  let descriptionDraft = $state('');

  function startEdit() {
    titleDraft = todo.title;
    descriptionDraft = todo.description ?? '';
    editing = true;
  }
</script>
```

### Typed Fetch Client (`web/src/lib/api.ts`)

```ts
import type { Todo, TodoCreate, TodoUpdate } from './types';

const BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  listTodos: () => request<Todo[]>('/todos'),
  getTodo: (id: number) => request<Todo>(`/todos/${id}`),
  createTodo: (payload: TodoCreate) =>
    request<Todo>('/todos', { method: 'POST', body: JSON.stringify(payload) }),
  updateTodo: (id: number, payload: TodoUpdate) =>
    request<Todo>(`/todos/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteTodo: (id: number) => request<void>(`/todos/${id}`, { method: 'DELETE' })
};
```

---

*Last updated: 2026-06-26*
