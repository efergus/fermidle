<script lang="ts">
	import type { Hint } from '$lib/data/questions';

	export let hint: Hint | undefined;
</script>

{#if hint?.type === 'closer'}
	<div>
		That's off by about
		<div class="flex vrt font-serif italic">
			<p class="px-2">{hint.value.values[0].name}</p>
			<hr class="border-t w-full border-solid border-secondary" />
			<p class="px-2">{hint.value.values[1].name}</p>
		</div>
	</div>
{/if}
