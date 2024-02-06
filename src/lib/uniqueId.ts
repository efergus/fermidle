let id = 1;

export function uniqueId(prefix = '') {
	return (prefix.toString() || 'id') + id;
}
