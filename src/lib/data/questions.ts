import jsonData from './values.json';

type Quantity = {
	value: number;
	units: string;
};

type Value = {
	value: Quantity;
	kind: string;
	name?: string;
};

type Thing = {
	values: Record<string, Value[]>;
	name: string;
};

export type Question = {
	kind: string;
	question: string;
	answer: number;
};

const data = jsonData as Thing[];

function scalar(value: Value) {
	return value.value.value;
}

function random_from_range(min: number, max: number) {
	return Math.floor(Math.random() * (max - min + 1) + min);
}

function random_item(kind: string) {
	const options = data
		.filter((thing) => 'length' in thing.values)
		.flatMap((thing) =>
			thing.values.length.map((value) => ({
				value,
				thing
			}))
		);
	if (options.length <= 1) {
		console.log(data[0]);
		return;
	}
	return options[random_from_range(0, options.length)];
}

function random_length_question(): Question {
	let smaller = random_item('length');
	let larger = random_item('length');

	if (!smaller || !larger) {
		throw new Error('Could not generate question');
	}

	if (scalar(smaller.value) > scalar(larger.value)) {
		const tmp = larger;
		larger = smaller;
		smaller = tmp;
	}

	const name1 = `${smaller.value.name || smaller.value.kind} of ${smaller.thing.name}`;
	const name2 = `${larger.value.name || larger.value.kind} of ${larger.thing.name}`;

	return {
		kind: 'length',
		question: `How many ${name1} long is ${name2}`,
		answer: scalar(larger.value) / scalar(smaller.value)
	};
}

export function random_question() {
	return random_length_question();
}

export default data;
