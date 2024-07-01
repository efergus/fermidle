<script lang="ts">
	import { scientific } from '$lib/scientific';

	export let base: string = '';
	export let exp: string = '';
</script>

<div class="inline-flex flex-nowrap">
	<slot name="base">{base}</slot>
	<div class="tall"><slot name="exp"><p>{exp}</p></slot></div>
</div>

<style>
	.tall {
		height: 1.5em;
		font-size: 0.7em;
	}
</style>
