<script lang="ts">
	import { spring } from 'svelte/motion';

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

<div class="text-xl w-full max-w-md break-words flex flex-wrap">
	<p class="font-bold">{lhs} ≈</p>
	<div class="ml-2 flex flex-wrap justify-stretch">
		{#if guess === null}
			<p>???</p>
		{:else}
			{#each guessDisplay as item}
				<p>{item}</p>
			{/each}
		{/if}
		<div class="vrt justify-end grow">
			<p class="ml-2 font-bold">· {rhs}</p>
		</div>
	</div>
</div>

<style lang="postcss">
</style>
