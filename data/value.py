from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Callable
from data import default, now

from units import Units, Quantity


@dataclass
class Value:
    value: Quantity
    name: str = ""  # ie max depth of the Pacific Ocean, population of the US, etc
    measurement: str = ""  # ie length, volume, density
    thing: str = ""  # ie Eiffel tower, Pacific ocean
    specifier: str = ""  # ie Max depth, population
    note: str = ""
    original: str = ""
    quality: float = 0.0
    generated: str = default(now)
    image: str = ""

    def serialize(self):
        return {
            "value": self.value.serialize(),
            "name": self.name,
            "measurement": self.measurement,
            "thing": self.thing,
            "specifier": self.specifier,
            "note": self.note,
            "quality": self.quality,
            "generated": self.generated,
            "image": self.image,
        }

    @staticmethod
    def deserialize(data: Dict):
        value = data.pop("value", "")
        if not value:
            raise ValueError(f"No value in {data}")
        return Value(**data, value=Quantity.deserialize(value))

    def key(self):
        return (self.thing, self.measurement, self.specifier)

    def to_string(self, thing_key: str = "thing"):
        data = {thing_key: self.thing, "measurement": self.measurement}
        if self.specifier:
            data["name"] = self.specifier
        if self.value:
            data["value"] = self.value.to_string(2)
        return "\n".join(f"{key}: {value}" for key, value in data.items() if value)

    def to_messages(self, include_name=True):
        messages = [{"role": "user", "content": self.to_string()}]
        if include_name and self.name:
            messages.append({"role": "assistant", "content": self.name})
        return messages


@dataclass
class Thing:
    name: str  # ie Eiffel tower, Pacific ocean
    tags: List[str]  # ie sphere, building
    values: Dict[str, List[Value]] = default(dict)
    broken: Dict[str, List[str]] = default(dict)

    def canonical(self, measurement, single=False):
        """Return the canonical value of a given measurement, if it exists"""
        values = self.values.get(measurement, [])
        if single and len(values) == 1:
            return values[0]
        for value in values:
            if not value.specifier:
                return value
        return None

    def alter(self, fns: List[Callable[[Thing], List[Value] | None]]):
        for fn in fns:
            extra = fn(self) or []
            for value in extra:
                value.thing = self.name
                if value.measurement in self.values:
                    self.values[value.measurement].append(value)
                else:
                    self.values[value.measurement] = [value]

    def serialize(self):
        return {
            "name": self.name,
            "tags": self.tags,
            "values": {
                key: [value.serialize() for value in values]
                for key, values in self.values.items()
            },
        }
