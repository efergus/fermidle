<script lang="ts">
	import type { Value } from '$lib/data/questions';

	export let value: Value;
	export let guess: number;
	export let fallback =
		'https://upload.wikimedia.org/wikipedia/commons/5/5a/Black_question_mark.png';

	// $: repeat = guess < 0 ? 'repeat' : 'no-repeat';
	let repeat = 'no-repeat';
	$: size = guess < 0 ? `${Math.min(2 ** ((guess - 1) / 2) * 0.98 + 0.02, 1) * 100}%` : 'contain';
	$: image = value.image?.startsWith('https://') ? value.image : fallback;
</script>

<div
	class="max-h-full h-full w-full vrt basis-1/2 bg-center bg-white"
	style={`background-image: url(${image}); background-repeat: ${repeat}; background-size: ${size}`}
	role="img"
	title={value.name}
></div>
