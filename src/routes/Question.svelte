<script lang="ts">
	export let question = '';

	$: questionWithMark = question.endsWith('?') ? question : question + '?';
	$: parts = questionWithMark.split('*');
	$: values = [parts[1], parts[3]];
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
		<p class="p-2">{values[0]}</p>
		<hr class="border-y-2 w-full border-solid border-secondary" />
		<p class="p-2">{values[1]}</p>
	</div>
</div>
