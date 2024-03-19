#!/usr/bin/env python3

from abc import ABC, abstractmethod
from collections import defaultdict
import logging
import math
import os
from dataclasses import dataclass, field
import random
from typing import Dict, List, Set
import click

import openai
from dotenv import load_dotenv
import examples
from examples import Example, ExampleValue, example_1
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
    "gpt-4-turbo": "gpt-4-turbo-preview"
}
# SYSTEM = """
# Given data of the from:
# """.strip()
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

def load_values(filename: str):
    with open(filename, "r") as file:
        data = json.load(file)
    example_values = defaultdict(list)
    for thing in data:
        for values in thing["values"].values():
            for value in values:
                example_values[value["kind"]].append(examples.ExampleValue(thing["name"], value["kind"], value["name"], value=value["value"]["value"], units=value["value"]["units"].replace('1', '')))
    return dict(example_values)

def name_key(value: dict | ExampleValue):
    if type(value) == ExampleValue:
        return (value.thing, value.measurement, value.name)
    return (value["thing"], value["measurement"], value.get('name', ''))

def load_names(filename: str):
    try:
        with open(filename, "r") as f:
            named = json.load(f)
    except FileNotFoundError:
        named = []
    named_dict = {name_key(value): value for value in named}
    return named_dict
    
def complete_called(example: ExampleValue, context: CompletionContext):
    """Detrmine a value's name using LLM completion"""
    messages = [START_MESSAGE, *examples.completion_called(example)]
    # for message in messages:
    #     print(f"{message['role']}: {repr(message['content'])}")
    response = context.complete(messages)
    print(response)
    return response

def complete(example: Example, context: CompletionContext) -> None:
    """Create a question using LLM completion"""
    messages = examples.completion(example)
    # for message in messages:
    #     print(f"{message['role']}: {repr(message['content'])}")
    response = context.complete(messages)
    print(response)
    return response


def create_called():
    values = load_values("./values.json")
    named = load_names("./names.json")
    context = OpenAICompletionContext()
    added = []
    try:
        for values in values.values():
            for value in values:
                key = name_key(value)
                if key in named:
                    continue
                called = complete_called(value, context).strip()
                value_dict = {
                    **value.to_dict(),
                    "called": called,
                    "generated": datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()
                    }
                added.append(value_dict)
    except KeyboardInterrupt:
        pass
    for value in added:
        named[name_key(value)] = value
        print(value)
    if len(named):
        with open('./names.json', 'w') as f:
            json.dump(list(named.values()), f, indent=2)
    return named
    # lengths: List[ExampleValue] = values.get('mass', [])
    # # print(json.dumps(lengths[:2]))
    # # length_values = values["length"]
    # length_pair = random.sample(lengths, 2)
    # length_pair.sort(key=lambda x: x.value)
    # smaller, larger = length_pair
    # for value in length_pair:
    #     value.called = complete_called(value, context)
    # complete(Example(*length_pair), context)
    # print(values)
    # value = random.choice(lengths)
    # print(len(values))
    # complete(value)

ValuesByMeasurement = Dict[str, List[ExampleValue]]

def random_value(values: List[ExampleValue]):
    """Choose a value with a random magnitude
    TODO: Actually implement in a way that works lol
    """
    # values = [value for value in values if value not in exclude]
    if(not values):
       raise ValueError("No values available to choose from")
    for value in values:
        if value.value <= 0:
            print(f"Skipping {value}")
    logged = [math.log(value.value) for value in values if value.value > 0]
    min_value = min(logged)
    max_value = max(logged)
    delta = max_value - min_value
    point = random.random()*delta + min_value
    while True:
        value = random.choice(values)
        scale = math.fabs(point-math.log(value.value))/delta
        if random.random() > scale:
            return value

def minmax_value(value_1, value_2):
    if value_1.value <= value_2.value:
        return (value_1, value_2)
    return (value_2, value_1)

def create_questions(values_by_measurement: ValuesByMeasurement, seed: str = ""):
    if seed:
        random.seed(seed)
    values = values_by_measurement["length"]
    smaller, larger = minmax_value(random_value(values), random_value(values))
    print(smaller, larger)
    # print(list(values_by_measurement.values())[0][:10])

@click.command()
@click.option('--names', default=False)
@click.option('--seed', default="")
def main(names, seed):
    if names:
        create_called()
    names = load_names("./names.json")
    values_by_measurement = defaultdict(list)
    for value_dict in names.values():
        value = ExampleValue.from_dict(value_dict)
        values_by_measurement[value.measurement].append(value)
    create_questions(dict(values_by_measurement), seed)

if __name__ == "__main__":
    main()