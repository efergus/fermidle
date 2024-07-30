import localforage from 'localforage';
import { getGlobalSeed } from './questions';
import { onBrowser } from '$lib/window';

export type AnswerRecord = {
	questionId: string;
	guesses: number[];
	correct: boolean | null;
};

export type AnswerStorage = AnswerRecord | null;

const answerStore = onBrowser()
	? localforage.createInstance({
			name: 'answers'
		})
	: null;

export async function getAnswers(seed?: string): Promise<AnswerStorage> {
	if (!answerStore) return null;
	seed = seed ?? (await getGlobalSeed());
	const answers = await answerStore.getItem<AnswerStorage>(seed);
	return answers ?? null;
}

export async function setAnswers(answers: AnswerStorage, seed?: string) {
	if (!answerStore) return;
	seed = seed ?? (await getGlobalSeed());
	await answerStore.setItem(seed, answers);
}

export async function isComplete(seed: string): Promise<boolean> {
	if (!answerStore) return false;
	// Deliberate use of != for null or undefined
	return (await getAnswers(seed))?.correct != null;
}
