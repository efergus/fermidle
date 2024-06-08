export type ScientificResult = {
	magnitude: number;
	digit: number;
	base: string;
};

export function scientific(value: number, precision = 1): ScientificResult {
	const magnitude = Math.floor(Math.log10(value));
	const base = value / 10 ** magnitude;
	const digit = Math.round(base);
	return {
		magnitude,
		digit,
		base: base.toFixed(precision - 1)
	};
}
