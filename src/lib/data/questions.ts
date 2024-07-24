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
};

export function random_hint(
	guess_magnitude: number,
	answer_magnitude: number,
	options: HintOptions = {}
): Hint {
	const rng = seeded_prng('hint', options.num ?? 0);
	const { difficulty_skew = DIFFICULTY_SKEW, direction_skew = DIRECTION_SKEW } = options;
	if (Math.floor(guess_magnitude) === Math.floor(answer_magnitude)) {
		return {
			type: 'correct',
			value: true
		};
	}
	const delta = Math.abs(answer_magnitude - guess_magnitude);
	const valid_questions = data.filter((queston) => {
		const question_magnitude = Math.log10(queston.answer);
		return Math.abs(question_magnitude - delta) < Math.max(0.6, Math.min(delta / 4, 1.5));
	});
	valid_questions.sort((a, b) => question_difficulty(a) - question_difficulty(b));
	const easiest_hint = valid_questions[0];
	const easiest_hint_difficulty = question_difficulty(easiest_hint);
	console.log({ easiest_hint_difficulty, easiest_hint });
	if (
		valid_questions.length > 0 &&
		rng.float() >= direction_skew &&
		easiest_hint_difficulty < rng.float(2, 10 * (1 + difficulty_skew))
	) {
		for (let i = 0; ; i = (i + 1) % valid_questions.length) {
			if (rng.float() > difficulty_skew) {
				return {
					type: 'delta',
					value: valid_questions[i]
				};
			}
		}
	}
	const value = guess_magnitude > answer_magnitude ? '⬇️' : '⬆️';
	return {
		type: 'message',
		value
	};
}
