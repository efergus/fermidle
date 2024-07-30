import random from 'random';
import data from './questions.json';
import { formatISO, isValid, parseISO } from 'date-fns';
import { pushState } from '$app/navigation';
import { writable } from 'svelte/store';

export type Value = {
	value: string;
	name: string;
	image?: string;
};

export type Question = {
	id: string;
	question: string;
	answer: number;
	values: Value[];
};

export function getTodaySeed() {
	return formatISO(new Date(), { representation: 'date' });
}

export function getGlobalSeed() {
	const today = getTodaySeed();
	if (typeof window === 'undefined') {
		return today;
	}
	const url = new URL(window.location.href);
	const params = new URLSearchParams(url.search);

	let seed = params.get('s');

	if (!seed) {
		return today;
	}
	let date = parseISO(seed || '');
	const now = new Date();
	if (isValid(date) && date > now) {
		return today;
	}
	return seed;
}

export function setGlobalSeed(seed: string) {
	const url = new URL(window.location.href);
	const params = new URLSearchParams(url.search);

	if (seed === getTodaySeed()) {
		params.delete('s');
	} else {
		params.set('s', seed);
	}
	url.search = params.toString();
	pushState(url.href, { seed });
}

export function seeded_prng(...seed: (string | number)[]) {
	const seedString = seed.map((x) => x.toString()).join('|') ?? '';
	return random.clone(seedString);
}

export async function random_question(seed: string): Promise<Question> {
	const rng = seeded_prng('question', seed);
	const question = rng.choice(data)!;
	return {
		id: question.id,
		question: question.question,
		answer: question.answer,
		values: question.values.map(({ value, name, image }) => ({ value, name, image }))
	};
}

export type Hint =
	| {
			type: 'closer';
			value: Question;
	  }
	| {
			type: 'delta';
			value: Question;
	  }
	| {
			type: 'direction';
			value: string;
	  }
	| {
			type: 'hotcold';
			value: string;
	  }
	| {
			type: 'message';
			value: string;
	  }
	| {
			type: 'correct';
			value: boolean;
	  };

export function question_difficulty(question: Question) {
	const value_sizes = question.values.map((value) =>
		Math.abs(Math.log10(parseFloat(value.value.split(' ')[0])))
	);
	return (
		value_sizes.reduce((acc, v) => acc + v, 0) *
		Math.max(Math.log10(Math.abs(Math.log10(question.answer))), 1)
	);
}

const DIFFICULTY_SKEW = 0.4; // Closer to 1 => likely to pick more difficult hints
const DIRECTION_SKEW = 0.3; // Chance to show a directional hint instead of a question hint

type HintOptions = {
	difficulty_skew?: number;
	direction_skew?: number;
	num?: number;
	previous_guess_magnitude?: number;
};

export async function random_hint(
	guess_magnitude: number,
	answer_magnitude: number,
	options: HintOptions = {}
): Promise<Hint> {
	const rng = await seeded_prng('hint', options.num ?? 0);
	const int_answer = Math.floor(answer_magnitude);
	const int_guess = Math.floor(guess_magnitude);
	if (int_guess === int_answer) {
		return {
			type: 'correct',
			value: true
		};
	}
	const delta = Math.abs(answer_magnitude - guess_magnitude);
	let closer = 0;
	if (options.previous_guess_magnitude !== undefined) {
		const prev_delta = Math.abs(int_answer - Math.floor(options.previous_guess_magnitude));
		closer = prev_delta - Math.abs(int_answer - int_guess);
	}

	if (closer && rng.float() < 0.5) {
		return {
			type: 'message',
			value: closer > 0 ? 'Warmer 🔥' : 'Colder 🥶'
		};
	}
	const value = guess_magnitude > answer_magnitude ? '⬇️' : '⬆️';
	return {
		type: 'message',
		value
	};
}

const activeQuestion = writable<Question>();
