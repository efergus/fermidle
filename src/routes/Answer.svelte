<script lang="ts">
	import { clone } from '$lib/transition/clone';
	import clsx from 'clsx';
	import { cubicInOut } from 'svelte/easing';
	import { fade, slide } from 'svelte/transition';

	export let values: (string | number)[] = [];
	export let target: Element | null = null;
	export let duration = 1400;
	export let size = 6;

	const options = { duration, easing: cubicInOut };
	$: display = values.slice(-size);
	$: extra = new Array(size).fill(null).map((_, i) => i < values.length);
</script>

<div class="w-full max-w-md relative">
	{#if target}
		<div class="absolute vrt items-stretch gap-2 w-full">
			{#each display as value, index (index)}
				<div class={clsx('hrz min-h-[3rem] border rounded px-6 bg-theme')} out:fade={options}>
					<p
						in:fade={{
							...options
						}}
					>
						Your answer was:
					</p>
					<p
						class="w-[3.5ch] text-4xl text-center font-semibold"
						in:clone={{ node: target, opacity: 1, ...options }}
					>
						{value}
					</p>
				</div>
			{/each}
		</div>
	{/if}
	<div class="vrt items-stretch gap-2 w-full">
		{#each extra as invisible}
			<div
				class={clsx(
					'w-full min-h-[3rem] border border-secondary rounded transition-opacity',
					invisible && 'opacity-0'
				)}
				style={`transition-duration: ${duration}ms;`}
			></div>
		{/each}
	</div>
</div>
