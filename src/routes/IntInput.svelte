<script lang="ts">
	import { setAnswerElement } from '$lib/context/answer';
	import { dispatchers, ident } from '$lib/dispatch';
	import CheckIcon from '$lib/icons/CheckIcon.svelte';
	import { onMount } from 'svelte';

	export let value: number | null = 0;
	export let placeholder = '0';
	export let disabled = false;

	let input: HTMLInputElement | null = null;

	export function focus(focus = true) {
		if (focus) {
			input?.focus();
		} else {
			input?.blur();
		}
	}

	const { change } = dispatchers({
		change: ident<number | null>
	});

	/** Set the value of the input, either keeping the cursor in the same position or implicitly moving it to the end */
	const set = (newValue: string | number, stayPut = true) => {
		if (!input) return;
		newValue = newValue.toString();
		const start = input.selectionStart;
		input.value = newValue;
		if (stayPut && start !== null) {
			input.setSelectionRange(start, start);
		}
		value = parse(newValue);
		return false;
	};
	const parse = (value: string) => {
		const num = Number(value);
		if (isNaN(num)) {
			return null;
		}
		return num;
	};
	// Limit to 2 digits, no leading zeros, keep negation
	const cleanupString = (value: string) => value.replace(/^(-?)\d*?([1-9]?\d?)$/, '$1$2');
	/** Set the input value if necessary and keep it in a predictable state
	 * TODO: make this less intrusive, allow copy/cut/paste/undo
	 */
	const cleanup = (
		target: HTMLInputElement,
		value?: string | number,
		forceSet?: boolean,
		stayPut = true
	) => {
		value = (value ?? target.value).toString();
		const cleanedValue = cleanupString(value);
		// If cleanedValue is not a number, just take any digits it has
		if (!/^-?\d*$/.test(cleanedValue)) {
			return set(cleanupString(value.match(/\d/g)?.join('') ?? ''), false);
		}
		if (cleanedValue !== value) {
			return set(cleanedValue, stayPut);
		}
		if (forceSet) {
			set(cleanedValue, stayPut);
		}
	};

	const submit = (e: Event) => {
		if (!input) return;
		e.preventDefault();
		const val = input.value;
		focus(false);
		change(parse(val));
	};

	const keyListener = (e: KeyboardEvent) => {
		if (!input || disabled) return;
		e.stopPropagation();
		const key = e.key;
		const target = input;
		const val = target.value;
		if (['ArrowDown', 'ArrowUp'].includes(key)) {
			e.preventDefault();
			cleanup(target, (value ?? 0) + (key === 'ArrowUp' ? 1 : -1), true, false);
			return;
		}
		if (key === 'Enter') {
			submit(e);
		}
		if (key === 'Escape') {
			focus(false);
		}
		if (key.length > 1) {
			return;
		}
		const start = target.selectionStart;
		const end = target.selectionEnd;

		if (start === null || end === null) {
			return false;
		}
		if (key === '-') {
			if (val[0] === '-') {
				set(val.slice(1));
				target.setSelectionRange(start - 1, start - 1);
			} else {
				set('-' + val);
				target.setSelectionRange(start + 1, start + 1);
			}
			e.preventDefault();
			return;
		}
		if (!/\d/.test(key)) {
			e.preventDefault();
			return;
		}
		if (!val) {
			cleanup(target, key, true, false);
		}
		const newValue = `${val.slice(0, start)}${key}${val.slice(end)}`;
		if (cleanup(target, newValue) === false) {
			e.preventDefault();
			return;
		}
	};

	const outsideKeyListener = (e: KeyboardEvent) => {
		if (document.activeElement !== document.body) {
			return;
		}
		if (
			e.key.length > 1
				? !['ArrowUp', 'ArrowDown', 'Backspace', 'Delete'].includes(e.key)
				: !/^[-\w]$/.test(e.key)
		) {
			return;
		}
		focus();
		if (input) {
			input.value = '';
		}
		keyListener(e);
		e.preventDefault();
	};

	onMount(() => {
		document.addEventListener('keydown', outsideKeyListener);
		return () => document.removeEventListener('keydown', outsideKeyListener);
	});

	$: {
		if (input && parse(input.value) !== value) {
			cleanup(input, (value ?? 0).toString(), true, false);
		}
	}
	$: {
		if (input) {
			setAnswerElement(input);
		}
	}
</script>

<div class="relative">
	<input
		class="peer rounded border-2 border-secondary focus:border-contrast w-[3.5ch] text-4xl text-center font-semibold"
		type="text"
		inputmode="numeric"
		pattern="-?[0-9]*"
		value=""
		{placeholder}
		{disabled}
		bind:this={input}
		on:focus
		on:input={(e) => {
			value = parse(e.currentTarget.value);
		}}
		on:keydown={keyListener}
		on:input={(e) => {
			cleanup(e.currentTarget, e.currentTarget.value);
		}}
	/>

	<button
		class="absolute top-0 right-0 translate-x-full h-full flex items-center px-2 rounded enabled:hover:bg-secondary disabled:opacity-30"
		on:click={submit}
		tabindex="-1"
		{disabled}
		><CheckIcon />
	</button>
</div>
