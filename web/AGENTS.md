# Web AGENTS.md

**AI Assistant Guide for SvelteKit + Tailwind v4 Frontend Development**

This file provides domain-specific context for AI agents working on the web frontend component of the Docker To-Do App.

---

## 🎯 Frontend Overview

The web frontend is a **SvelteKit 2** application using:
- **Svelte 5 runes** (`$state`, `$derived`, `$effect`, `$props`) for reactive state management
- **Tailwind CSS v4** for utility-first styling
- **TypeScript** for type safety with strict mode
- **Vite** as the bundler with API proxy configuration
- **Bun** as the package manager and runtime
- **nginX** as production server and reverse proxy
- **vitest** for unit testing
- **Playwright** for end-to-end testing

---

## 📁 Web Structure

```text
web/
├── src/                           # Source code
│   ├── app.html                   # HTML shell template
│   ├── app.css                    # Tailwind v4 entry point (@import 'tailwindcss')
│   ├── app.d.ts                   # SvelteKit type augmentation
│   ├── lib/
│   │   ├── api.ts                 # Typed fetch client for API communication with env support
│   │   ├── types.ts               # Shared TypeScript type definitions (Todo, TodoCreate, TodoUpdate, Filter)
│   │   └── components/
│   │       └── TodoItem.svelte    # Individual todo item component with toggle, edit, delete
│   └── routes/
│       ├── +layout.svelte         # Root layout (imports Tailwind CSS)
│       └── +page.svelte           # Main todo list page with state, filters, forms, error handling
├── tests/                         # Frontend tests (vitest)
│   ├── api.test.ts                # API client tests with fetch mocking
│   ├── filter.test.ts             # Filter logic unit tests
│   └── mocks/
│       └── env-public.ts          # Mock environment variables
├── package.json                   # Frontend dependencies and scripts
├── svelte.config.js               # SvelteKit configuration with static adapter
├── vite.config.ts                 # Vite configuration with /api proxy to FastAPI
├── tsconfig.json                  # TypeScript configuration with strict mode
├── nginx.conf                     # Production nginx reverse proxy with /api/* proxy
├── Dockerfile                     # Multi-stage build: Bun + nginx-unprivileged
├── .dockerignore                  # Files excluded from Docker build
├── .env.example                   # Public environment variables template (PUBLIC_API_BASE)
└── .gitignore                     # Git ignore rules for web
```

---

## 🏗️ Architecture

### Component Hierarchy

```text
App
└── +layout.svelte                    # Root layout with Tailwind
    └── +page.svelte                    # Main page
        ├── TodoItem (component)        # Individual todo item
        │   ├── Toggle button
        │   ├── Title (editable)
        │   ├── Description
        │   └── Delete button
        ├── Add Todo Form
        │   ├── Title input
        │   └── Submit button
        ├── Filter Controls
        │   ├── All
        │   ├── Active
        │   └── Completed
        └── Empty State Message
```

### Data Flow

```text
User Action (click, submit, etc.)
     ↓
Svelte Component (handlers)
     ↓
State Update ($state variables)
     ↓
Derived Values ($derived)
     ↓
Side Effects ($effect)
     ↓
API Client (api.ts)
     ↓
Fetch Request to /api (proxied to backend)
     ↓
Response → State Update
     ↓
Reactive UI Update
```

---

## 🎨 UI Components

### TodoItem.svelte

The individual todo item component handles:
- Displaying todo information (title, description, completed status) with strikethrough styling
- Toggling completed status with checkbox
- Inline editing of title and description with form
- Editing with Save/Cancel buttons
- Deleting the todo with confirmation
- Optimistic UI updates with error handling

The component uses Svelte 5 runes for state management:
- `$props()` for component props (todo, onToggle, onSave, onDelete)
- `$state` for local state (editing, draft values)
- Event handlers for user interactions

```svelte
<script lang="ts">
  import type { Todo } from '$lib/types';
  import { api } from '$lib/api';
  
  interface Props {
    todo: Todo;
    onDelete: () => void;
    onUpdate: (updated: Todo) => void;
  }
  
  let { todo, onDelete, onUpdate }: Props = $props();
  
  let isEditing = $state(false);
  let editTitle = $state(todo.title);
  let editDescription = $state(todo.description || '');
  
  const toggleCompleted = async () => {
    const updated = await api.updateTodo(todo.id, {
      completed: !todo.completed
    });
    onUpdate(updated);
  };
  
  const saveEdit = async () => {
    const updated = await api.updateTodo(todo.id, {
      title: editTitle,
      description: editDescription
    });
    onUpdate(updated);
    isEditing = false;
  };
  
  const handleDelete = async () => {
    await api.deleteTodo(todo.id);
    onDelete();
  };
</script>

<li class="flex items-start gap-3 p-3 border-b border-gray-200">
  <input 
    type="checkbox" 
    checked={todo.completed} 
    onchange={toggleCompleted}
    class="mt-1 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
  />
  
  {#if isEditing}
    <div class="flex-1">
      <input 
        type="text" 
        bind:value={editTitle}
        class="w-full p-2 border rounded"
      />
      <textarea 
        bind:value={editDescription}
        class="w-full p-2 border rounded mt-2"
        rows="2"
      />
      <div class="flex gap-2 mt-2">
        <button onclick={saveEdit} class="px-3 py-1 bg-blue-500 text-white rounded">
          Save
        </button>
        <button onclick={() => isEditing = false} class="px-3 py-1 bg-gray-200 rounded">
          Cancel
        </button>
      </div>
    </div>
  {:else}
    <div class="flex-1 min-w-0">
      <h3 class="text-lg font-medium {todo.completed ? 'line-through text-gray-400' : ''}">
        {todo.title}
      </h3>
      {#if todo.description}
        <p class="text-gray-600 {todo.completed ? 'line-through' : ''}">
          {todo.description}
        </p>
      {/if}
    </div>
    <button 
      onclick={() => isEditing = true} 
      class="px-2 py-1 bg-yellow-500 text-white rounded text-sm"
    >
      Edit
    </button>
  {/if}
  
  <button 
    onclick={handleDelete}
    class="px-2 py-1 bg-red-500 text-white rounded text-sm"
  >
    Delete
  </button>
</li>
```

### +page.svelte (Main Page)

The main page manages:
- Todo list state
- Filter state (all/active/completed)
- Loading states
- Error handling
- Form submission for new todos

```svelte
<script lang="ts">
  import { api } from '$lib/api';
  import TodoItem from '$lib/components/TodoItem.svelte';
  import type { Todo } from '$lib/types';
  
  let todos = $state<Todo[]>([]);
  let filter = $state<'all' | 'active' | 'completed'>('all');
  let loading = $state(true);
  let error = $state<string | null>(null);
  let newTodoTitle = $state('');
  
  // Fetch todos on mount
  $effect(() => {
    fetchTodos();
  });
  
  const fetchTodos = async () => {
    loading = true;
    error = null;
    try {
      todos = await api.listTodos();
    } catch (e) {
      error = 'Failed to load todos';
      console.error(e);
    } finally {
      loading = false;
    }
  };
  
  const visibleTodos = $derived.by(() => {
    if (filter === 'active') return todos.filter(t => !t.completed);
    if (filter === 'completed') return todos.filter(t => t.completed);
    return todos;
  });
  
  const handleAddTodo = async (e: Event) => {
    e.preventDefault();
    if (!newTodoTitle.trim()) return;
    
    try {
      const newTodo = await api.createTodo({
        title: newTodoTitle,
        description: '',
        completed: false
      });
      todos = [...todos, newTodo];
      newTodoTitle = '';
    } catch (e) {
      error = 'Failed to create todo';
      console.error(e);
    }
  };
  
  const handleUpdate = (updated: Todo) => {
    todos = todos.map(t => t.id === updated.id ? updated : t);
  };
  
  const handleDelete = (id: number) => {
    todos = todos.filter(t => t.id !== id);
  };
</script>

<svelte:head>
  <title>Todo App</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 p-4 md:p-8">
  <div class="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">Todo App</h1>
    
    <!-- Add Todo Form -->
    <form onsubmit={handleAddTodo} class="mb-6">
      <div class="flex gap-2">
        <input 
          type="text" 
          bind:value={newTodoTitle}
          placeholder="What needs to be done?"
          class="flex-1 p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
        <button 
          type="submit" 
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Add
        </button>
      </div>
    </form>
    
    <!-- Filter Controls -->
    <div class="flex gap-2 mb-4">
      <button 
        onclick={() => filter = 'all'}
        class="px-3 py-1 rounded {filter === 'all' ? 'bg-blue-500 text-white' : 'bg-gray-200'}"
      >
        All
      </button>
      <button 
        onclick={() => filter = 'active'}
        class="px-3 py-1 rounded {filter === 'active' ? 'bg-blue-500 text-white' : 'bg-gray-200'}"
      >
        Active
      </button>
      <button 
        onclick={() => filter = 'completed'}
        class="px-3 py-1 rounded {filter === 'completed' ? 'bg-blue-500 text-white' : 'bg-gray-200'}"
      >
        Completed
      </button>
    </div>
    
    <!-- Loading State -->
    {#if loading}
      <p class="text-gray-500">Loading...</p>
    {:else if error}
      <p class="text-red-500">{error}</p>
      <button onclick={fetchTodos} class="text-blue-500 underline">Retry</button>
    {:else if todos.length === 0}
      <p class="text-gray-500 text-center py-8">
        No todos yet. Add one above!
      </p>
    {:else}
      <p class="text-sm text-gray-500 mb-2">
        {visibleTodos.length} {visibleTodos.length === 1 ? 'todo' : 'todos'}
      </p>
      <ul class="divide-y divide-gray-200">
        {#each visibleTodos as todo}
          <TodoItem 
            {todo} 
            onDelete={() => handleDelete(todo.id)} 
            onUpdate={handleUpdate}
          />
        {/each}
      </ul>
    {/if}
  </div>
</div>
```

---

## 📡 API Client

### api.ts - Typed Fetch Client

The API client provides type-safe communication with the FastAPI backend:

```typescript
// src/lib/api.ts
import type { Todo, TodoCreate, TodoUpdate } from './types';

// Base URL for API requests
// In development: proxied to http://localhost:8000
// In production: via nginx to api service
const BASE = '/api';

// Generic request function with error handling
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(`
      ${res.status} ${res.statusText}: ${errorData.detail || ''}
    `.trim());
  }
  
  // Handle 204 No Content
  if (res.status === 204) return undefined as T;
  
  return res.json() as Promise<T>;
}

// Typed API methods
export const api = {
  // GET /todos - List all todos
  listTodos: () => request<Todo[]>('/todos'),
  
  // GET /todos/{id} - Get single todo
  getTodo: (id: number) => request<Todo>(`/todos/${id}`),
  
  // POST /todos - Create new todo
  createTodo: (payload: TodoCreate) =>
    request<Todo>('/todos', { 
      method: 'POST', 
      body: JSON.stringify(payload) 
    }),
  
  // PUT /todos/{id} - Update todo
  updateTodo: (id: number, payload: TodoUpdate) =>
    request<Todo>(`/todos/${id}`, { 
      method: 'PUT', 
      body: JSON.stringify(payload) 
    }),
  
  // DELETE /todos/{id} - Delete todo
  deleteTodo: (id: number) =>
    request<void>(`/todos/${id}`, { method: 'DELETE' })
};
```

---

## 📝 TypeScript Types

### types.ts - Shared Type Definitions

```typescript
// src/lib/types.ts

// Todo item type (matches API response)
export interface Todo {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string; // ISO 8601 date string
  updated_at: string | null;
}

// Request type for creating a todo
export interface TodoCreate {
  title: string;
  description?: string;
  completed?: boolean;
}

// Request type for updating a todo (all optional)
export interface TodoUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

// Filter type for UI
export type TodoFilter = 'all' | 'active' | 'completed';
```

---

## 🎨 Tailwind CSS v4

### Configuration

Tailwind v4 uses a CSS-first approach with zero configuration required for basic usage:

```css
/* src/app.css */
@import 'tailwindcss';
```

No `tailwind.config.js` is needed for the default token set.

### Design Tokens

The app uses Tailwind's default tokens with the following conventions:

#### Colors
- **Primary**: Blue (`bg-blue-500`, `text-blue-600`)
- **Success**: Green (`bg-green-500`)
- **Warning**: Yellow (`bg-yellow-500`)
- **Danger**: Red (`bg-red-500`)
- **Neutral**: Gray (`bg-gray-100`, `text-gray-600`)

#### Spacing
- Use Tailwind's spacing scale (p-2, p-4, p-6, etc.)
- Container max-width: `max-w-2xl` (42rem)
- Button padding: `px-4 py-2` or `px-3 py-1` for smaller buttons

#### Typography
- Heading 1: `text-2xl font-bold`
- Heading 2: `text-xl font-semibold`
- Body: `text-gray-800`
- Secondary: `text-gray-600`

#### Shadows
- Card shadow: `shadow` (default)
- Hover shadow: `shadow-md` or `shadow-lg`

---

## 🎭 Layout

### Root Layout (+layout.svelte)

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import '../app.css';
</script>

<slot />
```

The root layout:
1. Imports the Tailwind CSS file
2. Wraps all pages with the `<slot />` component
3. Provides consistent styling across the application

### Responsive Design

The app uses Tailwind's responsive prefixes:
- Mobile-first approach
- `md:` prefix for medium screens (768px+)
- `lg:` prefix for large screens (1024px+)

```svelte
<div class="p-4 md:p-8">
  <!-- Narrow padding on mobile, wider on desktop -->
</div>
```

---

## 🔌 Vite Configuration

### vite.config.ts

```typescript
// vite.config.ts
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    tailwindcss(), // Tailwind v4 plugin
    sveltekit()    // SvelteKit plugin
  ],
  server: {
    proxy: {
      // Proxy /api requests to FastAPI during development
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    // Enable HMR on port 5173
    port: 5173,
    strictPort: true
  },
  // Build configuration
  build: {
    // Output directory for build artifacts
    outDir: 'build',
    // Enable sourcemaps
    sourcemap: true
  }
});
```

### Development Proxy

- Requests to `/api/*` are proxied to `http://localhost:8000`
- This allows the frontend to call `/api/todos` which gets forwarded to the API
- No CORS configuration needed in development
- In production, nginx handles the proxy

---

## 📦 SvelteKit Configuration

### svelte.config.js

```javascript
// svelte.config.js
import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Use static adapter for production build
  // Outputs static files that can be served by nginx
  kit: {
    adapter: adapter({
      // Fallback to index.html for SPA routing
      fallback: 'index.html'
    })
  },
  
  // Preprocess Svelte files with TypeScript
  preprocess: vitePreprocess()
};

export default config;
```

---

## 🐳 Docker Configuration

### Dockerfile (Multi-stage Build)

The web Dockerfile uses Bun for building and nginx-unprivileged for serving:

```dockerfile
# Stage 1: build the SvelteKit static output
FROM oven/bun:1-alpine AS builder

WORKDIR /app

# Install dependencies (cached layer, deterministic via lockfile)
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# Build the static site
COPY . ./
RUN bun run build

# Stage 2: serve the build with the non-root nginx variant on port 8080
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY --chown=nginx:nginx nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder --chown=nginx:nginx /app/build /usr/share/nginx/html

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf

Production nginx configuration with proxy and caching:

```nginx
# nginx.conf
server {
    listen 8080;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Proxy /api/* to the FastAPI service (strips the /api prefix)
    location /api/ {
        proxy_pass http://api:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SPA fallback: serve the static index.html for unknown routes
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### docker-compose.yml (Web service)

Web service configuration with proper networking and dependencies:

```yaml
services:
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    networks:
      - traefik_frontend
    depends_on:
      - api
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "0.25"
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

---

## 🧪 Testing

### Test Setup

The frontend uses vitest for unit testing with comprehensive test coverage:

```bash
# Install dependencies
cd web
bun install

# Run tests
bun test

# Run tests in watch mode
bun test:watch

# Type checking
bun run check

# Build for production
bun run build

# Preview production build
bun run preview
```

### Test Files

| File | Purpose | Description |
|------|---------|-------------|
| `tests/api.test.ts` | API client tests | Tests fetch client with mocked responses |
| `tests/filter.test.ts` | Filter logic tests | Tests filtering functions for All/Active/Completed |
| `tests/mocks/env-public.ts` | Mock environment | Mock PUBLIC_API_BASE for testing |

### Example Tests

The API client tests use vi.stubGlobal to mock fetch:

```typescript
// tests/api.test.ts
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { api } from '../src/lib/api';
import type { Todo } from '../src/lib/types';

const sampleTodo: Todo = {
  id: 1,
  title: 'Buy milk',
  description: null,
  completed: false,
  created_at: '2026-04-30T10:00:00Z',
  updated_at: null
};

function jsonResponse(body: unknown, init: ResponseInit = { status: 200 }): Response {
  return new Response(JSON.stringify(body), {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init.headers ?? {}) }
  });
}

describe('api client', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('listTodos calls GET /todos and returns the parsed body', async () => {
    fetchMock.mockResolvedValue(jsonResponse([sampleTodo]));
    const todos = await api.listTodos();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('/api/todos');
    expect(init?.method).toBeUndefined();
    expect(todos).toEqual([sampleTodo]);
  });

  it('createTodo POSTs the payload as JSON', async () => {
    fetchMock.mockResolvedValue(jsonResponse(sampleTodo, { status: 201 }));
    const created = await api.createTodo({ title: 'Buy milk' });
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('/api/todos');
    expect(init?.method).toBe('POST');
    expect(init?.body).toBe(JSON.stringify({ title: 'Buy milk' }));
    expect((init?.headers as Record<string, string>)['Content-Type']).toBe('application/json');
    expect(created).toEqual(sampleTodo);
  });

  it('deleteTodo handles 204 No Content', async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }));
    await expect(api.deleteTodo(1)).resolves.toBeUndefined();
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('/api/todos/1');
    expect(init?.method).toBe('DELETE');
  });

  it('throws when the response is not ok', async () => {
    fetchMock.mockResolvedValue(
      new Response('boom', { status: 500, statusText: 'Internal Server Error' })
    );
    await expect(api.listTodos()).rejects.toThrow(/500/);
  });
});
```

### Filter Logic Tests

The filter logic is tested separately for pure business logic:

```typescript
// tests/filter.test.ts
import { describe, expect, it } from 'vitest';
import type { Filter, Todo } from '../src/lib/types';

function makeTodo(overrides: Partial<Todo>): Todo {
  return {
    id: 1,
    title: 'Sample',
    description: null,
    completed: false,
    created_at: '2026-04-30T10:00:00Z',
    updated_at: null,
    ...overrides
  };
}

function applyFilter(todos: Todo[], filter: Filter): Todo[] {
  if (filter === 'active') return todos.filter((t) => !t.completed);
  if (filter === 'completed') return todos.filter((t) => t.completed);
  return todos;
}

describe('filter logic', () => {
  const todos = [
    makeTodo({ id: 1, title: 'a', completed: false }),
    makeTodo({ id: 2, title: 'b', completed: true }),
    makeTodo({ id: 3, title: 'c', completed: false }),
  ];

  it('returns all todos when filter is "all"', () => {
    expect(applyFilter(todos, 'all')).toHaveLength(3);
  });

  it('returns only active todos when filter is "active"', () => {
    const result = applyFilter(todos, 'active');
    expect(result.map((t) => t.id)).toEqual([1, 3]);
  });

  it('returns only completed todos when filter is "completed"', () => {
    const result = applyFilter(todos, 'completed');
    expect(result.map((t) => t.id)).toEqual([2]);
  });
});
```

---

## 📦 Dependencies

### package.json

```json
{
  "name": "todo-web",
  "private": true,
  "version": "0.1.0",
  "description": "SvelteKit + Tailwind v4 frontend for Docker To-Do App",
  "type": "module",
  "scripts": {
    "dev": "vite dev",
    "build": "vite build",
    "preview": "vite preview",
    "check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json",
    "check:watch": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json --watch",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "@sveltejs/adapter-static": "^3.0.8",
    "@tailwindcss/vite": "^4.0.0",
    "svelte": "^5.16.0",
    "svelte-check": "^4.1.1",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.7.2",
    "vite": "^6.0.7"
  },
  "devDependencies": {
    "@sveltejs/kit": "^2.15.1",
    "@sveltejs/vite-plugin-svelte": "^5.0.3",
    "@vitest/coverage-v8": "2.1.9",
    "svelte": "^5.16.0",
    "svelte-check": "^4.1.1",
    "tslib": "^2.8.1",
    "vitest": "^2.1.8"
  }
}
```

---

## 🔒 Security Considerations

### Environment Variables
- Use `.env` for public environment variables (prefix with `PUBLIC_`)
- Use `.env.example` to document required variables
- Never commit `.env` files

### Security Best Practices
- Sanitize all user input before rendering
- Use `bind:value` instead of direct DOM manipulation
- Avoid `innerHTML` to prevent XSS attacks
- Use HTTPS in production
- Set appropriate CORS headers (handled by nginx in production)

---

## 📝 Common Tasks

### Adding a New Component

1. **Create the component file** in `src/lib/components/`
2. **Use PascalCase** for the filename (`NewComponent.svelte`)
3. **Define props** using `$props()` with TypeScript interface
4. **Use runes** for state management (`$state`, `$derived`, `$effect`)
5. **Style with Tailwind** utility classes

### Adding a New Page

1. **Create the page file** in `src/routes/` (e.g., `about/+page.svelte`)
2. **Add layout** if needed (e.g., `about/+layout.svelte`)
3. **Update navigation** in the main page

### Adding a New API Client Method

1. **Add type** in `src/lib/types.ts` if needed
2. **Add method** to `api` object in `src/lib/api.ts`
3. **Use the method** in components

---

## 🎯 Frontend-Specific Rules

### Svelte 5 Runes

**Always use runes, never use legacy `$:` syntax:**

| Rune | Purpose | Example |
|------|---------|---------|
| `$state` | Reactive state | `let count = $state(0);` |
| `$derived` | Derived values | `let double = $derived(count * 2);` |
| `$derived.by` | Complex derived | `let filtered = $derived.by(() => items.filter(i => i.active));` |
| `$effect` | Side effects | `$effect(() => { console.log(count); });` |
| `$props` | Component props | `let { todo }: Props = $props();` |
| `$inspect` | Debugging | `$inspect(count);` |

**Never use:**
```svelte
<!-- LEGACY - DO NOT USE -->
<script>
  let count = 0;
  $: doubled = count * 2;  // Legacy reactive declaration
</script>

<!-- CORRECT - Use runes -->
<script>
  let count = $state(0);
  let doubled = $derived(count * 2);
</script>
```

### TypeScript

- Always use explicit types at module boundaries
- Use interfaces for component props
- Use type aliases for complex types
- Never use `any` type

### Component Organization

- Keep components small and focused
- Use single-file components for simplicity
- Extract complex logic into separate files if needed
- Use meaningful component names

---

## 📚 Related Documentation

- [Root AGENTS.md](../AGENTS.md) - Main AI assistant guide
- [docs/AGENTS.md](../docs/AGENTS.md) - Extended AI guide
- [docs/TECHNICAL_GUIDE.md](../docs/TECHNICAL_GUIDE.md) - Technical implementation
- [docs/DESIGN_SYSTEM.md](../docs/DESIGN_SYSTEM.md) - UI design system
- [docs/COMPONENT_REFERENCE.md](../docs/COMPONENT_REFERENCE.md) - Component reference
- [README.md](README.md) - Web-specific README

---

*Last updated: 2026-06-26*
*Generated by Mistral Vibe for frontend-specific static context*