import math
from clean import Thing, Value
from units import Quantity


def sphere_volume_surface_area(thing: Thing):
    """
    If a sphere has a radius, add its surface area, volume, and circumference
    """
    if "length" not in thing.values:
        print("No length", thing.values)
        return []
    radius = None
    # find the sphere's radius
    diameter = thing.canonical("length", True)
    if diameter:
        diameter.specifier = "diameter"
        radius = diameter.value / 2
    else:
        for value in thing.values["length"]:
            # if it has a diameter, r = d / 2
            if not value.specifier or value.specifier.lower() in ("d", "diameter"):
                value.specifier = "diameter"
                radius = value.value / 2
                break
            # if it has a radius, use that
            if value.specifier.lower() in ("r", "radius"):
                value.specifier = "radius"
                radius = value.value
                break
    if radius is None:
        return []
    extend = []
    # if it does not have a volume, add it
    if "volume" not in thing.values:
        extend.append(
            Value(4 / 3 * math.pi * radius**3, measurement="volume", note="auto")
        )
    # if it does not have a surface area, add it
    if "surface area" not in thing.values:
        extend.append(
            Value(4 * math.pi * radius**2, measurement="surface area", note="auto")
        )
    # if it does not have a circumference, add it
    if "circumference" not in thing.values:
        extend.append(
            Value(
                2 * math.pi * radius,
                measurement="length",
                specifier="circumference",
                note="auto",
            )
        )
    return extend


speed_of_light = Quantity.from_str("3.0e8 m/s")


def em_radiation_values(thing: Thing):
    """
    Calculate period/frequency/wavelength given frequency/wavelength for em radiation
    """
    extend = []
    length = thing.canonical("length")
    if length and not length.specifier:
        length.specifier = "wavelength"
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
            specifier="wavelength",
            note="auto",
        )
        extend.append(length)
    if not frequency:
        return
    period = thing.canonical("time/age")
    true_period = Value(
        frequency.value**-1, measurement="time/age", specifier="period", note="auto"
    )
    if not period or (
        period.specifier != "period" and not period.value.close(true_period.value, 1e-1)
    ):
        extend.append(true_period)
    return extend


def country_population(thing: Thing):
    """
    Specify that the default count for a country is population
    """
    pop = thing.canonical("count")
    if not pop:
        return
    pop.specifier = "population"
    pop.note = pop.note or "auto"


def density(thing: Thing):
    """
    Calculate density based on mass and volume
    """
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
            specifier="avg density",
            note="auto",
        )
    ]


def minmax(thing: Thing):
    """
    Convert "min" to "min length" eg
    """
    for values in thing.values.values():
        for value in values:
            if value.specifier in ("min", "max"):
                value.specifier = f"{value.specifier} {value.measurement}"


# A map of tags to apply these alterations to
alter_map = {
    "sphere": [sphere_volume_surface_area],
    "radiation": [em_radiation_values],
    "country": [country_population],
    "": [density, minmax],
}
