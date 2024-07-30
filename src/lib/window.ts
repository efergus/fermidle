export function onBrowser(fn?: () => void) {
	if (typeof window === 'undefined') {
		return false;
	}
	if (fn) {
		return fn();
	}
	return true;
}
