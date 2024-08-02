<script lang="ts">
	import { getAnswerElement, provideAnswerElement } from '$lib/context/answer';
	import {
		getGlobalSeed,
		getTodaySeed,
		random_hint,
		random_question,
		seeded_prng,
		setGlobalSeed,
		type Hint as HintType,
		type Question
	} from '$lib/data/questions';
	import '../app.css';
	import Answer from './Answer.svelte';
	import DarkModeButton from './DarkModeButton.svelte';
	import Guesser from './Guesser.svelte';
	import QuestionView from './QuestionView.svelte';
	import Hint from './Hint.svelte';
	import Example from './Example.svelte';
	import Rotate from '$lib/icons/Rotate.svelte';
	import FermidleIcon from '$lib/icons/FermidleIcon.svelte';
	import Modal from './Modal.svelte';
	import { scientific } from '$lib/scientific';
	import Explanation from './Explanation.svelte';
	import { onMount } from 'svelte';
	import { getAnswers, isComplete, setAnswers } from '$lib/data/store';
	import GuessDisplay from './components/GuessDisplay.svelte';

	let guess = 0;
	let guesses: number[] = [];
	let showHelp = false;
	let today = getTodaySeed();
	let seed = today;
	let daily: boolean | null = null;
	let changed = false;

	provideAnswerElement();

	const answer = getAnswerElement();
	let question: Question | undefined;
	$: digit = question ? scientific(question.answer).digit : 1;
	let hint: HintType | undefined;
	let done = false;
	let correct: boolean | null = null;
	let dailyTodo = false;

	async function reset() {
		if (!seed) return;
		if (dailyTodo) {
			setSeed(today);
		} else {
			const rng = seeded_prng(Math.random().toString());
			setSeed(rng.int(0, 1e10).toString());
		}
		guess = 0;
		guesses = [];
		correct = null;
		hint = undefined;
		changed = false;
	}

	function setSeed(newSeed: string) {
		seed = newSeed;
		setGlobalSeed(seed);
		if (seed === today) {
			dailyTodo = false;
			window.sessionStorage.setItem('practice', '');
		} else {
			isComplete(today).then((complete) => (dailyTodo = !complete));
		}
		getAnswers(seed).then((answers) => {
			guesses = answers?.guesses.slice() ?? [];
		});
		return seed;
	}

	onMount(async () => {
		const practice = window.sessionStorage.getItem('practice');
		if (practice === null) {
			// practice if the page is opened to a specific question
			daily = seed === today;
			window.sessionStorage.setItem('practice', daily ? '' : 'true');
		} else {
			// only auto-load todays if we haven't already done it
			daily = !(await isComplete(today));
		}
		seed = daily ? today : getGlobalSeed();
		question = await random_question(seed);
		// Set today every 5 mins
		setInterval(() => {
			today = getTodaySeed();
			isComplete(today).then((complete) => {
				dailyTodo = !complete;
			});
		}, 1000 * 60);
		setSeed(seed);
	});

	$: random_question(seed).then((next) => (question = next));
	$: if (question && guesses.length) {
		const lastGuess = guesses[guesses.length - 1];
		const answerMagnitude = Math.floor(Math.log10(question.answer));
		if (lastGuess === answerMagnitude) {
			correct = true;
		} else if (guesses.length >= 6) {
			correct = false;
		}
	}
	$: done = correct !== null;
	$: {
		guess;
		changed = true;
	}
</script>

<svelte:head>
	<meta name="description" content="I'm Ethan Ferguson, and this is my website." />
</svelte:head>

<Modal bind:showModal={showHelp}>
	{#if showHelp}
		<Example />
	{/if}
</Modal>

<div class="w-full h-screen relative vrt justify-stretch bg-theme gap-4">
	<div class="w-full hrz justify-between sticky top-0 bg-theme">
		<div>
			<button
				class="p-1 m-1 stroke-contrast enabled:hover:bg-primary rounded-lg disabled:opacity-30"
				on:click={reset}
				disabled={seed === today && !done}
				><Rotate />
			</button>
		</div>
		<div class="max-w-lg w-full hrz justify-between font-bold text-2xl">
			<div class="basis-0 grow" />
			<a href="/"><FermidleIcon /></a>
			<div class="flex justify-end basis-0 grow">
				<button
					class="px-3 hover:bg-primary active:bg-primary/80 rounded"
					on:click={() => (showHelp = true)}>?</button
				>
			</div>
		</div>
		<DarkModeButton />
	</div>
	<div class="w-full h-full pb-6 px-2" style="scrollbar-gutter: stable both-edges;">
		<div class="vrt gap-2">
			<QuestionView {question} value={guess} />
			<GuessDisplay
				guess={changed ? guess : null}
				{digit}
				lhs={question?.values[0].name}
				rhs={question?.values[1].name}
			/>
			<Guesser
				on:change={async () => {
					if (done || !question) {
						return;
					}
					if (guesses.includes(guess)) {
						return;
					}
					const prev = guesses.length ? guesses[guesses.length - 1] : undefined;
					const nextGuesses = [...guesses, guess];
					hint = await random_hint(guess + Math.log10(digit), Math.log10(question.answer), {
						direction_skew: hint?.type === 'direction' ? 0 : 0.4,
						num: guesses.length,
						previous_guess_magnitude: prev
					});

					changed = true;
					guesses = nextGuesses;
					done = hint?.type === 'correct' || guesses.length >= 6;
					if (done) {
						correct = hint?.type === 'correct';
					}
					setAnswers(
						{
							questionId: question.id,
							guesses,
							correct
						},
						seed
					);
				}}
				bind:guess
				{digit}
				disabled={done}
			/>
			{#if done && question && correct !== null}
				<Explanation {question} {reset} {correct} {guesses}>
					Play {dailyTodo ? "today's" : 'again'}?
				</Explanation>
			{:else}
				<Hint {hint} />
			{/if}
			<Answer values={guesses} bind:target={$answer} />
		</div>
	</div>
</div>
