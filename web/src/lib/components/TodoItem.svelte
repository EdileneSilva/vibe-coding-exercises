<script lang="ts">
	import type { Todo, TodoUpdate, Reminder } from '$lib/types';
	import { api } from '$lib/api';
	import ReminderBadge from './ReminderBadge.svelte';
	import SubtaskList from './SubtaskList.svelte';
	import ReminderModal from './ReminderModal.svelte';

	interface Props {
		todo: Todo;
		onToggle: (id: number, completed: boolean) => void | Promise<void>;
		onSave: (id: number, patch: TodoUpdate) => void | Promise<void>;
		onDelete: (id: number) => void | Promise<void>;
		showSubtasks?: boolean;
		showReminders?: boolean;
	}

	let { todo, onToggle, onSave, onDelete, showSubtasks = true, showReminders = true } = $props();

	let editing = $state(false);
	let titleDraft = $state('');
	let descriptionDraft = $state('');
	let expanded = $state(false);
	let showReminderModal = $state(false);
	let reminders = $state<Reminder[]>([]);

	// Fetch reminders when component mounts or todo changes
	$effect(() => {
		if (todo.id) {
			fetchReminders();
		}
	});

	const fetchReminders = async () => {
		try {
			reminders = await api.listReminders(todo.id);
		} catch (e) {
			console.error('Failed to load reminders:', e);
		}
	};

	const handleAddReminder = (newReminder: Reminder) => {
		reminders = [...reminders, newReminder];
	};

	const handleDeleteReminder = async (reminderId: number) => {
		try {
			await api.deleteReminder(reminderId);
			reminders = reminders.filter(r => r.id !== reminderId);
		} catch (e) {
			console.error('Failed to delete reminder:', e);
		}
	};

	const handleSnoozeReminder = async (reminderId: number, hours: number) => {
		try {
			const updated = await api.snoozeReminder(reminderId, hours);
			reminders = reminders.map(r => r.id === reminderId ? updated : r);
		} catch (e) {
			console.error('Failed to snooze reminder:', e);
		}
	};

	function startEdit() {
		titleDraft = todo.title;
		descriptionDraft = todo.description ?? '';
		editing = true;
	}

	function cancelEdit() {
		editing = false;
	}

	async function save() {
		const trimmedTitle = titleDraft.trim();
		if (!trimmedTitle) return;
		await onSave(todo.id, {
			title: trimmedTitle,
			description: descriptionDraft.trim() || null
		});
		editing = false;
	}
</script>

<li class="group flex flex-col gap-2 rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md">
	<div class="flex items-start gap-3">
		<!-- Checkbox -->
		<input
			type="checkbox"
			checked={todo.completed}
			onchange={(e) => onToggle(todo.id, e.currentTarget.checked)}
			class="mt-1 h-5 w-5 shrink-0 cursor-pointer rounded border-slate-300 text-indigo-600 focus:ring-2 focus:ring-indigo-500"
			aria-label={`Mark ${todo.title} as ${todo.completed ? 'active' : 'completed'}`}
		/>

		<!-- Content -->
		<div class="min-w-0 flex-1">
			{#if editing}
				<form
					onsubmit={(e) => {
						e.preventDefault();
						save();
					}}
					class="space-y-2"
				>
					<input
						type="text"
						bind:value={titleDraft}
						class="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
						placeholder="Title"
						required
					/>
					<textarea
						bind:value={descriptionDraft}
						rows="2"
						class="w-full rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
						placeholder="Description (optional)"
					></textarea>
					<div class="flex gap-2">
						<button
							type="submit"
							class="rounded-md bg-indigo-600 px-3 py-1 text-sm font-medium text-white hover:bg-indigo-700"
						>
							Save
						</button>
						<button
							type="button"
							onclick={cancelEdit}
							class="rounded-md border border-slate-300 px-3 py-1 text-sm font-medium text-slate-700 hover:bg-slate-50"
						>
							Cancel
						</button>
					</div>
				</form>
			{:else}
				<p
					class="font-medium text-slate-900 break-words"
					class:line-through={todo.completed}
					class:text-slate-400={todo.completed}
				>
					{todo.title}
				</p>
				{#if todo.description}
					<p
						class="mt-1 text-sm text-slate-600 break-words"
						class:text-slate-400={todo.completed}
					>
						{todo.description}
					</p>
				{/if}
			{/if}
		</div>

		<!-- Actions -->
		<div class="flex gap-1">
			{#if showReminders && !editing}
				<button
					type="button"
					onclick={() => showReminderModal = true}
					class="rounded-md p-2 text-slate-500 hover:bg-indigo-50 hover:text-indigo-600 transition"
					title="Add reminder"
				>
					🔔
				</button>
			{/if}
			
			{#if !editing}
				<button
					type="button"
					onclick={startEdit}
					class="rounded-md p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700"
					aria-label="Edit task"
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
						<path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
						<path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
					</svg>
				</button>
				<button
					type="button"
					onclick={() => onDelete(todo.id)}
					class="rounded-md p-2 text-slate-500 hover:bg-red-50 hover:text-red-600"
					aria-label="Delete task"
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
					</svg>
				</button>
			{/if}
		</div>
	</div>

	<!-- Reminders display -->
	{#if showReminders && reminders.length > 0 && !editing}
		<div class="flex flex-wrap gap-1 px-8">
			{#each reminders as reminder}
				<ReminderBadge
					reminder={reminder}
					onSnooze={handleSnoozeReminder}
					onDelete={handleDeleteReminder}
					compact
				/>
			{/each}
		</div>
	{/if}

	<!-- Subtasks -->
	{#if showSubtasks && expanded}
		<SubtaskList
			todoId={todo.id}
			onChange={() => { /* Refresh parent if needed */ }}
			class="mt-2"
		/>
	{/if}

	<!-- Subtasks toggle -->
	{#if showSubtasks}
		<button
			type="button"
			onclick={() => expanded = !expanded}
			class="mt-2 flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition self-start"
		>
			<span>{expanded ? '▼' : '▶'}</span>
			<span>Subtasks</span>
		</button>
	{/if}
</li>

<!-- Reminder Modal -->
{#if showReminderModal}
	<ReminderModal
		todoId={todo.id}
		onClose={() => showReminderModal = false}
		onSave={handleAddReminder}
	/>
{/if}
