<script>
	import HamburgerToggle from './MenuToggle.svelte';

	export let checked = false;
	export let duration = 0.15;
</script>

<label class="menu">
	<input type="checkbox" class="menu hidden" bind:checked />
	<svg
		style="--duration:{duration}"
		xmlns="http://www.w3.org/2000/svg"
		width="24"
		height="24"
		viewBox="-12 -12 24 24"
		fill="none"
		stroke="currentColor"
		stroke-width="2"
		stroke-linecap="round"
		stroke-linejoin="round"
		class="feather feather-menu"
		><line class="line1" x1="-9" y1="0" x2="9" y2="0"></line><line
			class="line2"
			x1="-9"
			y1="0"
			x2="9"
			y2="0"
		></line><line class="line3" x1="-9" y1="0" x2="9" y2="0"></line></svg
	>
</label>

<style lang="postcss">
	label.menu {
		@apply p-2 absolute bottom-0 right-0 translate-y-full;
	}

	line {
		transition-property: transform;
		transition-duration: calc(var(--duration) * 1s);
		transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
	}
	.line1 {
		transform: translateY(30%);
	}
	.line2 {
		transform: scaleX(1);
	}
	.line3 {
		transform: translateY(-30%);
	}
	input.menu:checked ~ svg > line.line1 {
		transform: translateY(0) rotate(-45deg);
	}

	input.menu:checked ~ svg > line.line2 {
		transform: scaleX(0);
	}

	input.menu:checked ~ svg > line.line3 {
		transform: translateY(0) rotate(45deg);
	}
</style>
