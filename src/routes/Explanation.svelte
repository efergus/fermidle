<script lang="ts">
	import { type Question } from '$lib/data/questions';
	import { scientific } from '$lib/scientific';
	import Scientific from './format/Scientific.svelte';
	import ValueImage from './ValueImage.svelte';
	import Units from './format/Units.svelte';

	export let question: Question;
	export let correct = true;

	$: values = question.values.map(({ name, value }) => {
		const [num, units] = value.split(' ');
		return {
			name,
			num: parseFloat(num),
			units
		};
	});
</script>

<div class="vrt items-start w-full max-w-md py-4">
	<div>
		{#if correct}
			Correct! The answer is
		{:else}
			The correct answer was
		{/if}
		<Scientific value={question.answer} />
	</div>
	{#each values as value}
		<div>
			<p>
				<span class="font-bold">{value.name}</span> is
				<span class="italic"><Scientific value={value.num} /> <Units units={value.units} /></span>
			</p>
		</div>
	{/each}
</div>
