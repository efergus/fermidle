<script>
    import '../app.css';
    let base = 5; //TODO: get actual base from data etc

    let guess = '';
</script>

<div class="hrz items-start">
    <b class="text-5xl">
        {base} ⋅ 10
    </b>
    <input
        class="border-2 rounded border-contrast max-w-32"
        type="text"
        placeholder="Guess..."
        bind:value={guess} />
</div>

<style>

</style>