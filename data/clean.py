# import csv
from __future__ import annotations
import pandas
import re
from pandas import DataFrame, isna
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from pprint import pprint
import numpy as np
from typing import Dict, List, Callable
import json
import click
from data import Value, Thing

import units
import alter

number_regex = r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?"
range_regex = f"{number_regex}(?:-{number_regex})*"
unit_regex = r"[^\s]*"
note_regex = r"\(.*\)"

value_regex = re.compile(f"(?:(.*):)?\s*({range_regex})\s*({unit_regex})\s*({note_regex})?$")




def drop_empty(df: DataFrame, log=False):
    df = df.dropna(how="all")
    return df.dropna(how="all", axis=1)


def parse_number(s: str):
    try:
        return float(s), 0
    except:
        return None, 0


def get_things(df: DataFrame) -> List[Thing]:
    things = []
    for thing_name in df.index:
        row = df.loc[thing_name].dropna()
        cols = row.index
        thing = Thing(
            thing_name, tags=[tag.lower().strip() for tag in row.get("tags", "").split(", ") if tag]
        )
        values = defaultdict(list)
        broken = defaultdict(list)
        for kind in cols:
            if kind in ("tags", "thing"):
                continue
            vals = row[kind]
            for val in vals.split(","):
                val = val.strip()
                m = value_regex.match(val)
                if not m:
                    broken[kind].append(val)
                    continue
                (name, number, unit, note) = m.group(1, 2, 3, 4)
                num, uncertainty = parse_number(number)
                if not num:
                    broken[kind].append(val)
                    continue
                values[kind].append(Value(
                    units.Quantity.from_str(f"{num} {unit}").standardized(units.preferred), (name or "").lower(), kind, thing_name, original=val
                ))
        thing.values = dict(values)
        thing.broken = dict(broken)
        things.append(thing)
    return things

def clean(file):
    df = pandas.read_csv(file, sep="\t")
    df = df.rename(columns=lambda x: x.strip().lower())
    df = df[
        [
            "thing",
            "volume",
            "surface area",
            "length",
            "mass",
            "time/age",
            "count",
            "speed",
            "temperature",
            "density",
            "frequency",
            "energy",
            "power",
            "loudness",
            "charge",
            "other",
            "tags",
        ]
    ].copy()
    df = drop_empty(df)

    df = df.set_index("thing", drop=True)
    things = get_things(df)
    for thing in things:
        thing.alter(alter.alter_map.get('', []))
        for tag in thing.tags:
            thing.alter(alter.alter_map.get(tag, []))

    values: List[Value] = [value for thing in things for values in thing.values.values() for value in values]
    return values

@click.command()
@click.argument("input", type=click.File("r"), default="Fermidle - Values.tsv")
@click.argument("output", type=click.File("w"), default="values.json")
def main(input, output):
    df = pandas.read_csv(input, sep="\t")
    df = df.rename(columns=lambda x: x.strip().lower())
    df = df[
        [
            "thing",
            "volume",
            "surface area",
            "length",
            "mass",
            "time/age",
            "count",
            "speed",
            "temperature",
            "density",
            "frequency",
            "energy",
            "power",
            "loudness",
            "charge",
            "other",
            "tags",
        ]
    ].copy()
    df = drop_empty(df)
    column_counts = df.apply(lambda col: col.notna().values.sum())
    print(DataFrame([column_counts]).to_string(index=False))

    df = df.set_index("thing", drop=True)
    things = get_things(df)
    for thing in things:
        thing.alter(alter.alter_map.get('', []))
        for tag in thing.tags:
            thing.alter(alter.alter_map.get(tag, []))

    values: List[Value] = [value for thing in things for values in thing.values.values() for value in values]

    broken = [value.name for value in values if value.value is None]
    values_by_kind = defaultdict(list)
    for value in values:
        if value.value is None:
            continue
        values_by_kind[value.kind].append(value)

    # units_by_kind = defaultdict(set)
    # for kind, values in values_by_kind.items():
    #     units_by_kind[kind] = set(value.unit for value in values)
    # units_by_kind = dict(units_by_kind)
    # print("Broken:", broken)
    # pprint(units_by_kind)
    # for x in units_by_kind.values():
    #     for unit in x:
    #         units.parse(unit)
    all_units = defaultdict(int)
    for value in values:
        # print(f"{value.name or value.kind} of {value.thing}:")
        # print(value.value)
        # if value.kind == 'density':
        #     print(f"{value.name or value.kind} of {value.thing}:")
        #     print(value.value)
        all_units[str(value.value.units)] += 1
    
    units_by_frequency = [f"{x[0]}\t{x[1]}" for x in sorted(all_units.items(), reverse=True, key=lambda x: x[1])]
    print("\n".join(units_by_frequency))

    things_serial = [thing.serialize() for thing in things]
    json.dump(things_serial, output, indent=2)


if __name__ == "__main__":
    main()
