<script lang="ts">
	import type { Hint } from '$lib/data/questions';
	import clsx from 'clsx';

	export let hint: Hint | undefined;
</script>

<div class={clsx(hint ? 'h-28' : 'h-0', 'transition-all vrt justify-center w-full max-w-md')}>
	{#if hint?.type === 'closer'}
		<p class="w-full max-w-sm">That's off by about:</p>
		<div class="flex vrt w-full">
			<div class="flex vrt font-serif italic">
				<p class="px-2">{hint.value.values[0].name}</p>
				<hr class="border-t w-full border-solid border-secondary" />
				<p class="px-2">{hint.value.values[1].name}</p>
			</div>
		</div>
	{/if}

	{#if hint?.type === 'message'}
		<p class="text-2xl">{hint.value}</p>
	{/if}
</div>
