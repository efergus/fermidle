
from __future__ import annotations
from typing import Dict, List
from dataclasses import InitVar, dataclass, field, asdict
import re
from math import prod, log10, floor
from copy import copy, deepcopy
from collections import defaultdict

number_regex = r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?"

prefixes = {
    "T": 12,
    "G": 9,
    "M": 6,
    "k": 3,
    "d": -1,
    "c": -2,
    "m": -3,
    "u": -6,
    "n": -9,
    "p": -12,
}

prefixes_by_magnitude = {
    val: key for key, val in prefixes.items()
}

@dataclass
class Unit:
    name: str
    power: int = 1
    magnitude: int = 0

    @staticmethod
    def _parse(string: str, known):
        m = re.match(r'^(\D+)(-?\d*)$', string)
        if not m:
            raise ValueError(f"Could not parse unit '{string}'")
        name, power = m.group(1, 2)
        power = int(power) if power else 1
        magnitude = 0
        while name not in known:
            if name[-1] == 's' and name[:-1] in known:
                name = name[:-1]
                continue
            if name[0] in prefixes and name[1:] in known:
                magnitude = prefixes[name[0]]
                name = name[1:]
                continue
            break
        return Unit(name, power, magnitude)
    
    def __str__(self):
        return f"{prefixes_by_magnitude.get(self.magnitude, '')}{self.name}{self.power}"
    
    def __pow__(self, power):
        return Unit(self.name, self.power * power, self.magnitude)
    
    def powerless(self):
        return Unit(self.name, 1, self.magnitude)
    
    def magnitudeless(self):
        return Unit(self.name, self.power)

def scientific(num: float, precision: int=None):
    magnitude = floor(log10(num))
    if precision != None:
        num *= 10**(precision - magnitude - 1)
        num = round(num)/10**(precision - 1)
        return f"{num}e{magnitude}"
    return f"{num / 10**magnitude}e{magnitude}"

def combine_units(preferred_units):
    ratios = [ratio for ratio, _, _ in preferred_units]
    magnitudes = [magnitude for _, magnitude, _ in preferred_units]
    units = [unit for _, _, units in preferred_units for unit in units]
    return (prod(ratios), sum(magnitudes), units)

@dataclass
class Units:
    units: List[Unit]

    @staticmethod
    def parse(string: str, known: ConversionMap) -> List[Unit]:
        string = string.replace("^", "")
        positive, _, negative = string.partition("/")
        def helper(string: str):
            unit_strings = re.findall(r'([^\d/*]+\d*)', string)
            return [Unit._parse(s, known) for s in unit_strings]
        positive = helper(positive)
        negative = helper(negative)
        for unit in negative:
            unit.power *= -1
        return Units(positive + negative)
    
    def mul(self, units: Units):
        units = Units(self.units + units.units)
        units.simplify()
        return units
    
    def simplify(self):
        units = defaultdict(int)
        for unit in self.units:
            units[(unit.name, unit.magnitude)] += unit.power
        self.units = [Unit(name, power, magnitude) for (name, magnitude), power in units.items() if power != 0]

    def sort(self):
        self.units.sort(key=lambda x: (x.power, x.name, x.magnitude))

    def single(self):
        return (len(self.units) == 1 and self.units[0].power == 1 and self.units[0].name) or None

    def __len__(self):
        return len(self.units)

    def __mul__(self, other):
        return self.mul(other)
    
    def __pow__(self, power):
        return Units([unit ** power for unit in self.units])

    def __str__(self):
        units = sorted(self.units, key=lambda x: -x.power)
        neg_index = None
        for i, unit in enumerate(units):
            if unit.power < 0:
                neg_index = i
                break
        positive = units
        negative = []
        if neg_index != None:
            positive = units[:neg_index]
            negative = deepcopy(units[neg_index:])
            for unit in negative:
                unit.power *= -1
        positive = [str(unit) for unit in positive]
        negative = [str(unit) for unit in negative]
        string = "".join(positive)
        if negative:
            string += "/" + "".join(negative)
        return string
    
    def __iter__(self):
        return self.units.__iter__()
    
@dataclass
class Conversion:
    from_name: str
    to_name: str
    offset: float
    ratio: float = 1

    def convert(self, quantity: Quantity):
        single = quantity.units.single()
        if not single or single != self.from_name:
            return None
        return Quantity((quantity.value + self.offset) * self.ratio, Units([Unit(self.to_name)]))

@dataclass
class Quantity:
    value: float
    units: Units = field(default_factory=lambda: Units([]))
    uncertainty: float = 0

    @staticmethod
    def from_str(string: str):
        rest = r"\s*(.*)"
        match = re.match(f"({number_regex})?{rest}", string)
        if not match:
            print(f"Could not parse quantity '{string}'")
        number, units = match.group(1, 2)
        units = Units.parse(units, preferred)
        return Quantity(float(number or '1'), units)

    def standardized(self, map: ConversionMap, limit=100):
        res = deepcopy(self)
        for i in range(0, limit):
            single = res.units.single()
            if single and single in map:
                conversion = map[single]
                if type(conversion) == Conversion:
                    res = conversion.convert(res)
                    continue
            simplifier = Quantity(1)
            for unit in res.units:
                name = unit.name
                if unit.magnitude:
                    simplifier *= Quantity(10**(unit.magnitude*unit.power), Units([unit.magnitudeless(), unit**-1]))
                elif name in map and map[name] and type(map[name]) == Quantity:
                    simplifier *= map[name]**unit.power
            if len(simplifier.units):
                res *= simplifier
            else:
                break
        if i == 100:
            raise ValueError("AAAH")
        return res
    
    def close(self, other, eps=1e-5):
        if self.units != other.units:
            return False
        if self.value * other.value < 0:
            return False
        a = max(self.value, other.value)
        b = min(self.value, other.value)
        if not b:
            return False
        return a/b < eps
    
    def mul(self, other: Quantity):
        value = self.value
        units = self.units
        value = value * other.value
        units = units * other.units
        return Quantity(value, units)

    def __mul__(self, other):
        t = type(other)
        if t == Quantity:
            return self.mul(other)
        if t == Unit:
            return self.mul(Quantity(1, Units([other])))
        if t == float:
            return Quantity(self.value * other, self.units)
    
    def __rmul__(self, other):
        return self.__mul__(other)
        
    def __truediv__(self, other):
        return self * other ** -1
        
    def __pow__(self, power):
        return Quantity(self.value ** power, self.units ** power)
        
    def __str__(self):
        return f"{scientific(self.value, 3)} {self.units}"
    
    def serialize(self):
        return {
            'value': self.value,
            'units': str(self.units)
        }
        
def canonicalize_quantity_map(unit, quantity) -> Quantity:
    if not quantity:
        return
    if type(quantity) == str:
        return Quantity.from_str(quantity) * Unit(unit) ** -1
    if type(quantity) == Conversion:
        return quantity
    return quantity * Unit(unit) ** -1
    

ConversionMap = Dict[str, Quantity | Conversion | None]

preferred = {
    "g": None,
    "m": None,
    "s": None,
    "bit": None,
    "pH": None,
    "J": None,
    # imperial
    "in": "2.54e-2 m",
    "ft": "0.3048 m",
    "yd": "0.9144 m",
    "yard": "yd",
    "oz": "28.3495 g",
    "lb": "453.5924 g",
    "mph": "mile/h",
    "mile": "1.60934 km",
    "psi": "lb/in^2",
    "gal": "3.78541 L",
    # standard, unusual units
    "picometer": "pm",
    "kph": Quantity.from_str("km/h"),
    "ly": "9.461e15 m",

    "h": "hour",
    "hour": "3600 s",
    "day": "86400 s",
    "yr": "year",
    "year": Quantity(365*24*60*60, Units([Unit("s")])),

    "db": "dB",
    "C": Conversion("C", "K", 273.15),
    "F": Conversion("F", "C", -32, 5/9),
    "W": "J/s",
    "Wh": "W*h",
    "L": "1e-3 m3",
    "Hz": "/s"
}

preferred = {unit: canonicalize_quantity_map(unit, quantity) for unit, quantity in preferred.items()}

def test(value1: str, value2: str = "1"):
    quant1 = Quantity.from_str(value1)
    quant2 = Quantity.from_str(value2)
    quant3 = quant1 * quant2
    print("Quantity:", quant3)
    standardized = quant3.standardized(preferred)
    print("Standardized:", standardized)

if __name__ == "__main__":
    test("1 km^2/s", "0.5 ly/yr")
    test("1 ft^2/h", "2")
    test("30 F")
    test("Wh")
    test("2 gal")