<script>
	import DarkModeButton from './DarkModeButton.svelte';
	import HamburgerMenu from './SlideMenu.svelte';
</script>

<div class="w-full h-screen vrt justify-stretch bg-theme">
	<HamburgerMenu>
		<div
			class="vrt items-start gap-2 p-2 min-w-56 bg-theme border-b-2 border-l-2 border-secondary rounded-bl-lg"
		>
			<p>A menu item</p>
			<p>Ok we probably don't really need a menu but I wanted to make this</p>
			<DarkModeButton />
		</div></HamburgerMenu
	>
	<div class="vrt center gap-2 grow">
		<h1>Hello Adam</h1>
		<p class="border-b">
			Visit <a class="hover:bg-secondary px-1 -mx-0.5" href="https://kit.svelte.dev"
				>kit.svelte.dev</a
			> to read the documentation
		</p>
		<div class="p-4 rounded-lg vrt items-stretch gap-2">
			<p class="p-2 rounded-lg bg-primary grow text-center">Primary Background</p>
			<p class="py-2 px-4 rounded-lg bg-secondary">Secondary Background</p>
		</div>
	</div>
</div>
