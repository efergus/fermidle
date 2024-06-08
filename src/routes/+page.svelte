<script lang="ts">
	import { getAnswer, provideAnswer } from '$lib/context/answer';
	import { random_hint, random_question, type Hint as HintType } from '$lib/data/questions';
	import '../app.css';
	import Answer from './Answer.svelte';
	import DarkModeButton from './DarkModeButton.svelte';
	import Guesser from './Guesser.svelte';
	import Question from './Question.svelte';
	import Hint from './Hint.svelte';
	import Example from './Example.svelte';
	import Rotate from '$lib/icons/Rotate.svelte';
	import FermidleIcon from '$lib/icons/FermidleIcon.svelte';
	import Modal from './Modal.svelte';
	import { scientific } from '$lib/scientific';
	import Explanation from './Explanation.svelte';

	let guess = 0;
	let guesses: number[] = [];
	let showHelp = false;

	provideAnswer();

	const answer = getAnswer();
	let question = random_question();
	$: digit = scientific(question.answer).digit;
	let hint: HintType | undefined;

	function reset() {
		guess = 0;
		guesses = [];
		question = random_question();
	}
</script>

<Modal bind:showModal={showHelp}>
	<Example />
</Modal>

<div class="w-full h-screen vrt justify-stretch bg-theme gap-4">
	<div class="w-full hrz justify-between">
		<div>
			<button class="p-1 m-1 stroke-contrast hover:bg-primary rounded-lg" on:click={reset}
				><Rotate /></button
			>
		</div>
		<div class="max-w-lg w-full hrz justify-between font-bold text-2xl">
			<div class="basis-0 grow" />
			<div><FermidleIcon /></div>
			<div class="flex justify-end basis-0 grow">
				<button
					class="px-3 hover:bg-primary active:bg-primary/80 rounded"
					on:click={() => (showHelp = true)}>?</button
				>
			</div>
		</div>
		<DarkModeButton />
	</div>
	<div class="w-full h-full pb-6 px-2 overflow-auto" style="scrollbar-gutter: stable both-edges;">
		<div class="vrt">
			<Question {question} value={guess} />
			<Guesser
				on:change={() => {
					guesses = [...guesses, guess];
					console.log(question);
					hint = random_hint(guess + Math.log10(digit), Math.log10(question.answer), {
						direction_skew: hint?.type === 'direction' ? 0 : 0.4
					});
				}}
				bind:guess
				{digit}
			/>
			{#if hint?.type === 'correct'}
				<Explanation {question} />
			{:else}
				<Hint {hint} />
			{/if}
			<Answer values={guesses} bind:target={$answer} />
		</div>
	</div>
</div>
