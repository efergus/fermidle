<script lang="ts">
	import clsx from 'clsx';
	import Increment from './Increment.svelte';
	import ChevronDown from '$lib/icons/ChevronDown.svelte';
	import ChevronUp from '$lib/icons/ChevronUp.svelte';
	import { onMount } from 'svelte';
	import IntInput from './IntInput.svelte';
	import { spring } from 'svelte/motion';

	export let guess = 0;
	export let digit = 5;
	export let unit = 'units';

	let guessDisplayAmt = spring(0, { stiffness: 0.1, damping: 0.8 });
	let guessDisplay = [''];

	let focused = false;
	let clearFocusTimeout = () => {};

	let inputGroup: HTMLDivElement | null = null;

	onMount(() => {
		document.addEventListener('click', () => {});
	});

	const incrementer = (value: number) => () => {
		guess += value;
	};

	$: $guessDisplayAmt = guess;
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

<div class="vrt gap-4 w-full">
	<div class="hrz items-start">
		<div class="h-full vrt justify-end pt-8">
			<b class="text-8xl">
				{digit} · 10
			</b>
		</div>
		<div
			class={clsx('vrt rounded')}
			bind:this={inputGroup}
			on:focusin={() => {
				focused = true;
				clearFocusTimeout();
			}}
			on:focusout={() => {
				if (!inputGroup?.contains(document.activeElement)) {
					clearFocusTimeout();
					const handle = setTimeout(() => (focused = false), 2000);
					clearFocusTimeout = () => {
						clearTimeout(handle);
						clearFocusTimeout = () => {};
					};
				}
			}}
		>
			<Increment show={focused} on:click={incrementer(1)}>
				<ChevronUp />
			</Increment>
			<IntInput on:change bind:value={guess} />
			<Increment show={focused} on:click={incrementer(-1)}>
				<ChevronDown />
			</Increment>
		</div>
	</div>
	<div class="text-4xl w-full max-w-md break-words flex flex-wrap content-start">
		{#each guessDisplay as item}
			<p>{item}</p>
		{/each}
		<div class="vrt justify-end">
			<p class="pl-2 font-bold text-2xl">{unit}</p>
		</div>
	</div>
</div>

<style>
</style>
