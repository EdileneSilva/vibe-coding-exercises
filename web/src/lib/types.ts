export interface Todo {
	id: number;
	title: string;
	description: string | null;
	completed: boolean;
	created_at: string;
	updated_at: string | null;
	subtasks?: Subtask[];
	reminders?: Reminder[];
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

// ============= SUBTASK TYPES =============

export interface Subtask {
	id: number;
	todo_id: number;
	title: string;
	description: string | null;
	status: 'pending' | 'in_progress' | 'completed';
	blocked_by_id: number | null;
	created_at: string;
	updated_at: string | null;
}

export interface SubtaskCreate {
	title: string;
	description?: string | null;
	status?: 'pending' | 'in_progress' | 'completed';
	blocked_by_id?: number | null;
}

export interface SubtaskUpdate {
	title?: string;
	description?: string | null;
	status?: 'pending' | 'in_progress' | 'completed';
	blocked_by_id?: number | null;
}

// ============= REMINDER TYPES =============

export type ReminderType = 'deadline' | 'recurring';
export type ReminderState = 'active' | 'approaching' | 'overdue';
export type ReminderFrequency = 'daily' | 'weekly' | 'monthly';
export type NotificationChannel = 'email' | 'in_app' | 'sms';

export interface Reminder {
	id: number;
	todo_id: number;
	type: ReminderType;
	deadline?: string | null;
	frequency?: ReminderFrequency | null;
	interval_days?: number | null;
	channels: string; // Comma-separated list of NotificationChannel
	state: ReminderState;
	snoozed_until?: string | null;
	snooze_count: number;
	created_at: string;
	updated_at: string | null;
}

export interface ReminderCreateForDeadline {
	type: 'deadline';
	deadline: string; // ISO 8601 datetime
	channels: NotificationChannel[];
}

export interface ReminderCreateForRecurring {
	type: 'recurring';
	frequency: ReminderFrequency;
	channels: NotificationChannel[];
}

export interface ReminderUpdate {
	type?: ReminderType;
	deadline?: string | null;
	frequency?: ReminderFrequency | null;
	channels?: NotificationChannel[] | string | null;
	state?: ReminderState;
}

// Dependency graph types
export interface DependencyGraph {
	subtasks: Array<{
		id: number;
		title: string;
		status: string;
		blocked_by_id: number | null;
	}>;
	edges: Array<[number, number]>; // [from_id, to_id] for blocked_by relationships
}
