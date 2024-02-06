import { createEventDispatcher, type DispatchOptions } from 'svelte';

type DispatcherFn = ((arg: any) => any) | (() => void);

type Param<T extends (arg: any) => any> = Parameters<T>[0];

export type Dispatchers<T extends Record<string, DispatcherFn>> = {
	[key in keyof T]: Param<T[key]> extends undefined
		? () => void
		: (arg: Param<T[key]>) => ReturnType<T[key]>;
};

export function dispatchers<T extends Record<string, DispatcherFn>>(functions: T): Dispatchers<T> {
	const dispatcher = createEventDispatcher();
	return Object.fromEntries(
		Object.keys(functions).map((key) => {
			const k = key as keyof T;
			return [
				key,
				(arg: Parameters<T[typeof k]>[0], options?: DispatchOptions) => {
					dispatcher(key, functions[k](arg), options);
				}
			];
		})
	) as Dispatchers<T>;
}

export function ident<T = undefined>(x: T): T {
	return x;
}
