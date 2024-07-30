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

export function getAnswerElement() {
	return get().element;
}

export function setAnswerElement(e: Element) {
	get().setAnswer(e);
}

export function provideAnswerElement() {
	const element = writable<Element | null>(null);
	setContext<AnswerContext>(key, {
		element,
		setAnswer(e: Element) {
			element.set(e);
		}
	});
}
