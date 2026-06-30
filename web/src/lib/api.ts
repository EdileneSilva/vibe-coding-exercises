import { env } from '$env/dynamic/public';
import type {
	Todo,
	TodoCreate,
	TodoUpdate,
	Subtask,
	SubtaskCreate,
	SubtaskUpdate,
	Reminder,
	ReminderCreateForDeadline,
	ReminderCreateForRecurring,
	ReminderUpdate,
	DependencyGraph
} from './types';

const BASE = env.PUBLIC_API_BASE || '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
	const res = await fetch(`${BASE}${path}`, {
		headers: { 'Content-Type': 'application/json' },
		...init
	});
	if (!res.ok) {
		const detail = await res.text().catch(() => res.statusText);
		throw new Error(`${res.status} ${res.statusText}: ${detail}`);
	}
	if (res.status === 204) return undefined as T;
	return res.json() as Promise<T>;
}

export const api = {
	// ============= TODO ENDPOINTS =============
	listTodos: () => request<Todo[]>('/todos'),
	getTodo: (id: number) => request<Todo>(`/todos/${id}`),
	createTodo: (payload: TodoCreate) =>
		request<Todo>('/todos', { method: 'POST', body: JSON.stringify(payload) }),
	updateTodo: (id: number, payload: TodoUpdate) =>
		request<Todo>(`/todos/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
	deleteTodo: (id: number) => request<void>(`/todos/${id}`, { method: 'DELETE' }),

	// ============= SUBTASK ENDPOINTS =============
	// List all subtasks for a todo
	listSubtasks: (todoId: number) => request<Subtask[]>(`/todos/${todoId}/subtasks`),
	// Get a single subtask
	getSubtask: (subtaskId: number) => request<Subtask>(`/subtasks/${subtaskId}`),
	// Create a new subtask
	createSubtask: (todoId: number, payload: SubtaskCreate) =>
		request<Subtask>(`/todos/${todoId}/subtasks`, { method: 'POST', body: JSON.stringify(payload) }),
	// Update a subtask
	updateSubtask: (subtaskId: number, payload: SubtaskUpdate) =>
		request<Subtask>(`/subtasks/${subtaskId}`, { method: 'PUT', body: JSON.stringify(payload) }),
	// Delete a subtask
	deleteSubtask: (subtaskId: number) => request<void>(`/subtasks/${subtaskId}`, { method: 'DELETE' }),
	// Get dependency graph for a todo
	getDependencyGraph: (todoId: number) => request<DependencyGraph>(`/todos/${todoId}/subtasks/dependencies`),
	// Complete a subtask (checks dependencies)
	completeSubtask: (subtaskId: number) =>
		request<Subtask>(`/subtasks/${subtaskId}/complete`, { method: 'POST' }),

	// ============= REMINDER ENDPOINTS =============
	// List all reminders for a todo
	listReminders: (todoId: number) => request<Reminder[]>(`/todos/${todoId}/reminders`),
	// Get a single reminder
	getReminder: (reminderId: number) => request<Reminder>(`/reminders/${reminderId}`),
	// Create a deadline reminder
	createDeadlineReminder: (todoId: number, payload: ReminderCreateForDeadline) =>
		request<Reminder>(`/todos/${todoId}/reminders/deadline`, { method: 'POST', body: JSON.stringify(payload) }),
	// Create a recurring reminder
	createRecurringReminder: (todoId: number, payload: ReminderCreateForRecurring) =>
		request<Reminder>(`/todos/${todoId}/reminders/recurring`, { method: 'POST', body: JSON.stringify(payload) }),
	// Update a reminder
	updateReminder: (reminderId: number, payload: ReminderUpdate) =>
		request<Reminder>(`/reminders/${reminderId}`, { method: 'PUT', body: JSON.stringify(payload) }),
	// Delete a reminder
	deleteReminder: (reminderId: number) => request<void>(`/reminders/${reminderId}`, { method: 'DELETE' }),
	// Snooze a reminder
	snoozeReminder: (reminderId: number, hours: number = 1) =>
		request<Reminder>(`/reminders/${reminderId}/snooze?hours=${hours}`, { method: 'POST' }),
	// Get todos with reminders due within hours
	getRemindersDue: (hours: number = 48) => request<Todo[]>(`/reminders/due?hours=${hours}`),
	// Update all reminder states
	updateReminderStates: () => request<{ updated_count: number; message: string }>('/reminders/update-states', { method: 'POST' })
};
