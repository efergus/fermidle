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

export function random_question(): Question {
	const question = data[Math.floor(Math.random() * data.length)];
	return {
		question: question.question,
		answer: question.answer,
		values: question.values.map(({ value, name, image }) => ({ value, name, image }))
	};
}

export type Hint = {
	type: 'closer';
	value: Question;
};

export function random_hint(guess_magnitude: number, answer_magnitude: number): Hint {
	const delta = Math.abs(answer_magnitude - guess_magnitude);
	const valid_questions = data.filter((queston) => {
		const question_magnitude = Math.log10(queston.answer);
		return Math.abs(question_magnitude - delta) < 1.5;
	});
	return {
		type: 'closer',
		value: valid_questions[0]
	};
}
