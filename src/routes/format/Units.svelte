<script lang="ts">
	import Frac from './Frac.svelte';
	import Scientific from './Scientific.svelte';

	export let units = '';

	function power_pairs(units: string) {
		const parts = units.split(/(\d+)/g).filter((x) => x);
		const pairs = [];
		let unit = '';
		for (const part of parts) {
			const exp = parseInt(part);
			if (unit && exp) {
				pairs.push({
					unit,
					exp
				});
			} else {
				unit = part;
			}
		}
		const lastidx = parts.length - 1;
		if (parts.length && !parseInt(parts[lastidx])) {
			pairs.push({
				unit: parts[lastidx],
				exp: 1
			});
		}
		return pairs;
	}

	function unit_powers(units: string) {
		const unit_parts = units.split('/').map(power_pairs);
		const num = unit_parts[0] ?? [];
		const den = unit_parts[1] ?? [];
		return { num, den };
	}

	$: powers = unit_powers(units);

	$: console.log({ powers });
</script>

<div class="inline">
	{#if powers.den.length}
		<Frac>
			<div slot="num">
				{#each powers.num as unit}
					{#if unit.exp !== 1}
						<Scientific>
							<p slot="base">{unit.unit}</p>
							<p slot="exp">{unit.exp}</p>
						</Scientific>
					{:else}
						{unit.unit}
					{/if}
				{/each}
				{#if !powers?.num.length}
					<p>1</p>
				{/if}
			</div>
			<div slot="den">
				{#each powers.den as unit}
					{#if unit.exp !== 1}
						<Scientific>
							<p slot="base">{unit.unit}</p>
							<p slot="exp">{unit.exp}</p>
						</Scientific>
					{:else}
						{unit.unit}
					{/if}
				{/each}
			</div>
		</Frac>
	{:else}
		{#each powers.num as unit}
			{#if unit.exp !== 1}
				<Scientific>
					<p slot="base">{unit.unit}</p>
					<p slot="exp">{unit.exp}</p>
				</Scientific>
			{:else}
				{unit.unit}
			{/if}
		{/each}
	{/if}
</div>
