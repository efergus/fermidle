<script lang="ts">
	import { clone } from '$lib/transition/clone';
	import { flip } from 'svelte/animate';
	import { cubicInOut } from 'svelte/easing';
	import { fade, slide } from 'svelte/transition';

	export let values: (string | number)[] = [];
	export let target: Element | null = null;
	export let duration = 1400;

	const options = { duration, easing: cubicInOut };
</script>

<div class="flex flex-col-reverse justify-end gap-2 min-h-72">
	{#if target}
		{#each values as value, i (i)}
			<div
				class="hrz"
				in:fade={options}
				animate:flip={{
					...options
				}}
			>
				Your answer was: <p
					class="w-[3.5ch] text-4xl text-center font-semibold"
					in:clone={{ node: target, opacity: 1, ...options }}
				>
					{value}
				</p>
			</div>
		{/each}
	{/if}
</div>
