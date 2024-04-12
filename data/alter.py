import math
from clean import Thing, Value
from units import Quantity


def sphere_volume_surface_area(thing: Thing):
    if "length" not in thing.values:
        print("No length", thing.values)
        return []
    radius = None
    diameter = thing.canonical("length", True)
    if diameter:
        diameter.name = "diameter"
        radius = diameter.value / 2
    else:
        for value in thing.values["length"]:
            # print("length", value)
            if not value.name or value.name.lower() in ("d", "diameter"):
                value.name = "diameter"
                radius = value.value / 2
                break
            if value.name.lower() in ("r", "radius"):
                value.name = "radius"
                radius = value.value
                break
    if radius is None:
        return []
    extend = []
    if "volume" not in thing.values:
        extend.append(
            Value(4 / 3 * math.pi * radius**3, measurement="volume", note="auto")
        )
    if "surface area" not in thing.values:
        extend.append(
            Value(4 * math.pi * radius**2, measurement="surface area", note="auto")
        )
    if "circumference" not in thing.values:
        extend.append(
            Value(
                2 * math.pi * radius,
                measurement="length",
                name="circumference",
                note="auto",
            )
        )
    return extend


speed_of_light = Quantity.from_str("3.0e8 m/s")


def em_radiation_values(thing: Thing):
    extend = []
    length = thing.canonical("length")
    if length and not length.name:
        length.name = "wavelength"
    frequency = thing.canonical("frequency")
    if length and not frequency:
        frequency = Value(
            speed_of_light / length.value, measurement="frequency", note="auto"
        )
        extend.append(frequency)
    if frequency and not length:
        length = Value(
            frequency.value / speed_of_light,
            measurement="length",
            name="wavelength",
            note="auto",
        )
        extend.append(length)
    if not frequency:
        return
    period = thing.canonical("time/age")
    true_period = Value(
        frequency.value**-1, measurement="time/age", name="period", note="auto"
    )
    if not period or (
        period.name != "period" and not period.value.close(true_period.value, 1e-1)
    ):
        extend.append(true_period)
    return extend


def country_population(thing: Thing):
    pop = thing.canonical("count")
    if not pop:
        return
    pop.name = "population"
    pop.note = pop.note or "auto"


def density(thing: Thing):
    if "density" in thing.values:
        return []
    mass = thing.canonical("mass")
    volume = thing.canonical("volume")
    if not volume or not mass:
        return []
    return [
        Value(
            mass.value / volume.value,
            measurement="density",
            name="avg density",
            note="auto",
        )
    ]


def minmax(thing: Thing):
    for values in thing.values.values():
        for value in values:
            if value.name in ("min", "max"):
                value.name = f"{value.name} {value.measurement}"


alter_map = {
    "sphere": [sphere_volume_surface_area],
    "radiation": [em_radiation_values],
    "country": [country_population],
    "": [density, minmax],
}
