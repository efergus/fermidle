# import csv
import pandas
import re
from pandas import DataFrame, isna
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from pprint import pprint
import numpy as np
from typing import Dict, List
import json
import click

number_regex = r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?"
range_regex = f"{number_regex}(?:-{number_regex})?"
unit_regex = r"[^\s]*"

value_regex = re.compile(f"(?:(.*):)?\s*({range_regex})\s*({unit_regex})$")


def default(fn):
    return field(default_factory=fn)


@dataclass
class Value:
    name: str = ""  # ie Max height, population, etc
    value: float = None  # The value
    unit: str = ""  # ie g/cm^3
    kind: str = ""  # ie legth, volume, density
    thing: str = ""  # ie Eiffel tower, Pacific ocean
    uncertainty: float = 0.0  # +/- how much


@dataclass
class Thing:
    name: str  # ie Eiffel tower, Pacific ocean
    tags: List[str]  # ie sphere, building
    values: Dict[str, List[Value]] = default(dict)


def drop_empty(df: DataFrame, log=False):
    df = df.dropna(how="all")
    return df.dropna(how="all", axis=1)


def parse_number(s: str):
    try:
        return float(s), 0
    except:
        return None, 0


def get_things(df: DataFrame):
    things = []
    for row_name in df.index:
        row = df.loc[row_name].dropna()
        cols = row.index
        thing = Thing(
            row_name, tags=[tag.lower() for tag in row.get("tags", "").split(", ")]
        )
        values = defaultdict(list)
        for col_name in cols:
            if col_name in ("tags", "thing"):
                continue
            vals = row[col_name]
            for val in vals.split(","):
                val = val.strip()
                m = value_regex.match(val)
                if not m:
                    values[val].append(Value(val, None, "", col_name, row_name))
                    continue
                (name, number, unit) = m.group(1, 2, 3)
                num, uncertainty = parse_number(number)
                values[col_name].append(Value(
                    name, num, unit, col_name, row_name, uncertainty
                ))
        thing.values = dict(values)
        things.append(thing)
    return things


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
    values = [value for thing in things for values in thing.values.values() for value in values]

    broken = [value.name for value in values if value.value is None]
    values_by_kind = defaultdict(list)
    for value in values:
        if value.value is None:
            continue
        values_by_kind[value.kind].append(value)

    units_by_kind = defaultdict(set)
    for kind, values in values_by_kind.items():
        units_by_kind[kind] = set(value.unit for value in values)
    units_by_kind = dict(units_by_kind)
    print("Broken:", broken)
    pprint(units_by_kind)

    things_serial = [asdict(thing) for thing in things]
    json.dump(things_serial, output, indent=2)


if __name__ == "__main__":
    main()
