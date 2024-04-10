import json
from typing import List
import click
import clean
from data import Value
from natural_language import OpenAICompletionContext, create_names

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
    json.dump([value.serialize() for value in values], file)

def create_values(input_file, values_filename):
    values = clean.clean(input_file)
    existing_values = load_values(values_filename)
    # existing_names = load_names()
    values = generate_names(values)
    with open(values_filename, "w") as values_file:
        save_values(values, values_file)
    return [value for value in values if value.name]

@click.command()
@click.argument("input", type=click.File("r"), default="Fermidle - Values.tsv")
@click.argument("output", type=click.File("w"), default="questions.json")
@click.option("--values", type=click.Path(), default="values.json")
def main(input, output, values):
    create_values(input, values)

if __name__ == "__main__":
    main()