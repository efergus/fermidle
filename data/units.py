
from __future__ import annotations
from typing import Dict, List
from dataclasses import InitVar, dataclass, field, asdict
import re
from math import prod, log10, floor
from copy import copy, deepcopy

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

@dataclass
class Conversion:
    to_unit: InitVar[str | Unit | List[Unit] | Units]
    to: Unit = field(init=False)
    ratio: float = 1
    offset: float = 0

    def __post_init__(self, to_unit):
        t = type(to_unit)
        if t == str:
            self.to = Units([Unit(to_unit)])
        elif t == Unit:
            self.to = Units([to_unit])
        elif t == list:
            self.to = Units(to_unit)
        else:
            self.to = to_unit
    
    def to(self, conversion: Conversion):
        units = deepcopy(conversion.to)
        ratio = self.ratio * conversion.ratio
        # TODO: check
        offset = self.offset*self.ratio + conversion.offset
        return Conversion(units, ratio, offset)
    
    def standardized(self, map: ConversionMap):
        units = [unit.standardized(map) for unit in self.to]


ConversionMap = Dict[str, Conversion | None]

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
        power = int(power) if power else 0
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
        return f"{self.name}{self.power}"
    
    # def preferred(self, known: Dict[str, Conversion]):
    #     if self.name not in known:
    #         return self
    #     conversion = known[self.name]
    #     # ratio = 1
    #     # power = 1
    #     # magnitude = 0
    #     # for unit in conversion.to:
    #     return conversion.ratio, conversion.to

# def scientific(num: float, precision: int=None):
#     magnitude = floor(log10(num))
    

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
            unit_strings = re.findall(r'([^\d/]+\d*)', string)
            return [Unit._parse(s, known) for s in unit_strings]
        positive = helper(positive)
        negative = helper(negative)
        for unit in negative:
            unit.power *= -1
        return Units(positive + negative)
    
    @staticmethod
    def _standardized(unit: Units | Unit | List[Unit], map: ConversionMap):
        if type(unit) == Units:
            unit = unit.units
        if type(unit) == list:
            return combine_units([Units._standardized(copy(unit), known) for unit in unit])
        if unit.name not in map or map[unit.name] == None:
            return (1, unit.magnitude * unit.power, Units([Unit(unit.name, unit.power)]))
        conversion = copy(map[unit.name])
        # some combine operation
        conversion2 = Units._standardized(conversion.to, known)
        for unit2 in conversion2:
            unit2.power *= unit.power
        conversion.to = conversion2
        conversion.magnitude = (conversion2.magnitude + unit.magnitude) * unit.power
        conversion.ratio = (conversion2.ratio * conversion.ratio) ** unit.power
        return conversion
    
    def standardized(self, known):
        return Units._standardized(self, known)

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
class Quantity:
    value: float
    units: Units
    uncertainty: float = 0

    def standardized(self, map: ConversionMap):
        conversion = self.units.standardized(map)
        value = (self.value + conversion.offset) * conversion.ratio * 10**conversion.magnitude
        return Quantity(value, conversion.to, self.uncertainty*conversion.ratio)

    @staticmethod
    def from_str(string: str):
        number, _, units = string.partition(' ')
        units = Units.parse(units, known)
        return Quantity(float(number), units)

def canonicalize_conversion(conversion) -> Conversion:
    if type(conversion) == str:
        return Conversion(conversion)
    if type(conversion) == Unit:
        return Conversion([conversion])
    return conversion

known = {
    "g": None,
    "m": None,
    "s": None,
    "bit": None,
    "pH": None,
    "Hz": None,
    "J": None,
    # Technically the unit is Bells
    "dB": None,
    # imperial
    "in": Conversion("m", 2.54),
    "ft": Conversion("m", 0.3048),
    "yard": Conversion("m", 0.9144),
    "oz": Conversion("g", 28.3495),
    "lb": Conversion("g", 453.5924),
    "mph": Conversion("kph", 1.60934),
    "mile": Conversion("km", 1.60934),
    # standard, unusual units
    "ton": Unit("g", magnitude=6),
    "picometer": "pm",
    "kph": Conversion([Unit("m"), Unit("s", -1)], 5/18),
    "eV": Conversion("J", 1.60218e-19),
    "C": Conversion("K", 1, 273.15),

    "h": "hour",
    "hour": Conversion("s", 3600),
    "year": Conversion("s", 365*24*60*60),
}

known = {unit: canonicalize_conversion(conversion) for unit, conversion in known.items()}

def test(units: str):
    print("Convert:", units)
    value = Quantity.from_str(units)
    # print(value)
    value.standardized(known)

if __name__ == "__main__":
    test("1 km^2/h")
    test("1 ft^2/h")
    test("1 kft^2/h")
    test("1 s/h")
    test("1 mph/s")
    test("1 miles")