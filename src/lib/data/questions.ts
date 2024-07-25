import random from 'random';
import data from './questions.json';
import { addDays, formatISO, isValid, parseISO } from 'date-fns';

export type Value = {
	value: string;
	name: string;
	image?: string;
};

export type Question = {
	question: string;
	answer: number;
	values: Value[];
};

function globalSeed() {
	return formatISO(new Date(), { representation: 'date' });
}
const GLOBAL_SEED = globalSeed();

function seeded_prng(...seed: (string | number)[]) {
	let globalSeed = GLOBAL_SEED;
	if (typeof window !== 'undefined') {
		const params = new URLSearchParams(window.location.search);
		let seed = params.get('s');
		if (!seed) {
			params.set('s', GLOBAL_SEED);
			window.location.search = params.toString();
		}
		let date = parseISO(seed || '');
		if (!seed || !isValid(date) || date > new Date()) {
			seed = GLOBAL_SEED;
			params.set('s', GLOBAL_SEED);
			window.location.search = params.toString();
		}
		globalSeed = seed;
	}

	const seedString = seed.map((x) => x.toString()).join('|') ?? '';
	return random.clone(globalSeed + seedString);
}

export function random_question(num: number): Question {
	const rng = seeded_prng('question', num);
	const question = rng.choice(data)!;
	return {
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

export function random_hint(
	guess_magnitude: number,
	answer_magnitude: number,
	options: HintOptions = {}
): Hint {
	const rng = seeded_prng('hint', options.num ?? 0);
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
