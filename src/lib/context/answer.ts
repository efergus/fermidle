import { uniqueId } from '$lib/uniqueId';
import { getContext, setContext } from 'svelte';
import { writable, type Writable } from 'svelte/store';

const key = uniqueId('answer');

type AnswerContext = {
	element: Writable<Element | null>;
	setAnswer(e: Element): void;
};

function get() {
	return getContext<AnswerContext>(key);
}

export function getAnswer() {
	return get().element;
}

export function setAnswer(e: Element) {
	get().setAnswer(e);
}

export function provideAnswer() {
	const element = writable<Element | null>(null);
	setContext<AnswerContext>(key, {
		element,
		setAnswer(e: Element) {
			element.set(e);
		}
	});
}
