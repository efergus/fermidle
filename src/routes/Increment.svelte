<script lang="ts">
	export let disabled = false;
</script>

<button
	on:click
	{disabled}
	class="w-full h-full left-0 py-1 rounded vrt center enabled:hover:bg-secondary disabled:opacity-30"
	tabindex="-1"
>
	<slot />
</button>
