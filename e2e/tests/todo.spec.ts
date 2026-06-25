import { test, expect } from '@playwright/test';

test.describe('Todo App E2E Tests', () => {
  const API_BASE = process.env.API_URL || 'http://localhost:8000';
  const WEB_BASE = process.env.WEB_URL || 'http://localhost:8080';

  test.beforeAll(async () => {
    // Ensure API is running
    console.log(`API URL: ${API_BASE}`);
    console.log(`WEB URL: ${WEB_BASE}`);
  });

  test.describe('API Tests', () => {
    test('GET /todos returns empty array initially', async ({ request }) => {
      const response = await request.get(`${API_BASE}/todos`);
      expect(response.ok()).toBeTruthy();
      const todos = await response.json();
      expect(Array.isArray(todos)).toBeTruthy();
    });

    test('POST /todos creates a new todo', async ({ request }) => {
      const newTodo = {
        title: 'E2E Test Todo',
        description: 'Created by Playwright',
        completed: false
      };
      
      const response = await request.post(`${API_BASE}/todos`, {
        data: newTodo
      });
      
      expect(response.status()).toBe(201);
      const createdTodo = await response.json();
      expect(createdTodo.title).toBe(newTodo.title);
      expect(createdTodo.description).toBe(newTodo.description);
      expect(createdTodo.completed).toBe(false);
      expect(createdTodo.id).toBeDefined();
    });

    test('GET /todos/{id} retrieves a specific todo', async ({ request }) => {
      // First create a todo
      const createResponse = await request.post(`${API_BASE}/todos`, {
        data: {
          title: 'Test Todo for Retrieval',
          description: 'Testing GET by ID',
          completed: false
        }
      });
      const createdTodo = await createResponse.json();
      const todoId = createdTodo.id;
      
      // Then retrieve it
      const getResponse = await request.get(`${API_BASE}/todos/${todoId}`);
      expect(getResponse.ok()).toBeTruthy();
      const retrievedTodo = await getResponse.json();
      expect(retrievedTodo.id).toBe(todoId);
      expect(retrievedTodo.title).toBe('Test Todo for Retrieval');
    });

    test('PUT /todos/{id} updates a todo', async ({ request }) => {
      // Create a todo
      const createResponse = await request.post(`${API_BASE}/todos`, {
        data: {
          title: 'Todo to Update',
          completed: false
        }
      });
      const createdTodo = await createResponse.json();
      const todoId = createdTodo.id;
      
      // Update it
      const updateResponse = await request.put(`${API_BASE}/todos/${todoId}`, {
        data: {
          title: 'Updated Todo',
          completed: true
        }
      });
      expect(updateResponse.ok()).toBeTruthy();
      const updatedTodo = await updateResponse.json();
      expect(updatedTodo.title).toBe('Updated Todo');
      expect(updatedTodo.completed).toBe(true);
    });

    test('DELETE /todos/{id} deletes a todo', async ({ request }) => {
      // Create a todo
      const createResponse = await request.post(`${API_BASE}/todos`, {
        data: {
          title: 'Todo to Delete',
          completed: false
        }
      });
      const createdTodo = await createResponse.json();
      const todoId = createdTodo.id;
      
      // Delete it
      const deleteResponse = await request.delete(`${API_BASE}/todos/${todoId}`);
      expect(deleteResponse.status()).toBe(204);
      
      // Verify it's deleted
      const getResponse = await request.get(`${API_BASE}/todos/${todoId}`);
      expect(getResponse.status()).toBe(404);
    });
  });

  test.describe('Web UI Tests', () => {
    test('Page loads successfully', async ({ page }) => {
      await page.goto(WEB_BASE);
      await expect(page).toHaveTitle(/Todo App/i);
    });

    test('Add todo form is visible', async ({ page }) => {
      await page.goto(WEB_BASE);
      await expect(page.locator('input[type="text"]')).toBeVisible();
      await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('Filter buttons are visible', async ({ page }) => {
      await page.goto(WEB_BASE);
      await expect(page.getByRole('button', { name: 'All' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Active' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Completed' })).toBeVisible();
    });

    test('Can add a todo through UI', async ({ page }) => {
      await page.goto(WEB_BASE);
      
      const todoText = 'Playwright Test Todo';
      await page.locator('input[type="text"]').fill(todoText);
      await page.locator('button[type="submit"]').click();
      
      // Wait for the todo to appear
      await expect(page.locator('text=' + todoText)).toBeVisible();
    });

    test('Can mark todo as completed', async ({ page }) => {
      await page.goto(WEB_BASE);
      
      // Add a todo
      const todoText = 'Todo to Complete';
      await page.locator('input[type="text"]').fill(todoText);
      await page.locator('button[type="submit"]').click();
      await page.waitForSelector('text=' + todoText);
      
      // Mark as completed
      const checkbox = page.locator('input[type="checkbox"]').first();
      await checkbox.check();
      
      // Verify it's marked as completed (should have line-through style)
      const todoItem = page.locator('text=' + todoText);
      await expect(todoItem).toHaveClass(/line-through/i);
    });

    test('Filtering works correctly', async ({ page }) => {
      await page.goto(WEB_BASE);
      
      // Add a todo
      await page.locator('input[type="text"]').fill('Active Todo');
      await page.locator('button[type="submit"]').click();
      await page.waitForSelector('text=Active Todo');
      
      // Add and complete another todo
      await page.locator('input[type="text"]').fill('Completed Todo');
      await page.locator('button[type="submit"]').click();
      await page.waitForSelector('text=Completed Todo');
      const checkboxes = page.locator('input[type="checkbox"]');
      await checkboxes.last().check();
      
      // Click Active filter
      await page.getByRole('button', { name: 'Active' }).click();
      await expect(page.locator('text=Active Todo')).toBeVisible();
      await expect(page.locator('text=Completed Todo')).not.toBeVisible();
      
      // Click Completed filter
      await page.getByRole('button', { name: 'Completed' }).click();
      await expect(page.locator('text=Completed Todo')).toBeVisible();
      await expect(page.locator('text=Active Todo')).not.toBeVisible();
      
      // Click All filter
      await page.getByRole('button', { name: 'All' }).click();
      await expect(page.locator('text=Active Todo')).toBeVisible();
      await expect(page.locator('text=Completed Todo')).toBeVisible();
    });

    test('Can delete a todo', async ({ page }) => {
      await page.goto(WEB_BASE);
      
      // Add a todo
      const todoText = 'Todo to Delete';
      await page.locator('input[type="text"]').fill(todoText);
      await page.locator('button[type="submit"]').click();
      await page.waitForSelector('text=' + todoText);
      
      // Delete it
      await page.locator('button', { hasText: 'Delete' }).first().click();
      
      // Verify it's gone
      await expect(page.locator('text=' + todoText)).not.toBeVisible();
    });
  });
});
