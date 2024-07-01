import json
import math
import random
from typing import List
import click
import clean
from images import image_search
from question import Question
from value import Value
from natural_language import create_names


def generate_names(values: List[Value], manual=False):
    values = create_names(values, manual=manual)
    return values


def load_values(filename: str):
    try:
        with open(filename, "r") as file:
            return [Value.deserialize(value) for value in json.load(file)]
    except FileNotFoundError:
        return []


def save_values(values, file):
    json.dump([value.serialize() for value in values], file, indent=2)


def create_values(input_file, values_filename, manual=False):
    values = clean.clean(input_file)
    existing_values = load_values(values_filename)
    existing_values = {value.key(): value for value in existing_values}
    for value in values:
        existing = existing_values.get(value.key())
        if existing:
            value.name = existing.name
            value.quality = existing.quality
            value.generated = existing.generated
            value.image = existing.image or value.image

    values = generate_names(values, manual=manual)
    images = {}
    for value in values:
        images[value.thing] = value.image or images.get(value.thing, "")
    try:
        for thing in images.keys():
            image = images[thing]
            if not image.startswith("http"):
                image_url = image_search(image or thing) or ""
                images[thing] = image_url
                print(image, thing, image_url)
    except KeyboardInterrupt:
        pass
    for value in values:
        value.image = images[value.thing]
    with open(values_filename, "w") as values_file:
        save_values(values, values_file)
    return [value for value in values if value.name]


def load_questions(filename: str = "./questions.json"):
    try:
        with open(filename, "r") as f:
            return [Question.deserialize(data) for data in json.load(f)]
    except FileNotFoundError:
        return []


def save_questions(questions: List[Question], file):
    json.dump([question.serialize() for question in questions], file, indent=2)


def create_questions(values: List[Value], questions_filename, count=20):
    questions = load_questions(questions_filename)
    keys = {question.key() for question in questions}
    generated = 0
    tries = 0
    while generated < count and tries < 1e6:
        tries += 1
        matches = []
        while not matches:
            value1 = random.choice(values)
            matches = [
                value
                for value in values
                if value.measurement == value1.measurement
                and value.thing != value1.thing
                and str(value.value.units) == str(value1.value.units)
            ]
        value2 = random.choice(matches)
        answer = value1.value / value2.value
        answer_magnitude = math.log10(answer.value)
        if answer_magnitude < -3 and random.random() > 2 ** (answer_magnitude / 4):
            value1, value2 = value2, value1
        answer = value1.value / value2.value
        answer_magnitude = math.log10(answer.value)
        question = Question(
            [value1, value2],
            f"What is the ratio of the *{value1.name}* to the *{value2.name}*",
            answer=answer.value,
            quality=1.0,
            measurement=value1.measurement,
            style="ratio",
        )
        key = question.key()
        if key not in keys:
            questions.append(question)
            keys.add(key)
            generated += 1
            tries = 0
    with open(questions_filename, "w") as questions_file:
        save_questions(questions, questions_file)
    return questions


@click.command()
@click.argument("input", type=click.File("r"), default="Fermidle - Values.tsv")
@click.argument("output", type=click.Path(), default="questions.json")
@click.option("--values", type=click.Path(), default="values.json")
@click.option("--seed", "-s", default="")
@click.option("--manual", "-m", is_flag=True)
@click.option("--judge", "-j", is_flag=True)
@click.option("--count", "-c", default=20)
def main(input, output, values, seed, manual, judge, count):
    if seed:
        random.seed(seed)
    named_values = create_values(input, values, manual=manual)
    if seed:
        random.seed(seed)
    questions = create_questions(named_values, output, count=count)


if __name__ == "__main__":
    main()
