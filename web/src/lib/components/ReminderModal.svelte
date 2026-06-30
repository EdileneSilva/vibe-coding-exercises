<script lang="ts">
	import type { Reminder, ReminderCreateForDeadline, ReminderCreateForRecurring, ReminderUpdate } from '$lib/types';
	import { api } from '$lib/api';

	interface Props {
		todoId: number;
		reminder?: Reminder | null;
		onClose: () => void;
		onSave: (reminder: Reminder) => void;
	}

	let { todoId, reminder = null, onClose, onSave } = $props();

	let isEditing = $state(reminder !== null);
	let type = $state<'deadline' | 'recurring'>('deadline');
	let deadline = $state('');
	let frequency = $state<'daily' | 'weekly' | 'monthly'>('daily');
	let selectedChannels = $state<Set<string>>(new Set(['in_app']));

	const channels = ['in_app', 'email', 'sms'] as const;
	const frequencies = ['daily', 'weekly', 'monthly'] as const;

	// Helper to capitalize first letter
	function capitalize(str: string): string {
		return str.charAt(0).toUpperCase() + str.slice(1);
	}

	// Initialize from existing reminder
	$effect(() => {
		if (reminder) {
			type = reminder.type as 'deadline' | 'recurring';
			if (reminder.deadline) {
				deadline = reminder.deadline;
			}
			if (reminder.frequency) {
				frequency = reminder.frequency as 'daily' | 'weekly' | 'monthly';
			}
			if (reminder.channels) {
				selectedChannels = new Set(reminder.channels.split(',').map(c => c.trim()));
			}
		}
	});

	let error = $state<string | null>(null);

	function setChannel(channel: string, enabled: boolean) {
		if (enabled) {
			selectedChannels.add(channel);
		} else {
			selectedChannels.delete(channel);
		}
	}

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = null;

		try {
			let newReminder: Reminder;
			
			if (isEditing && reminder) {
				// Update existing reminder
				const payload: ReminderUpdate = {
					type,
					channels: Array.from(selectedChannels)
				};
				
				if (type === 'deadline') {
					payload.deadline = deadline || undefined;
				} else {
					payload.frequency = frequency;
				}

				newReminder = await api.updateReminder(reminder.id, payload);
			} else {
				// Create new reminder
				if (type === 'deadline') {
					if (!deadline) {
						error = 'Please select a deadline';
						return;
					}
					const payload: ReminderCreateForDeadline = {
						type: 'deadline',
						deadline,
						channels: Array.from(selectedChannels) as any
					};
					newReminder = await api.createDeadlineReminder(todoId, payload);
				} else {
					const payload: ReminderCreateForRecurring = {
						type: 'recurring',
						frequency,
						channels: Array.from(selectedChannels) as any
					};
					newReminder = await api.createRecurringReminder(todoId, payload);
				}
			}

			onSave(newReminder);
			onClose();
		} catch (e: any) {
			error = e.message || 'Failed to save reminder';
			console.error(e);
		}
	}

	async function handleDelete() {
		if (!reminder) return;
		
		try {
			await api.deleteReminder(reminder.id);
			onClose();
		} catch (e) {
			error = 'Failed to delete reminder';
			console.error(e);
		}
	}
</script>

<!-- Modal overlay -->
<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onclick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
	<!-- Modal content -->
	<div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl" onclick|stopPropagation>
		<!-- Header -->
		<div class="flex items-center justify-between mb-4">
			<h2 class="text-xl font-bold text-slate-900">
				{isEditing ? 'Edit Reminder' : 'Add Reminder'}
			</h2>
			<button
				type="button"
				onclick={onClose}
				class="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition"
				title="Close"
			>
				✕
			</button>
		</div>

		<!-- Error message -->
		{#if error}
			<div class="mb-4 rounded-lg bg-red-50 p-3 text-red-700 text-sm">
				{error}
			</div>
		{/if}

		<!-- Form -->
		<form onsubmit={handleSubmit} class="space-y-4">
			<!-- Reminder type selection -->
			<div class="flex gap-2">
				<button
					type="button"
					onclick={() => type = 'deadline'}
					class="flex-1 rounded-lg border p-3 text-center font-medium transition {type === 'deadline' ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 bg-white'}"
				>
					📅 Deadline
				</button>
				<button
					type="button"
					onclick={() => type = 'recurring'}
					class="flex-1 rounded-lg border p-3 text-center font-medium transition {type === 'recurring' ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 bg-white'}"
				>
					🔄 Recurring
				</button>
			</div>

			<!-- Deadline-specific fields -->
			{#if type === 'deadline'}
				<div class="space-y-2">
					<label class="block text-sm font-medium text-slate-700">Deadline</label>
					<input
						type="datetime-local"
						bind:value={deadline}
						class="w-full rounded-lg border border-slate-300 p-3 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
						required={!isEditing}
					/>
				</div>
			{/if}

			<!-- Recurring-specific fields -->
			{#if type === 'recurring'}
				<div class="space-y-2">
					<label class="block text-sm font-medium text-slate-700">Frequency</label>
					<div class="flex gap-2">
						{#each frequencies as freq}
							<button
								type="button"
								onclick={() => frequency = freq}
								class="flex-1 rounded-lg border p-3 text-center font-medium transition {frequency === freq ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 bg-white'}"
							>
								{capitalize(freq)}
							</button>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Notification channels -->
			<div class="space-y-2">
				<label class="block text-sm font-medium text-slate-700">
					Notification Channels
				</label>
				<div class="flex gap-2 flex-wrap">
					{#each channels as channel}
						<button
							type="button"
							onclick={() => setChannel(channel, !selectedChannels.has(channel))}
							class="rounded-lg border p-2 px-3 text-sm font-medium transition {selectedChannels.has(channel) ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'}"
						>
							{#if selectedChannels.has(channel)}
								✓
							{/if}
							{capitalize(channel)}
						</button>
					{/each}
				</div>
			</div>

			<!-- Action buttons -->
			<div class="flex gap-2">
				{#if isEditing && reminder}
					<button
						type="button"
						onclick={handleDelete}
						class="flex-1 rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 transition"
					>
						Delete
					</button>
				{/if}
				<button
					type="button"
					onclick={onClose}
					class="flex-1 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition"
				>
					Cancel
				</button>
				<button
					type="submit"
					class="flex-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition"
				>
					{isEditing ? 'Save Changes' : 'Add Reminder'}
				</button>
			</div>
		</form>
	</div>
</div>

