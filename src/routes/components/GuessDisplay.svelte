<script lang="ts">
	import { spring } from 'svelte/motion';
	import Frac from '../format/Frac.svelte';

	export let guess: number | null = null;
	export let digit = 5;
	export let lhs = 'X';
	export let rhs = 'Y';

	let guessDisplayAmt = spring(0, { stiffness: 0.1, damping: 0.8 });
	let guessDisplay = [''];

	$: $guessDisplayAmt = guess ?? 0;
	$: {
		const amt = Math.round($guessDisplayAmt);
		const d = digit.toString();
		const zeros = new Array(Math.abs(amt)).fill('0');
		if (amt >= 0) {
			guessDisplay = [d, ...zeros.flatMap((z, i) => (i % 3 === 2 ? [z, ','] : [z])).reverse()];
		} else {
			zeros[0] = '0.';
			guessDisplay = [...zeros, d];
		}
	}
</script>

<div class="flex flex-col items-center font-serif italic text-xl max-w-lg">
	<div class="grid gap-2 w-full max-w-xs break-words content-center items-center">
		<p>X</p>
		<p>=</p>
		<div class="value"><p>{lhs}</p></div>
		<p>Y</p>
		<p>=</p>
		<div class="value"><p>{rhs}</p></div>
	</div>

	<div class="flex gap-2 w-full justify-center items-center col-span-3 min-h-[5em]">
		<Frac>
			<p slot="num">X</p>
			<p slot="den">Y</p>
		</Frac>
		<p class="font-sans">≈</p>
		<div class="flex flex-wrap">
			{#if guess === null}
				<p class="value">???</p>
			{:else}
				{#each guessDisplay as item}
					<p>{item}</p>
				{/each}
			{/if}
		</div>
	</div>
</div>

<style lang="postcss">
	.grid {
		grid-template-columns: min-content min-content 1fr;
	}
	div.value {
		@apply flex justify-end text-center font-bold text-balance;
	}
</style>
