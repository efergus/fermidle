<script lang="ts">
	import { getAnswer, provideAnswer } from '$lib/context/answer';
	import '../app.css';
	import Answer from './Answer.svelte';
	import DarkModeButton from './DarkModeButton.svelte';
	import Guesser from './Guesser.svelte';
	import { random_question, type Question } from '$lib/data/questions';
	import { onMount } from 'svelte';

	let guess = 0;
	let guesses: number[] = [];
	let question: Question | undefined;
	let digit: number | undefined;
	let shown_answer: number | undefined;

	provideAnswer();

	const answer = getAnswer();

	onMount(() => {
		question = random_question();
		// console.log(random_question());
	});
</script>

<div class="w-full h-screen vrt justify-stretch bg-theme">
	<div class="w-full hrz justify-end"><DarkModeButton /></div>
	<div class="vrt center w-full gap-2 grow p-2">
		<p>{question?.question}</p>
		<p>answer was: {shown_answer ?? ''}</p>
		<Guesser
			on:change={() => {
				// const value = question?.answer ?? 1;
				// shown_answer = Math.round(Math.log10(value));
				// digit = Math.round(value / 10 ** shown_answer);
				// question = random_question();
				// guesses = [...guesses, guess];
				const value = question?.answer ?? 1;
				let real_answer = Math.round(Math.log10(value));
				digit = Math.round(value / 10 ** real_answer);
				guesses = [...guesses, guess];
				if (guess === real_answer) {
					shown_answer = real_answer;
					question = random_question();
				}
			}}
			{digit}
			bind:guess
		/>
		<Answer values={guesses} bind:target={$answer} />
	</div>
</div>
