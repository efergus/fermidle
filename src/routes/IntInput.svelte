<script lang="ts">
	import { onMount } from 'svelte';
	import { slide } from 'svelte/transition';

	export let value = 0;

	export function focus() {
		input?.focus();
	}

	let input: HTMLInputElement | null = null;

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
		if (document.activeElement !== document.body) {
			return;
		}
		if (!['ArrowUp', 'ArrowDown', 'Backspace', 'Delete'].includes(e.key) && !/[-\d]/.test(e.key)) {
			e.stopPropagation();
			return;
		}
		input?.focus();
		e.preventDefault();
	};

	onMount(() => {
		document.addEventListener('keydown', (e) => {
			keyListener(e);
			return () => document.removeEventListener('keydown', keyListener);
		});
	});

	$: {
		if (input && parse(input.value) !== value) {
			cleanup(input, value.toString(), true, false);
		}
	}
</script>

<input
	class="peer rounded border-2 border-secondary focus:border-contrast w-[3.5ch] text-4xl text-center font-semibold"
	type="text"
	inputmode="numeric"
	pattern="-?[0-9]*"
	value="0"
	bind:this={input}
	on:focus
	on:change
	on:input
	on:input={(e) => {
		value = parse(e.currentTarget.value);
	}}
	on:keydown={(e) => {
		e.stopPropagation();
		const key = e.key;
		const target = e.currentTarget;
		const val = target.value;
		if (['ArrowDown', 'ArrowUp'].includes(key)) {
			e.preventDefault();
			cleanup(target, value + (key === 'ArrowUp' ? 1 : -1), true, false);
			// target.setSelectionRange(val.length, val.length);
			return;
		}
		console.log(key);
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
	}}
	on:input={(e) => {
		cleanup(e.currentTarget, e.currentTarget.value);
	}}
/>
