<script lang="ts">
	import { setAnswer } from '$lib/context/answer';
	import { dispatchers, ident } from '$lib/dispatch';
	import { onMount } from 'svelte';

	export let value = 0;
	export let enabled = true;
	export let placeholder = '0';

	let input: HTMLInputElement | null = null;

	export function focus(focus = true) {
		if (focus) {
			input?.focus();
		} else {
			input?.blur();
		}
	}

	const { change } = dispatchers({
		change: ident<number>
	});

	const set = (newValue: string | number, stayPut = true) => {
		if (!input) return;
		newValue = newValue.toString();
		const start = input.selectionStart ?? 0;
		input.value = newValue;
		if (stayPut) {
			input.setSelectionRange(start, start);
		}
		value = parse(newValue);
		return false;
	};
	const parse = (value: string) => {
		return Number(value) || 0;
	};
	// Limit to 2 digits, no leading zeros, keep negation
	const cleanupString = (value: string) => value.replace(/^(-?)\d*?([1-9]?\d?)$/, '$1$2');
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

	const keyListener = (e: KeyboardEvent) => {
		if (!input) return;
		e.stopPropagation();
		const key = e.key;
		const target = input;
		const val = target.value;
		if (['ArrowDown', 'ArrowUp'].includes(key)) {
			e.preventDefault();
			cleanup(target, value + (key === 'ArrowUp' ? 1 : -1), true, false);
			return;
		}
		if (key === 'Enter') {
			e.preventDefault();
			focus(false);
			change(parse(val));
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
				: !/^[-\d]$/.test(e.key)
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
			cleanup(input, value.toString(), true, false);
		}
	}
	$: {
		if (input) {
			setAnswer(input);
		}
	}
</script>

<input
	class="peer rounded border-2 border-secondary focus:border-contrast w-[3.5ch] text-4xl text-center font-semibold"
	type="text"
	inputmode="numeric"
	pattern="-?[0-9]*"
	value=""
	{placeholder}
	disabled={!enabled}
	bind:this={input}
	on:focus
	on:input
	on:input={(e) => {
		value = parse(e.currentTarget.value);
	}}
	on:keydown={keyListener}
	on:input={(e) => {
		cleanup(e.currentTarget, e.currentTarget.value);
	}}
/>
