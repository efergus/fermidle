import { cubicInOut, cubicOut } from 'svelte/easing';
import type { EasingFunction } from 'svelte/transition';

export type CloneParams = {
	node: Element;
	delay?: number;
	duration?: number | ((len: number) => number);
	opacity?: number;
	easing?: EasingFunction;
};

export function clone(node: Element, params: CloneParams) {
	const style = getComputedStyle(node);
	const {
		node: from_node,
		delay = 0,
		duration = (d: number) => Math.sqrt(d) * 30,
		opacity = 0,
		easing = cubicInOut
	} = params;
	const from = from_node.getBoundingClientRect();
	const to = node.getBoundingClientRect();
	const dx = from.left - to.left;
	const dy = from.top - to.top;
	const dw = from.width / to.width;
	const dh = from.height / to.height;
	const d = Math.sqrt(dx * dx + dy * dy);
	const transform = style.transform === 'none' ? '' : style.transform;
	const to_opacity = +style.opacity;
	return {
		delay,
		duration: typeof duration === 'function' ? duration(d) : duration,
		easing,
		css: (t: number, u: number) => `
			opacity: ${u * opacity + t * to_opacity};
			transform-origin: top left;
			transform: ${transform} translate(${u * dx}px,${u * dy}px) scale(${t + u * dw}, ${t + u * dh});
		`
	};
}
