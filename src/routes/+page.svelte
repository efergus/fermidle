<script lang="ts">
	import { onMount } from 'svelte';
	import '../app.css';
	import DarkModeButton from './DarkModeButton.svelte';
	import Guesser from './Guesser.svelte';

	let guess = 0;
	let input: Guesser;

	// onMount(() => {
	// 	document.addEventListener('keydown', (e) => {
	// 		if (e.key === 'ArrowUp') {
	// 			guess += 1;
	// 		} else if (e.key === 'ArrowDown') {
	// 			guess -= 1;
	// 		}
	// 		if (e.key === ' ' || e.key.length > 1) {
	// 			e.stopPropagation();
	// 			return;
	// 		}
	// 		input?.focus();
	// 		e.preventDefault();
	// 	});
	// });
</script>

<!-- svelte-ignore a11y-interactive-supports-focus -->
<div class="w-full h-screen vrt justify-stretch bg-theme" role="spinbutton">
	<div class="w-full hrz justify-end"><DarkModeButton /></div>
	<div class="vrt center w-full gap-2 grow">
		<Guesser bind:this={input} bind:guess />
	</div>
</div>
