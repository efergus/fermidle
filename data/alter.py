import math
from clean import Thing, Value

def sphere_volume_surface_area(thing: Thing):
    if 'length' not in thing.values:
        print("No length", thing.values)
        return []
    radius = None
    if len(thing.values['length']) == 1:
        radius = thing.values['length'][0].value / 2
    else:
        for value in thing.values['length']:
            # print("length", value)
            if not value.name or value.name.lower() in ('d', 'diameter'):
                radius = value.value / 2
                break
            if value.name.lower() in ('r', 'radius'):
                radius = value.value
                break
    if radius is None:
        return []
    extend = []
    if 'volume' not in thing.values:
        extend.append(Value(4/3 * math.pi * radius ** 3, kind='volume', note='auto'))
    if 'surface area' not in thing.values:
        extend.append(Value(4 * math.pi * radius ** 2, kind='surface area', note='auto'))
    return extend

def density(thing: Thing):
    if 'density' in thing.values:
        return []
    mass = thing.canonical('mass')
    volume = thing.canonical('volume')
    if not volume or not mass:
        return []
    return [Value(mass.value/volume.value, kind='density', name='avg density', note='auto')]

def minmax(thing: Thing):
    for values in thing.values.values():
        for value in values:
            if value.name in ('min', 'max'):
                value.name = f"{value.name} {value.kind}"

alter_map = {
    "sphere": [sphere_volume_surface_area],
    "": [density, minmax]
}