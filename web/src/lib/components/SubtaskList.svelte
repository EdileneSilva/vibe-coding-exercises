<script lang="ts">
	import type { Subtask, SubtaskCreate } from '$lib/types';
	import { api } from '$lib/api';
	import SubtaskItem from './SubtaskItem.svelte';

	interface Props {
		todoId: number;
		onChange?: () => void | Promise<void>;
		readOnly?: boolean;
	}

	let { todoId, onChange, readOnly = false } = $props();

	let subtasks = $state<Subtask[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let showAddForm = $state(false);
	let newSubtaskTitle = $state('');
	let newSubtaskDescription = $state('');

	// Fetch subtasks on mount
	$effect(() => {
		fetchSubtasks();
	});

	const fetchSubtasks = async () => {
		loading = true;
		error = null;
		try {
			subtasks = await api.listSubtasks(todoId);
			if (onChange) {
				await onChange();
			}
		} catch (e) {
			error = 'Failed to load subtasks';
			console.error(e);
		} finally {
			loading = false;
		}
	};

	const handleAddSubtask = async (e: Event) => {
		e.preventDefault();
		if (!newSubtaskTitle.trim()) return;

		try {
			const newSubtask = await api.createSubtask(todoId, {
				title: newSubtaskTitle.trim(),
				description: newSubtaskDescription.trim() || null
			});
			subtasks = [...subtasks, newSubtask];
			newSubtaskTitle = '';
			newSubtaskDescription = '';
			showAddForm = false;
			if (onChange) {
				await onChange();
			}
		} catch (e) {
			error = 'Failed to create subtask';
			console.error(e);
		}
	};

	const handleDeleteSubtask = async (subtaskId: number) => {
		try {
			await api.deleteSubtask(subtaskId);
			subtasks = subtasks.filter(s => s.id !== subtaskId);
			if (onChange) {
				await onChange();
			}
		} catch (e) {
			error = 'Failed to delete subtask';
			console.error(e);
		}
	};

	const handleUpdateSubtask = async (subtaskId: number, patch: Partial<SubtaskCreate>) => {
		try {
			const updated = await api.updateSubtask(subtaskId, patch);
			subtasks = subtasks.map(s => s.id === subtaskId ? updated : s);
			if (onChange) {
				await onChange();
			}
		} catch (e) {
			error = 'Failed to update subtask';
			console.error(e);
		}
	};

	const handleToggleSubtask = async (subtaskId: number, completed: boolean) => {
		try {
			const updated = await api.updateSubtask(subtaskId, {
				status: completed ? 'completed' : 'pending'
			});
			subtasks = subtasks.map(s => s.id === subtaskId ? updated : s);
			if (onChange) {
				await onChange();
			}
		} catch (e) {
			error = 'Failed to toggle subtask';
			console.error(e);
		}
	};

	const handleSetDependency = async (subtaskId: number, blockedById: number | null) => {
		try {
			const updated = await api.updateSubtask(subtaskId, { blocked_by_id: blockedById });
			subtasks = subtasks.map(s => s.id === subtaskId ? updated : s);
			if (onChange) {
				await onChange();
			}
		} catch (e) {
			error = 'Failed to set dependency';
			console.error(e);
		}
	};

	// Calculate completion stats
	const completedCount = $derived(subtasks.filter(s => s.status === 'completed').length);
	const totalCount = $derived(subtasks.length);
	const completionPercentage = $derived(totalCount > 0 ? (completedCount / totalCount) * 100 : 0);
</script>

<div class="mt-4 border-t border-slate-200 pt-4">
	<div class="flex items-center justify-between mb-3">
		<div class="flex items-center gap-3">
			<h4 class="font-medium text-slate-700">
				Subtasks ({completedCount}/{totalCount})
			</h4>
			
			{#if totalCount > 0}
				<div class="w-24 h-2 rounded-full bg-slate-200 overflow-hidden">
					<div
						class="h-full bg-indigo-600 transition-all duration-300"
						style={`width: ${completionPercentage}%`}
					></div>
				</div>
			{/if}
		</div>
		
		{#if !readOnly}
			<button
				type="button"
				onclick={() => showAddForm = !showAddForm}
				class="flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 transition"
			>
				<span>+</span>
				<span>Add Subtask</span>
			</button>
		{/if}
	</div>

	<!-- Error message -->
	{#if error}
		<p class="text-red-500 text-sm mb-3">{error}</p>
	{/if}

	<!-- Loading state -->
	{#if loading}
		<p class="text-slate-500 text-sm">Loading subtasks...</p>
	{/if}

	<!-- Add subtask form -->
	{#if showAddForm && !readOnly}
		<form
			onsubmit={handleAddSubtask}
			class="mb-4 p-3 rounded-lg bg-slate-50 border border-slate-200"
		>
			<div class="flex flex-col gap-2">
				<input
					type="text"
					bind:value={newSubtaskTitle}
					class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
					placeholder="Subtask title"
					required
				/>
				<textarea
					bind:value={newSubtaskDescription}
					rows="2"
					class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
					placeholder="Description (optional)"
				></textarea>
				<div class="flex gap-2 justify-end">
					<button
						type="button"
						onclick={() => showAddForm = false}
						class="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
					>
						Cancel
					</button>
					<button
						type="submit"
						class="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
					>
						Add Subtask
					</button>
				</div>
			</div>
		</form>
	{/if}

	<!-- Subtask list -->
	{#if subtasks.length > 0}
		<ul class="space-y-2">
			{#each subtasks as subtask}
				<SubtaskItem
					subtask={subtask}
					blockingSubtasks={subtasks}
					onToggle={handleToggleSubtask}
					onSave={handleUpdateSubtask}
					onDelete={handleDeleteSubtask}
					onSetDependency={handleSetDependency}
					disabled={readOnly}
				/>
			{/each}
		</ul>
	{:else if !loading && !showAddForm}
		<p class="text-slate-500 text-sm text-center py-4">
			No subtasks yet. Add one above!
		</p>
	{/if}
</div>
