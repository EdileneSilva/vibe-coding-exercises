# Web AGENTS.md

**AI Assistant Guide for SvelteKit + Tailwind v4 Frontend Development**

This file provides domain-specific context for AI agents working on the web frontend component of the Docker To-Do App.

---

## 🎯 Frontend Overview

The web frontend is a **SvelteKit 2** application using:
- **Svelte 5 runes** for reactive state management
- **Tailwind CSS v4** for styling
- **TypeScript** for type safety
- **Vite** as the bundler
- **Bun** as the package manager and runtime
- **nginX** as production server and reverse proxy

---

## 📁 Web Structure

```text
web/
├── src/                           # Source code
│   ├── app.html                   # HTML shell template
│   ├── app.css                    # Tailwind v4 entry point (@import 'tailwindcss')
│   ├── app.d.ts                   # SvelteKit type augmentation
│   ├── lib/
│   │   ├── api.ts                 # Typed fetch client for API communication
│   │   ├── types.ts               # Shared TypeScript type definitions
│   │   └── components/
│   │       └── TodoItem.svelte    # Individual todo item component
│   └── routes/
│       ├── +layout.svelte         # Root layout (imports Tailwind CSS)
│       └── +page.svelte           # Main todo list page
├── tests/                         # Frontend tests
│   ├── test_api.ts                # API client tests
│   └── test_page.svelte           # Page component tests
├── package.json                   # Frontend dependencies and scripts
├── svelte.config.js               # SvelteKit configuration
├── vite.config.ts                 # Vite configuration with /api proxy
├── tsconfig.json                  # TypeScript configuration
├── nginx.conf                     # Production nginx configuration
├── Dockerfile                     # Multi-stage build: Bun + nginx
├── .dockerignore                  # Files excluded from Docker build
├── .env.example                   # Public environment variables template
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
- Displaying todo information (title, description, completed status)
- Toggling completed status
- Inline editing of title and description
- Deleting the todo

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

```dockerfile
# Stage 1: Build the application
FROM node:20-slim AS builder

WORKDIR /app

# Copy package files first for caching
COPY package.json bun.lock ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN bun run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Proxy API requests to the API service
    location /api/ {
        proxy_pass http://api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Serve static files
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### docker-compose.yml (Web service)

```yaml
services:
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    container_name: todo-web
    restart: unless-stopped
    ports:
      - "8080:80"
    networks:
      - traefik_frontend
      - traefik_backend
    depends_on:
      api:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

---

## 🧪 Testing

### Test Setup

```bash
# Install dependencies
cd web
bun install

# Run tests
bun test

# Run tests in watch mode
bun test --watch

# Type checking
bun run check

# Build for production
bun run build

# Preview production build
bun run preview
```

### Example Tests

```typescript
// tests/test_api.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { api } from '$lib/api';

// Mock fetch globally
vi.stubGlobal('fetch', async (url: string, init?: RequestInit) => {
  // Mock responses based on URL and method
  if (url.includes('/todos') && (!init || init.method === 'GET')) {
    return {
      ok: true,
      status: 200,
      json: async () => [
        { id: 1, title: 'Test todo', completed: false, created_at: new Date().toISOString(), updated_at: null }
      ]
    };
  }
  throw new Error('Unexpected request');
});

describe('api client', () => {
  it('should list todos', async () => {
    const todos = await api.listTodos();
    expect(todos).toHaveLength(1);
    expect(todos[0].title).toBe('Test todo');
  });
});
```

---

## 📦 Dependencies

### package.json

```json
{
  "name": "todo-web",
  "version": "0.1.0",
  "description": "SvelteKit + Tailwind v4 frontend for Docker To-Do App",
  "scripts": {
    "dev": "vite dev",
    "build": "svelte-kit sync && vite build",
    "preview": "vite preview",
    "check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "@sveltejs/adapter-static": "^2.15.0",
    "@tailwindcss/vite": "^4.0.0",
    "svelte": "^5.16.0",
    "svelte-check": "^4.0.0",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.7.0",
    "vite": "^6.0.0"
  },
  "devDependencies": {
    "@sveltejs/kit": "^2.15.0",
    "@sveltejs/vite-plugin-svelte": "^4.0.0",
    "jsdom": "^25.0.0",
    "vitest": "^2.0.0"
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

*Last updated: 2026-06-23*
*Generated by Mistral Vibe for frontend-specific static context*