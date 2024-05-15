<script lang="ts">
	import type { Question } from '$lib/data/questions';

	export let question: Question;

	$: values = question.values;
</script>

<div class="flex vrt text-3xl text-center">
	<!-- <div class="max-w-xl">
		{#each parts as part, i}
			<span class={i % 2 ? 'font-bold' : ''}>{part}</span>
		{/each}
	</div> -->
	<div class="flex hrz gap-2">
		<p class="text-2xl">What is</p>
		<div class="flex vrt p-2 font-serif italic max-w-md">
			<p class="p-1">X</p>
			<hr class="border-y w-full border-solid border-secondary" />
			<p class="p-1">Y</p>
		</div>
		?
	</div>
	<div class="flex vrt p-2 font-serif font-bold italic max-w-md">
		<p class="p-2">{values[0].name}</p>
		<hr class="border-y w-full border-solid border-secondary" />
		<p class="p-2">{values[1].name}</p>
	</div>
	<div class="flex hrz gap-4 max-w-lg max-h-72">
		<div class="max-h-full h-full aspect-square vrt">
			<img src={values[0].image} class="object-cover h-full rounded-md" alt={values[0].name} />
		</div>
		<div class="max-h-full h-full aspect-square vrt">
			<img src={values[1].image} class="h-full rounded-md" alt={values[1].name} />
		</div>
	</div>
</div>
