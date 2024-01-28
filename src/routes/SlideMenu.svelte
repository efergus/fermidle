<script>
	import HamburgerToggle from './MenuToggle.svelte';

	export let open = false;
</script>

<div class="relative w-full">
	<div class="menu">
		<slot />
		<HamburgerToggle bind:checked={open} />
	</div>
</div>

<style lang="postcss">
	div.menu {
		transform: translateY(-100%);
		@apply absolute top-0 right-0 transition-transform max-w-fit;
	}
	div.menu:has(label > input.menu:checked) {
		transform: translateY(0);
	}
</style>
