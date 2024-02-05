<script lang="ts">
	import clsx from 'clsx';
	import Increment from './Increment.svelte';
	import ChevronDown from '$lib/icons/ChevronDown.svelte';
	import ChevronsDown from '$lib/icons/ChevronsDown.svelte';
	import ChevronUp from '$lib/icons/ChevronUp.svelte';
	import ChevronsUp from '$lib/icons/ChevronsUp.svelte';
	import { onMount } from 'svelte';
	import IntInput from './IntInput.svelte';
	import { spring } from 'svelte/motion';

	export let guess = 0;
	export let digit = 5;

	export function focus() {
		input?.focus();
	}

	let guessDisplayAmt = spring(0, { stiffness: 0.1, damping: 0.8 });
	let guessDisplay = '';

	let focused = false;

	let input: IntInput;
	let inputGroup: HTMLDivElement | null = null;

	onMount(() => {
		document.addEventListener('click', () => {
			focused = !!inputGroup?.contains(document.activeElement);
		});
	});

	const incrementer = (value: number) => () => {
		guess += value;
	};

	$: console.log(guess);
	$: $guessDisplayAmt = guess;
	$: {
		const amt = Math.round($guessDisplayAmt);
		const d = digit.toString();
		if (amt >= 0) {
			guessDisplay = d + '0'.repeat(amt);
		} else {
			guessDisplay = '0.' + '0'.repeat(-amt - 1) + d;
		}
	}
</script>

<div class="vrt gap-4 w-full">
	<div class="hrz items-start">
		<div class="h-full vrt justify-end">
			<b class="text-8xl">
				{digit} ⋅ 10
			</b>
		</div>
		<div class={clsx('vrt rounded', focused && 'outline-contrast')} bind:this={inputGroup}>
			<Increment show={focused} on:click={incrementer(5)}>
				<ChevronsUp />
			</Increment>
			<Increment show={focused} on:click={incrementer(1)}>
				<ChevronUp />
			</Increment>
			<IntInput
				bind:this={input}
				bind:value={guess}
				on:focus={() => {
					focused = true;
				}}
			/>
			<Increment show={focused} on:click={incrementer(-1)}>
				<ChevronDown />
			</Increment>
			<Increment show={focused} on:click={incrementer(-5)}>
				<ChevronsDown />
			</Increment>
		</div>
	</div>
	<div class="text-4xl w-full max-w-[20ch] h-[5em] break-words">
		{guessDisplay}
	</div>
</div>

<style>
</style>
