<script lang="ts">
	export let show = true;
	export let disabled = false;

	let shown = false;

	$: shown = show || shown;
</script>

<button
	on:click
	{disabled}
	class={`w-full h-full left-0 py-1 rounded vrt center transition-opacity enabled:hover:bg-secondary ${show ? 'opacity-100' : shown ? 'opacity-40' : 'opacity-0'}`}
	tabindex="-1"
>
	<slot />
</button>
