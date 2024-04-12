#!/usr/bin/env python3

from abc import ABC, abstractmethod
from collections import defaultdict
import logging
import math
import os
from dataclasses import dataclass, field
import random
from typing import Dict, Iterable, List, Set, Tuple
import click

import openai
from dotenv import load_dotenv
import examples
from examples import Question, ExampleValue, example_1, now, scientific
import json
import sys
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# Constants
# MODELS = ["gpt-3.5", "gpt-3.5-turbo", "gpt-4", "gpt-4-1106-preview"]
OPENAI_MODELS = {
    "3": "gpt-3.5-turbo",
    "4": "gpt-4-turbo-preview",
    "gpt-3.5": "gpt-3.5",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-4": "gpt-4",
    "gpt-4-turbo": "gpt-4-turbo-preview",
}
# SYSTEM = """
# Given data of the from:
# """.strip()


def system_message(message: str):
    return {
        "role": "system",
        "content": message,
    }


SYSTEM = "Convert data to what you'd call it. Don't include any values"
# SYSTEM = "You are a thesaurus. Respond 'synonym1, synonym2, ... | antonym1, antonym2, ...'."
START_MESSAGE = {
    "role": "system",
    "content": SYSTEM,
}


class CompletionContext(ABC):

    @abstractmethod
    def complete(self, messages: List[dict]):
        pass


@dataclass
class OpenAICompletionContext(CompletionContext):
    model: str = "3"
    live: bool = False
    openai_client: openai.OpenAI = field(init=False)

    def __post_init__(self):
        self.client = openai.OpenAI()

    def complete(self, messages: List[dict]):
        """Complete the current message using OpenAI."""
        try:
            response = ""
            stream = self.client.chat.completions.create(
                messages=messages,
                model=OPENAI_MODELS.get(self.model, self.model),
                stream=True,
            )
            for part in stream:
                if part.choices[0].finish_reason == "stop":
                    break
                content = part.choices[0].delta.content
                response += content
                if self.live:
                    print(content, end="", flush=True)
        except openai.OpenAIError as e:
            print(f"An API error occurred: {e}")
        return response


# Utilities


def load_values(file):
    data = json.load(file)
    example_values = defaultdict(list)
    for thing in data:
        for values in thing["values"].values():
            for value in values:
                example_values[value["kind"]].append(
                    examples.ExampleValue(
                        thing["name"],
                        value["kind"],
                        value["name"],
                        value=value["value"]["value"],
                        units=value["value"]["units"].replace("1", ""),
                    )
                )
    return dict(example_values)


def name_key(value: dict | ExampleValue):
    if type(value) == ExampleValue:
        return value.key()
    return (value["thing"], value["measurement"], value.get("name", ""))


def load_names(file):
    named = json.load(file)
    named_dict = {name_key(value): ExampleValue.from_dict(value) for value in named}
    return named_dict


def complete_called(example: ExampleValue, context: CompletionContext):
    """Detrmine a value's name using LLM completion"""
    messages = [START_MESSAGE, *examples.completion_called(example)]
    response = context.complete(messages)
    print(response)
    return response


def complete(example: Question, context: CompletionContext) -> None:
    """Create a question using LLM completion"""
    messages = examples.completion(example)
    response = context.complete(messages)
    print(response)
    return response


def create_names(
    context: OpenAICompletionContext,
    values_file: str = "./values.json",
    labels_file: str = "./names.json",
    sample_size: int = 10,
    manual_quality: bool = False,
):
    values = load_values(values_file)
    randomized_values = [value for vals in values.values() for value in vals]
    random.shuffle(randomized_values)
    named = load_names(labels_file)
    existing_values = set(value.key() for value in randomized_values)
    for key in list(named.keys()):
        if key not in existing_values:
            print(key)
            del named[key]
    all_named = list(named.values())
    random.shuffle(all_named)
    all_named.sort(key=lambda x: x.quality, reverse=True)
    print("To generate:", len(randomized_values) - len(all_named))
    named_examples = all_named[:sample_size]
    named_example_messages = [
        message for example in named_examples for message in example.to_messages()
    ]
    added = []
    try:
        for value in randomized_values:
            key = name_key(value)
            if key in named:
                continue
            # print(value.to_string())
            called = context.complete(
                [START_MESSAGE, *named_example_messages, *value.to_messages()]
            )
            print(called)
            if manual_quality:
                quality = float(input("Quality (0-5): "))
                value.quality = min(quality / 5, 0.99)
            value.called = called
            value.generated = now()
            added.append(value)
    except KeyboardInterrupt:
        pass
    for value in added:
        named[value.key()] = value
        # print(value)
    if len(named):
        with open(labels_file, "w") as f:
            json.dump([value.to_dict() for value in named.values()], f, indent=2)
    return named


def create_called_manual():
    values = load_values("./values.json")
    named = load_names("./names.json")
    added = []
    try:
        randomized = [value for vals in values.values() for value in vals]
        random.shuffle(randomized)
        for value in randomized:
            key = name_key(value)
            if key in named:
                continue
            print()
            print(value.to_string())
            called = input("Called: ")
            if not called:
                continue
            value.called = called
            value.quality = 1.0
            value.generated = now()
            added.append(value.to_dict())
    except KeyboardInterrupt:
        pass
    for value in added:
        named[name_key(value)] = value
        # print(value)
    if len(named):
        with open("./names.json", "w") as f:
            json.dump(list(named.values()), f, indent=2)


ValuesByMeasurement = Dict[str, List[ExampleValue]]


def random_value(values: List[ExampleValue]):
    """Choose a value with a random magnitude
    TODO: Actually implement in a way that works lol
    """
    # values = [value for value in values if value not in exclude]
    value = random.choice(values)
    return value
    if not values:
        raise ValueError("No values available to choose from")
    logged = [math.log(value.value) for value in values if value.value > 0]
    min_value = min(logged)
    max_value = max(logged)
    delta = max_value - min_value
    point = random.random() * delta + min_value
    while True:
        value = random.choice(values)
        scale = math.fabs(point - math.log(value.value)) / delta * 0.8
        if random.random() > scale:
            return value


def random_ordered_pair(values: List[ExampleValue]):
    values = random.sample(values, 2)
    return minmax_value(*values)


def minmax_value(value_1, value_2):
    if value_1.value <= value_2.value:
        return (value_1, value_2)
    return (value_2, value_1)


def question_key(value: Question):
    return (name_key(value.smaller), name_key(value.larger))


def load_questions(filename: str = "./questions.json"):
    try:
        with open(filename, "r") as f:
            examples = [Question.from_dict(data) for data in json.load(f)]
        return {example.key(): example for example in examples}
    except FileNotFoundError:
        return {}


def save_questions(
    questions: Iterable[Question] | Dict[Tuple[str, str, str], Question],
    filename: str = "./questions.json",
):
    if type(questions) == dict:
        questions = questions.values()
    data = sorted(
        (data.to_dict() for data in questions),
        key=lambda x: (1 - x.quality, x.question),
    )
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def create_question(example, context, example_questions, manual_quality=False):
    messages = [
        system_message(
            f"Create a fermi question based on the given items. It should be short. Don't make it fancy."
        ),
        *examples.examples(*example_questions, example),
    ]
    # for message in messages:
    print(messages[-1]["content"].replace("\n", "  |  "))
    response = context.complete(messages)
    print(messages[-1])
    print(response)
    print(scientific(example.larger.value / example.smaller.value, 2))
    example.question = response
    if manual_quality:
        quality = float(input("Quality (0-5): "))
        example.quality = min(quality / 5, 0.99)
    return example


def create_questions(
    values_by_measurement: ValuesByMeasurement,
    context: OpenAICompletionContext,
    seed: str = "",
    count: int = 1,
    sample: int = 10,
    measurement="length",
):
    # with open("./length/questions.txt") as f:
    #     example_questions = f.read().strip()
    questions = load_questions()
    if seed:
        random.seed(seed)
    values = values_by_measurement[measurement]
    values = [value for value in values if value.value > 0]
    example_questions = [
        question for question in questions.values() if question.quality > 0.8
    ]
    example_questions.sort(
        key=lambda x: x.quality if x.measurement == measurement else x.quality * 0.9,
        reverse=True,
    )
    chosen_examples = example_questions[:sample].copy()
    if len(chosen_examples) < sample:
        raise ValueError("Insufficient number of quality example questions")
    for example in chosen_examples:
        for message in example.to_messages():
            print(message)

    random.shuffle(chosen_examples)
    print(len(chosen_examples), "examples")
    try:
        i = 0
        tries = 0
        while i < count and tries < 100:
            smaller, larger = random_ordered_pair(values)
            example = Question(smaller, larger)
            if example.key() in questions:
                tries += 1
                continue
            print()
            question = create_question(example, context, chosen_examples)
            questions[question.key()] = question
            i += 1
            tries = 0
    except KeyboardInterrupt:
        pass
    save_questions(questions)


def create_questions_manual(
    values_by_measurement: ValuesByMeasurement, seed: str = "", measurement="length"
):
    if seed:
        random.seed(seed)
    values = values_by_measurement[measurement]
    print(len(values))
    values = [value for value in values if value.value > 0]
    print(len(values))
    questions = load_questions()
    try:
        while True:
            smaller, larger = random_ordered_pair(values)
            example = Question(smaller, larger, quality=1.0)
            if example.key() in questions:
                continue
            print(example.to_prompt())
            question = input("Question: ")
            if not question:
                continue
            example.question = question
            print()
            questions[example.key()] = example
    except KeyboardInterrupt:
        pass
    print("Done")
    save_questions(questions)


@click.command()
@click.option("--names", "-n", is_flag=True)
@click.option("--seed", "-s", default="")
@click.option("--measurement", "-x", default="length")
@click.option("--count", "-c", default=1)
@click.option("--sample", "-p", default=10)
@click.option("--manual", "-m", is_flag=True)
@click.option("--rate", "-r", is_flag=True)
def main(
    names, seed, measurement: str, count: int, sample: int, manual: bool, rate: bool
):
    context = OpenAICompletionContext()
    measurement = measurement.lower()
    if names:
        if manual:
            create_called_manual()
        else:
            create_names(context, sample, manual_quality=quality)
        return
    existing_values = load_names("./names.json")
    values_by_measurement = defaultdict(list)
    for value in existing_values.values():
        values_by_measurement[value.measurement].append(value)
        # if value.measurement == measurement:
        #     print(value.called, value.value, value_dict)
    values = dict(values_by_measurement)
    if rate:
        questions = load_questions()
        all_questions = list(questions.values())
        if seed:
            random.seed(seed)
        random.shuffle(all_questions)
        try:
            for question in all_questions:
                if question.quality:
                    continue
                print(question.to_prompt())
                print(question.question)
                try:
                    quality = float(input("Quality (0-5): "))
                    question.quality = min(quality / 5, 0.99) if quality != 0 else 0.01
                except ValueError:
                    pass
        except KeyboardInterrupt:
            pass
        save_questions(questions)
    elif manual:
        if not names:
            create_questions_manual(values, seed, measurement=measurement)
    else:
        create_questions(
            dict(values_by_measurement),
            context,
            seed,
            measurement=measurement,
            count=count,
            sample=sample,
        )


if __name__ == "__main__":
    main()
