<script lang="ts">
	import type { Hint } from '$lib/data/questions';
	import clsx from 'clsx';

	export let hint: Hint | undefined;
</script>

<div
	class={clsx(
		hint ? 'h-36' : 'h-0',
		'transition-all flex flex-col justify-center w-full max-w-md items-start'
	)}
>
	{#if hint?.type === 'closer'}
		That's off by about:
		<div class="flex vrt w-full">
			<div class="flex vrt font-serif italic">
				<p class="px-2">{hint.value.values[0].name}</p>
				<hr class="border-t w-full border-solid border-secondary" />
				<p class="px-2">{hint.value.values[1].name}</p>
			</div>
		</div>
	{/if}
</div>
