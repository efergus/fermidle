<script lang="ts">
	import type { Question } from '$lib/data/questions';
	import Frac from './format/Frac.svelte';
	import FracQuestion from './FracQuestion.svelte';
	import ValueImage from './ValueImage.svelte';

	export let question: Question;
	export let value: number = 1;
	export let describe = false;

	$: values = question.values;
	$: repeat1 = value < 0 ? 'repeat' : 'no-repeat';
	$: repeat2 = value > 0 ? 'repeat' : 'no-repeat';
</script>

<div class="flex vrt text-xl max-w-lg w-full text-center">
	{#if describe}
		<div class="flex hrz gap-2">
			<p class="text-2xl">What is</p>
			<div class="font-serif italic">
				<Frac
					><p slot="num">X</p>
					<p slot="den">Y</p></Frac
				>
			</div>
			?
		</div>
	{/if}
	<div class="flex hrz gap-4 max-w-lg h-44 max-h-[30vw] w-full bg-white rounded p-1">
		<ValueImage value={values[0]} guess={value} />
		<ValueImage value={values[1]} guess={-value} />
	</div>
	<div class="p-1 text-base text-right w-full">*not to scale</div>
	<FracQuestion {question} />
</div>
