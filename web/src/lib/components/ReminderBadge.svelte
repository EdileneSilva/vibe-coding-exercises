<script lang="ts">
	import type { Reminder } from '$lib/types';

	interface Props {
		reminder: Reminder;
		onSnooze?: (reminderId: number, hours: number) => void | Promise<void>;
		onDelete?: (reminderId: number) => void | Promise<void>;
		compact?: boolean;
	}

	let { reminder, onSnooze, onDelete, compact = $state(false) } = $props();

	// Helper functions
	function formatDeadline(deadline: string | null | undefined): string {
		if (!deadline) return '';
		const date = new Date(deadline);
		return date.toLocaleString('en-US', {
			month: 'short',
			day: 'numeric',
			hour: 'numeric',
			minute: '2-digit',
			hour12: true
		});
	}

	function formatFrequency(frequency: string | null | undefined): string {
		if (!frequency) return '';
		return frequency.charAt(0).toUpperCase() + frequency.slice(1);
	}

	function getStateColor(state: string): string {
		switch (state) {
			case 'overdue':
				return 'bg-red-100 text-red-700 border-red-300';
			case 'approaching':
				return 'bg-amber-100 text-amber-700 border-amber-300';
			default:
				return 'bg-indigo-100 text-indigo-700 border-indigo-300';
		}
	}

	function getStateIcon(state: string): string {
		switch (state) {
			case 'overdue':
				return '⚠️';
			case 'approaching':
				return '⏰';
			default:
				return '🔔';
		}
	}

	function getChannelsDisplay(channels: string): string {
		if (!channels) return 'In-app';
		const channelList = channels.split(',').map(c => c.trim());
		return channelList.join(', ');
	}
</script>

<div class="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium" class={getStateColor(reminder.state)}>
	<span>{getStateIcon(reminder.state)}</span>
	
	{#if reminder.type === 'deadline' && reminder.deadline}
		<span class="hidden sm:inline">{formatDeadline(reminder.deadline)}</span>
	{:else if reminder.type === 'recurring' && reminder.frequency}
		<span class="hidden sm:inline">Every {formatFrequency(reminder.frequency)}</span>
	{/if}
	
	{#if !compact && reminder.channels}
		<span class="hidden md:inline">via {getChannelsDisplay(reminder.channels)}</span>
	{/if}
	
	{#if onSnooze || onDelete}
		<div class="flex gap-0.5 ml-1">
			{#if onSnooze}
				<button
					onclick={() => onSnooze(reminder.id, 1)}
					class="rounded-full p-0.5 hover:bg-white/50 transition"
					title="Snooze 1 hour"
				>
					⏸️
				</button>
			{/if}
			{#if onDelete}
				<button
					onclick={() => onDelete(reminder.id)}
					class="rounded-full p-0.5 hover:bg-white/50 transition"
					title="Delete reminder"
				>
					🗑️
				</button>
			{/if}
		</div>
	{/if}
</div>
