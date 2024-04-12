import json
from typing import List
import click
import clean
from value import Value
from natural_language import create_names


def generate_names(values: List[Value], manual=False):
    values = create_names(values)
    return values


def load_values(filename: str):
    try:
        with open(filename, "r") as file:
            return [Value.deserialize(value) for value in json.load(file)]
    except FileNotFoundError:
        return []


def save_values(values, file):
    json.dump([value.serialize() for value in values], file, indent=2)


def create_values(input_file, values_filename):
    values = clean.clean(input_file)
    existing_values = load_values(values_filename)
    existing_values = {value.key(): value for value in existing_values}
    for value in values:
        key = value.key()
        existing = existing_values.get(key)
        if key in existing:
            value.name = existing.name
            value.quality = existing.quality
            value.generated = existing.generated

    values = generate_names(values)
    with open(values_filename, "w") as values_file:
        save_values(values, values_file)
    return [value for value in values if value.name]


@click.command()
@click.argument("input", type=click.File("r"), default="Fermidle - Values.tsv")
@click.argument("output", type=click.File("w"), default="questions.json")
@click.option("--values", type=click.Path(), default="values.json")
@click.option("--judge", "-j", is_flag=True)
def main(input, output, values, judge):
    named_values = create_values(input, values)


if __name__ == "__main__":
    main()
