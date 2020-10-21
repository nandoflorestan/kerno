/** @prettier */
"use strict";

export function jsonrightToEntities(jsonright, cls, useNew = false) {
	// Usage: const entities = jsonrightToEntities(serverData, MyClass, true);
	if (!jsonright.length) return [];
	const entities = [];
	const iterators = jsonright.map((field) => field.values());
	for (const i of iterators) {
		i.key = i.next().value;
	}
	let iteration = {value: null, done: true};
	do {
		const pojo = {};
		for (const i of iterators) {
			iteration = i.next();
			pojo[i.key] = iteration.value;
		}
		if (!iteration.done) {
			// $FlowFixMe
			entities.push(useNew ? new cls(pojo) : cls.new(pojo));
		}
	} while (!iteration.done);
	return entities;
}
