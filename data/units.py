

from dataclasses import dataclass, field, asdict

@dataclass
class Conversion:
    to: str
    ratio: float
    offset: float = 0

@dataclass
class Quantity:
    unit: str
    magnitude: int
    power: int