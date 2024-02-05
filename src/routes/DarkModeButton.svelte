<script>
	import Moon from './Moon.svelte';
</script>

<label class="fill-contrast hover:bg-primary p-1 m-1 rounded-lg cursor-pointer">
	<input
		id="dark-mode-toggle"
		type="checkbox"
		class="hidden dark-mode-toggle"
		on:change={(e) => {
			console.log(e.currentTarget.checked);
		}}
	/>
	<Moon />
</label>
