<script>
	import DarkModeButton from './DarkModeButton.svelte';
	import Guesser from './Guesser.svelte';
</script>

<div class="w-full h-screen vrt justify-stretch bg-theme">
	<div class="w-full hrz justify-end"><DarkModeButton /></div>
	<div class="vrt center gap-2 grow">
		<Guesser />
	</div>
</div>
