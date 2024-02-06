<script lang="ts">
	export let show = true;
</script>

<button
	on:click
	class={`w-full h-full left-0 py-1 rounded vrt center transition-opacity hover:bg-secondary ${show ? 'opacity-100' : 'opacity-0'}`}
>
	<slot />
</button>
