<script lang="ts">
	import { getAnswer, provideAnswer } from '$lib/context/answer';
	import '../app.css';
	import Answer from './Answer.svelte';
	import DarkModeButton from './DarkModeButton.svelte';
	import Guesser from './Guesser.svelte';

	let guess = 0;
	let guesses: number[] = [];

	provideAnswer();

	const answer = getAnswer();
</script>

<div class="w-full h-screen vrt justify-stretch bg-theme">
	<div class="w-full hrz justify-end"><DarkModeButton /></div>
	<div class="vrt center w-full gap-2 grow p-2">
		<Guesser
			on:change={() => {
				guesses = [...guesses, guess];
			}}
			bind:guess
		/>
		<Answer values={guesses} bind:target={$answer} />
	</div>
</div>
