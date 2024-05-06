<script lang="ts">
	import { getAnswer, provideAnswer } from '$lib/context/answer';
	import { random_question } from '$lib/data/questions';
	import '../app.css';
	import Answer from './Answer.svelte';
	import DarkModeButton from './DarkModeButton.svelte';
	import Guesser from './Guesser.svelte';
	import Question from './Question.svelte';

	let guess = 0;
	let guesses: number[] = [];

	provideAnswer();

	const answer = getAnswer();
	let question = random_question();
	$: magnitude = Math.floor(Math.log10(question.answer));
	$: digit = Math.round(question.answer / 10 ** magnitude);
</script>

<div class="w-full h-screen vrt justify-stretch bg-theme">
	<div class="w-full hrz justify-end"><DarkModeButton /></div>
	<div
		class="vrt center w-full h-full gap-2 grow pb-6 overflow-auto"
		style="scrollbar-gutter: stable both-edges;"
	>
		<Question question={question.question} />
		<Guesser
			on:change={() => {
				if (guess === magnitude) {
					question = random_question();
					guesses = [];
				} else {
					guesses = [...guesses, guess];
					console.log(question);
				}
			}}
			bind:guess
			{digit}
		/>
		<Answer values={guesses} bind:target={$answer} />
	</div>
</div>
