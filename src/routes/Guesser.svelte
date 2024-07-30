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
	export let placeholder = '?';
	export let disabled = false;

	let inputGroup: HTMLDivElement | null = null;

	const incrementer = (value: number) => () => {
		guess += value;
	};
</script>

<div class="vrt gap-4 w-full">
	<div class="hrz items-start">
		<div class="h-full hrz justify-end pt-8 gap-4 text-7xl md:text-8xl">
			<p class="text-6xl">≈</p>
			<b>
				{digit}·10
			</b>
		</div>
		<div class={clsx('vrt rounded mt-[-4px]')} bind:this={inputGroup}>
			<Increment {disabled} on:click={incrementer(1)}>
				<ChevronUp />
			</Increment>
			<IntInput on:change {disabled} bind:value={guess} {placeholder} />
			<Increment {disabled} on:click={incrementer(-1)}>
				<ChevronDown />
			</Increment>
		</div>
	</div>
	<!-- <div class="text-4xl w-full max-w-md break-words flex flex-wrap content-start">
		{#each guessDisplay as item}
			<p>{item}</p>
		{/each}
		<div class="vrt justify-end">
			<p class="pl-2 font-bold text-2xl">{unit}</p>
		</div>
	</div> -->
</div>
