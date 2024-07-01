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

	export let question: Question;
	export let correct = true;
	export let open = true;
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
</script>

<Modal showModal>
	<div class="vrt items-start w-full py-4 gap-2">
		<div class="w-full">
			{#if correct}
				<h1>Correct!</h1>
			{:else}
				<h1>Better luck next time...</h1>
			{/if}
		</div>
		{#each values as value}
			<div class="flex gap-2 justify-between w-full">
				<p>
					<span class="font-bold">{value.name}</span>
				</p>
				<div class="flex items-center gap-2 italic text-2xl">
					≈ <Scientific value={value.num} />
					<Units units={value.units} />
				</div>
			</div>
		{/each}
		<div class="flex flex-col w-full items-start">
			<div><FracQuestion {question} /></div>
			<div
				class="flex flex-wrap items-center justify-end w-full max-w-full gap-2 italic text-2xl whitespace-nowrap"
			>
				≈
				<Frac>
					<div slot="num" class="flex items-center gap-2">
						<Scientific value={values[0].num} />
						<Units units={values[0].units} />
					</div>
					<div slot="den" class="flex items-center gap-2">
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
				</Frac>·
				<Frac>
					<p slot="num">
						<Units units={values[0].units} />
					</p>
					<p slot="den">
						<Units units={values[1].units} />
					</p>
				</Frac> ≈
				<Scientific value={question.answer} />
			</div>
		</div>
		<div class="flex w-full justify-center mt-6">
			<button
				class="flex gap-4 bg-primary px-4 py-2 rounded"
				on:click={() => {
					open = false;
					reset();
				}}
				>Play again? <Rotate />
			</button>
		</div>
	</div>
</Modal>
