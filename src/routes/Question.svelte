<script lang="ts">
	import type { Question } from '$lib/data/questions';
	import ValueImage from './ValueImage.svelte';

	export let question: Question;
	export let value: number = 1;

	$: values = question.values;
	$: repeat1 = value < 0 ? 'repeat' : 'no-repeat';
	$: repeat2 = value > 0 ? 'repeat' : 'no-repeat';
</script>

<div class="flex vrt text-xl max-w-lg w-full text-center">
	<!-- <div class="flex hrz gap-1">
		<p class="text-2xl">What is</p>
		<div class="flex vrt p-2 font-serif italic max-w-md">
			<p class="px-1">X</p>
			<hr class="border-y w-full border-solid border-secondary" />
			<p class="px-1">Y</p>
		</div>
		?
	</div> -->
	<div class="flex hrz gap-4 max-w-lg h-44 max-h-[30vw] w-full">
		<ValueImage value={values[0]} guess={value} />
		<ValueImage value={values[1]} guess={-value} />
	</div>
	<div class="p-1 text-base text-right w-full">*not to scale</div>
	<div class="flex vrt p-1 font-serif font-bold italic max-w-md">
		<p class="p-1">{values[0].name}</p>
		<hr class="border-y w-full border-solid border-secondary" />
		<p class="p-1">{values[1].name}</p>
	</div>
</div>
