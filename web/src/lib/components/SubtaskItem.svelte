<script lang="ts">
	import type { Subtask, SubtaskUpdate } from '$lib/types';

	interface Props {
		subtask: Subtask;
		blockingSubtasks?: Subtask[];
		onToggle?: (subtaskId: number, completed: boolean) => void | Promise<void>;
		onSave?: (subtaskId: number, patch: SubtaskUpdate) => void | Promise<void>;
		onDelete?: (subtaskId: number) => void | Promise<void>;
		onSetDependency?: (subtaskId: number, blockedById: number | null) => void | Promise<void>;
		disabled?: boolean;
	}

	let { subtask, blockingSubtasks = [], onToggle, onSave, onDelete, onSetDependency, disabled = false } = $props();

	let editing = $state(false);
	let titleDraft = $state('');
	let descriptionDraft = $state('');
	let showDependencyMenu = $state(false);

	// Check if this subtask is blocked by another
	const isBlocked = $derived(subtask.blocked_by_id !== null);
	
	// Find the blocking subtask
	const blockingSubtask = $derived(blockingSubtasks.find(s => s.id === subtask.blocked_by_id));
	
	// Check if this subtask blocks others
	const blocksOthers = $derived(blockingSubtasks.some(s => s.blocked_by_id === subtask.id));

	function startEdit() {
		titleDraft = subtask.title;
		descriptionDraft = subtask.description ?? '';
		editing = true;
	}

	function cancelEdit() {
		editing = false;
	}

	async function save() {
		const trimmedTitle = titleDraft.trim();
		if (!trimmedTitle) return;
		if (onSave) {
			await onSave(subtask.id, {
				title: trimmedTitle,
				description: descriptionDraft.trim() || null
			});
		}
		editing = false;
	}

	async function toggleCompleted() {
		if (disabled) return;
		if (onToggle) {
			await onToggle(subtask.id, !subtask.completed);
		}
	}

	async function handleDelete() {
		if (disabled) return;
		if (onDelete) {
			await onDelete(subtask.id);
		}
	}

	async function setBlockedBy(blockedById: number | null) {
		if (onSetDependency) {
			await onSetDependency(subtask.id, blockedById);
		}
		showDependencyMenu = false;
	}

	function getStatusColor(status: string): string {
		switch (status) {
			case 'completed':
				return 'text-green-600';
			case 'in_progress':
				return 'text-blue-600';
			default:
				return 'text-slate-600';
		}
	}
</script>

<li class="group flex items-start gap-3 rounded-lg border border-slate-200 bg-white/50 p-3 transition hover:bg-white">
	<!-- Checkbox -->
	<input
		type="checkbox"
		checked={subtask.status === 'completed'}
		onchange={(e) => toggleCompleted()}
		class="mt-1 h-4 w-4 shrink-0 cursor-pointer rounded border-slate-300 text-indigo-600 focus:ring-2 focus:ring-indigo-500"
		aria-label={`Mark ${subtask.title} as ${subtask.status === 'completed' ? 'pending' : 'completed'}`}
		disabled={disabled}
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
					class="w-full rounded-md border border-slate-300 px-2 py-1 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
					placeholder="Subtask title"
					required
				/>
				<textarea
					bind:value={descriptionDraft}
					rows="2"
					class="w-full rounded-md border border-slate-300 px-2 py-1 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
					placeholder="Description (optional)"
				></textarea>
				<div class="flex gap-2">
					<button
						type="submit"
						class="rounded-md bg-indigo-600 px-2 py-1 text-xs font-medium text-white hover:bg-indigo-700"
					>
						Save
					</button>
					<button
						type="button"
						onclick={cancelEdit}
						class="rounded-md border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
					>
						Cancel
					</button>
				</div>
			</form>
		{:else}
			<div class="flex items-center gap-2">
				<p
					class="font-medium text-sm {subtask.status === 'completed' ? 'line-through text-slate-400' : 'text-slate-900'}"
				>
					{subtask.title}
				</p>
				
				{#if isBlocked && blockingSubtask}
					<span
						class="rounded-full bg-amber-100 px-1.5 py-0.5 text-xs font-medium text-amber-700"
						title="Blocked by: {blockingSubtask.title}"
					>
						⏸️ Blocked
					</span>
				{/if}
				
				{#if blocksOthers}
					<span
						class="rounded-full bg-indigo-100 px-1.5 py-0.5 text-xs font-medium text-indigo-700"
						title="This subtask blocks other subtasks"
					>
						🔒 Blocks
					</span>
				{/if}
			</div>
			
			{#if subtask.description && !editing}
				<p
					class="mt-1 text-xs text-slate-600 break-words {subtask.status === 'completed' ? 'line-through text-slate-400' : ''}"
				>
					{subtask.description}
				</p>
			{/if}
		{/if}
		
		<!-- Dependency info -->
		{#if isBlocked && blockingSubtask && !editing}
			<p class="mt-1 text-xs text-amber-600">
				Blocked by: {blockingSubtask.title}
			</p>
		{/if}
		
		{#if blocksOthers && !editing}
			<p class="mt-1 text-xs text-indigo-600">
				Blocks: {blockingSubtasks.filter(s => s.blocked_by_id === subtask.id).map(s => s.title).join(', ')}
			</p>
		{/if}
	</div>

	<!-- Actions -->
	{#if !editing}
		<div class="flex gap-1 opacity-0 transition group-hover:opacity-100">
			<!-- Dependency menu -->
			{#if onSetDependency}
				<div class="relative">
					<button
						type="button"
						onclick={() => showDependencyMenu = !showDependencyMenu}
						class="rounded-md p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-700"
						title="Set dependency"
					>
						🔗
					</button>
					
					{#if showDependencyMenu}
						<div class="absolute right-0 top-full mt-1 w-48 rounded-md bg-white border border-slate-200 shadow-lg z-10 p-2">
							<h4 class="font-medium text-sm text-slate-700 mb-2">Blocked by:</h4>
							<button
								type="button"
								onclick={() => setBlockedBy(null)}
								class="w-full text-left px-2 py-1 rounded text-sm hover:bg-slate-100 flex items-center gap-2"
							>
								<span>🟢 None</span>
							</button>
							
							{#each blockingSubtasks.filter(s => s.id !== subtask.id) as candidate}
								<button
									type="button"
									onclick={() => setBlockedBy(candidate.id)}
									class="w-full text-left px-2 py-1 rounded text-sm hover:bg-slate-100 flex items-center gap-2 {candidate.id === subtask.blocked_by_id ? 'bg-indigo-50' : ''}"
								>
									<span class="text-xs">🔒</span>
									<span>{candidate.title}</span>
								</button>
							{/each}
						</div>
					{/if}
				</div>
			{/if}
			
			<!-- Edit button -->
			<button
				type="button"
				onclick={startEdit}
				class="rounded-md p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-700"
				title="Edit subtask"
			>
				<svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
					<path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
					<path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
				</svg>
			</button>
			
			<!-- Delete button -->
			<button
				type="button"
				onclick={handleDelete}
				class="rounded-md p-1.5 text-slate-500 hover:bg-red-50 hover:text-red-600"
				title="Delete subtask"
				disabled={disabled}
			>
				<svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
					<path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
				</svg>
			</button>
		</div>
	{/if}
</li>
