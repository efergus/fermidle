<script>
    import '../app.css';
    let base = 5; //TODO: get actual base from data etc

    let inputField;
    let newFieldValue = '';

    function isNumeric(str) {
        if (typeof str != "string") return false // we only process strings!  
        return !isNaN(parseInt(str)) && // use type coercion to parse the _entirety_ of the string (`parseFloat` alone does not do this)...
                !isNaN(parseFloat(str)) // ...and ensure strings of whitespace fail
     }

    const onInput = (event) => {
        if (event.key !== 'Enter') return;
        if (!isNumeric(newFieldValue)) return;
        console.log(newFieldValue);
        inputField.value = '';
    };
</script>

<div class="hrz items-start">
    <b class="text-5xl">
        {base} ⋅ 10
    </b>
    <input
        class="border-2 rounded border-contrast max-w-32"
        name="inputField1"
        type="text"
        placeholder="Guess..."
        bind:this={inputField}
        on:keydown={onInput}
        bind:value={newFieldValue} />
</div>
<!-- <p>User input: {newFieldValue || "..."}</p> -->

<style>

</style>