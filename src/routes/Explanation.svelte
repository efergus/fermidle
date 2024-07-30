<script lang="ts">
	import { type Question } from '$lib/data/questions';
	import { scientific } from '$lib/scientific';
	import Scientific from './format/Scientific.svelte';
	import ValueImage from './ValueImage.svelte';
	import Units from './format/Units.svelte';
	import Modal from './Modal.svelte';
	import FracQuestion from './FracQuestion.svelte';
	import Frac from './format/Frac.svelte';
	import Rotate from '$lib/icons/Rotate.svelte';
	import clsx from 'clsx';

	export let question: Question;
	export let correct = true;
	export let open = true;
	export let guesses: number[] = [];
	export let reset = () => {};

	$: values = question.values.map(({ name, value }) => {
		const [numStr, units] = value.split(' ');
		const num = parseFloat(numStr);
		return {
			name,
			num,
			units,
			scientific: scientific(num)
		};
	});
	const vars = ['X', 'Y'];
	$: len = guesses.length;
</script>

<Modal showModal>
	<div class="vrt items-start w-full pb-2 px-2 gap-2 font-serif">
		<div
			class="w-full flex flex-col gap-2 items-center px-2 font-bold font-sans text-center text-balance"
		>
			{#if correct}
				<h2>{len === 1 ? 'Impressive' : 'Correct'}!</h2>
				<p>You got the answer in {len} guess{len === 1 ? '!' : 'es.'}</p>
				<div class="flex gap-2 mt-2">
					{#each guesses as guess, i}
						<div
							class={clsx(
								i + 1 === len ? 'bg-primary scale-125 shadow' : 'bg-secondary',
								'px-2 py-1 rounded w-10 h-10 vrt justify-center'
							)}
						>
							<p>{guess}</p>
						</div>
					{/each}
				</div>
			{:else}
				<h2>Better luck next time...</h2>
			{/if}
		</div>
		{#each values as value, i}
			<div class="flex gap-2 justify-between items-center w-full italic">
				<div class="flex gap-2 items-center">
					<p class="text-xl whitespace-nowrap">{vars[i]} =</p>
					<p class="font-bold text-balance">{value.name}</p>
				</div>
				<div class="flex items-center gap-2 text-2xl">
					≈ <Scientific value={value.num} />
					<Units units={value.units} />
				</div>
			</div>
		{/each}
		<div class="flex flex-col w-full items-start">
			<div
				class="flex flex-wrap items-center justify-end w-full max-w-full gap-2 font-serif italic text-2xl whitespace-nowrap"
			>
				<div class="flex vrt p-1 text-xl italic max-w-md">
					<Frac>
						<p slot="num">{'X'}</p>
						<p slot="den">{'Y'}</p>
					</Frac>
				</div>
				≈
				<Frac>
					<div slot="num" class="flex items-end gap-2">
						<Scientific value={values[0].num} />
						<Units units={values[0].units} />
					</div>
					<div slot="den" class="flex items-end gap-2">
						<Scientific value={values[1].num} />
						<Units units={values[1].units} />
					</div>
				</Frac> =
				<Frac>
					<p slot="num">{values[0].scientific.base}</p>
					<p slot="den">{values[1].scientific.base}</p>
				</Frac>·
				<Frac>
					<p slot="num">
						<Scientific
							><p slot="base">10</p>
							<p slot="exp">{values[0].scientific.magnitude}</p></Scientific
						>
					</p>
					<p slot="den">
						<Scientific
							><p slot="base">10</p>
							<p slot="exp">{values[1].scientific.magnitude}</p></Scientific
						>
					</p>
				</Frac>
				{#if values[0].units || values[1].units}·
					<Frac>
						<p slot="num">
							<Units units={values[0].units} />
						</p>
						<p slot="den">
							<Units units={values[1].units} />
						</p>
					</Frac>
				{/if} ≈
				<Scientific value={question.answer} />
			</div>
		</div>
		<div class="flex w-full justify-center mt-6 font-sans">
			<button
				class="flex gap-4 bg-primary px-4 py-2 rounded"
				on:click={() => {
					open = false;
					reset();
				}}
				><slot /> <Rotate />
			</button>
		</div>
	</div>
</Modal>
