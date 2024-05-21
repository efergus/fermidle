import random, { RNG, Random } from 'random';
import seedrandom from 'seedrandom';
import data from './questions.json';

type Value = {
	value: string;
	name: string;
	image?: string;
};

export type Question = {
	question: string;
	answer: number;
	values: Value[];
};

export function seed(value?: string) {
	if (!value) {
		value = new Date().toISOString().split('T')[0];
	}
	random.use(seedrandom(value) as unknown as RNG);
}

export function random_question(): Question {
	const question = random.choice(data)!;
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
			type: 'message';
			value: string;
	  };

export function random_hint(guess_magnitude: number, answer_magnitude: number): Hint {
	console.log({ guess_magnitude, answer_magnitude });
	if (Math.floor(guess_magnitude) === Math.floor(answer_magnitude)) {
		return {
			type: 'message',
			value: 'Correct!'
		};
	}
	const delta = Math.abs(answer_magnitude - guess_magnitude);
	const valid_questions = data.filter((queston) => {
		const question_magnitude = Math.log10(queston.answer);
		return Math.abs(question_magnitude - delta) < 1.5;
	});
	if (valid_questions.length > 0) {
		return {
			type: 'closer',
			value: random.choice(valid_questions)!
		};
	}
	const value = guess_magnitude > answer_magnitude ? '⬇️' : '⬆️';
	return {
		type: 'message',
		value
	};
}
