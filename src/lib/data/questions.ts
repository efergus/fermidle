import data from './questions.json';

type Question = {
	question: string;
	answer: number;
};

export function random_question(): Question {
	const question = data[Math.floor(Math.random() * data.length)];
	return {
		question: question.question,
		answer: question.answer
	};
}
