<script lang="ts">
	import { scientific } from '$lib/scientific';

	export let value: number = 1;
	export let precision = 1;

	$: sci = scientific(value, precision);
</script>

<div class="inline-flex flex-nowrap">
	<slot name="base">{sci.base}·10</slot>
	<div class="tall"><slot name="exp"><p>{sci.magnitude}</p></slot></div>
</div>

<style>
	.tall {
		height: 100%;
		transform: translate(0.25ch, -25%);
		font-size: 0.7em;
	}
</style>
