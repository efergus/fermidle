
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Callable

from units import Units

def default(fn):
    return field(default_factory=fn)

@dataclass
class Value:
    value: Units.Quantity
    name: str = ""  # ie Max height, population, etc
    kind: str = ""  # ie legth, volume, density
    thing: str = ""  # ie Eiffel tower, Pacific ocean
    note: str = ""
    original: str = ""

    def serialize(self):
        return {
            'value': self.value.serialize(),
            'name': self.name,
            'kind': self.kind,
            'thing': self.thing,
            'note': self.note
        }

@dataclass
class Thing:
    name: str  # ie Eiffel tower, Pacific ocean
    tags: List[str]  # ie sphere, building
    values: Dict[str, List[Value]] = default(dict)
    broken: Dict[str, List[str]] = default(dict)

    def canonical(self, kind, single=False):
        """Return the canonical value of a given kind, if it exists"""
        values = self.values.get(kind, [])
        if single and len(values) == 1:
            return values[0]
        for value in values:
            if not value.name:
                return value
        return None

    def alter(self, fns: List[Callable[[Thing], List[Value] | None]]):
        for fn in fns:
            extra = fn(self) or []
            for value in extra:
                value.thing = self.name
                if value.kind in self.values:
                    self.values[value.kind].append(value)
                else:
                    self.values[value.kind] = [value]

    def serialize(self):
        return {
            'name': self.name,
            'tags': self.tags,
            'values': {
                key: [value.serialize() for value in values] for key, values in self.values.items()
            },
        }