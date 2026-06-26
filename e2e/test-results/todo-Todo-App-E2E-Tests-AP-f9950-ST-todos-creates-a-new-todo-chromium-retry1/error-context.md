# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: todo.spec.ts >> Todo App E2E Tests >> API Tests >> POST /todos creates a new todo
- Location: tests/todo.spec.ts:21:5

# Error details

```
Error: apiRequestContext.post: connect ECONNREFUSED ::1:8000
Call log:
  - → POST http://localhost:8000/todos
    - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.7827.55 Safari/537.36
    - accept: */*
    - accept-encoding: gzip,deflate,br
    - content-type: application/json
    - content-length: 81

```