<script lang="ts">
	export let show = true;

	let shown = false;

	$: shown = show || shown;
</script>

<button
	on:click
	class={`w-full h-full left-0 py-1 rounded vrt center transition-opacity hover:bg-secondary ${show ? 'opacity-100' : shown ? 'opacity-40' : 'opacity-0'}`}
>
	<slot />
</button>
