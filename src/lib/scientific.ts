export type ScientificResult = {
	magnitude: number;
	digit: number;
	base: string;
};

export function scientific(value: number, precision = 1): ScientificResult {
	let magnitude = Math.floor(Math.log10(value));
	let base = value / 10 ** magnitude;
	let digit = Math.round(base);
	// Probably a better way to do this, but this is an easy fix for if it rounds up to 10
	if (digit >= 10) {
		magnitude += 1;
		base = value / 10 ** magnitude;
		digit = Math.round(digit / 10);
	}
	return {
		magnitude,
		digit,
		base: base.toFixed(precision - 1)
	};
}
