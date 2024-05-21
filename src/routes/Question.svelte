<script lang="ts">
	import type { Question } from '$lib/data/questions';

	export let question: Question;
	export let value: number = 1;

	$: values = question.values;
</script>

<div class="flex vrt text-2xl max-w-xl w-full md:text-3xl text-center">
	<div class="flex hrz gap-1">
		<p class="text-2xl">What is</p>
		<div class="flex vrt p-2 font-serif italic max-w-md">
			<p class="px-1">X</p>
			<hr class="border-y w-full border-solid border-secondary" />
			<p class="px-1">Y</p>
		</div>
		?
	</div>
	<div class="flex vrt p-2 font-serif font-bold italic max-w-md">
		<p class="p-1">{values[0].name}</p>
		<hr class="border-y w-full border-solid border-secondary" />
		<p class="p-1">{values[1].name}</p>
	</div>
	<div class="flex hrz gap-4 max-w-xl h-52 max-h-[30vw] w-full">
		<div
			class="max-h-full h-full w-full vrt basis-1/2 bg-center"
			style={`background-image: url(${values[0].image}); background-size: ${Math.min(2 ** (value / 2) * 0.98 + 0.02, 1) * 100}%`}
		></div>
		<div
			class="max-h-full h-full w-full vrt basis-1/2 bg-center"
			style={`background-image: url(${values[1].image}); background-size: ${Math.min(2 ** (-value / 2) * 0.98 + 0.02, 1) * 100}%`}
		></div>
	</div>
	<div class="p-1 text-lg text-right w-full">*not to scale</div>
</div>
