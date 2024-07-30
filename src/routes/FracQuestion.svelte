<script lang="ts">
	import type { Question } from '$lib/data/questions';
	import Frac from './format/Frac.svelte';

	export let question: Question | undefined;

	$: values = question?.values ?? [];
</script>

<div class="flex vrt p-1 font-serif font-bold italic max-w-md">
	<Frac>
		<p slot="num">{values[0]?.name ?? 'X'}</p>
		<p slot="den">{values[1]?.name ?? 'Y'}</p>
	</Frac>
</div>
