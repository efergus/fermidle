#!/usr/bin/env python3

from abc import ABC, abstractmethod
from collections import defaultdict
import logging
import math
import os
from dataclasses import dataclass, field
import random
from typing import Dict, List, Set, Tuple
import click

import openai
from dotenv import load_dotenv
import examples
from examples import Example, ExampleValue, example_1, scientific
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


def create_called(context: OpenAICompletionContext):
    values = load_values("./values.json")
    named = load_names("./names.json")
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
    value = random.choice(values)
    return value
    if(not values):
       raise ValueError("No values available to choose from")
    logged = [math.log(value.value) for value in values if value.value > 0]
    min_value = min(logged)
    max_value = max(logged)
    delta = max_value - min_value
    point = random.random()*delta + min_value
    while True:
        value = random.choice(values)
        scale = math.fabs(point-math.log(value.value))/delta*0.8
        if random.random() > scale:
            return value

def random_ordered_pair(values: List[ExampleValue]):
    values = random.sample(values, 2)
    return minmax_value(*values)

def minmax_value(value_1, value_2):
    if value_1.value <= value_2.value:
        return (value_1, value_2)
    return (value_2, value_1)

# def load_questions(filename: str):
    

def create_question(values, context, example_questions):
    smaller, larger = minmax_value(random_value(values), random_value(values))
    example = Example(smaller, larger)
    messages = [
        system_message(f"Choose the most appropriate example question for the given items.\nExample questions:\n{example_questions}"),
        *examples.completion(example)
    ]
    # for message in messages:
    #     print(message)
    response = context.complete(messages)
    print(messages[-1])
    print(response)
    print(scientific(larger.value / smaller.value, 2))

def create_questions(values_by_measurement: ValuesByMeasurement, context: OpenAICompletionContext, seed: str = "", count: int = 1):
    with open("./length/questions.txt") as f:
        example_questions = f.read().strip()
    if seed:
        random.seed(seed)
    values = values_by_measurement["length"]
    values = [value for value in values if value.value > 0]
    for _ in range(count):
        create_question(values, context, example_questions)

def create_manual_questions(values_by_measurement: ValuesByMeasurement, seed: str = ""):
    if seed:
        random.seed(seed)
    values = values_by_measurement["length"]
    values = [value for value in values if value.value > 0]
    examples = []
    try:
        while True:
            smaller, larger = random_ordered_pair(values)
            example = Example(smaller, larger)
            print(example.to_prompt())
            question = input("Question: ")
            example.question = question
            print()
            examples.append(example)
    except KeyboardInterrupt:
        pass
    print("Done")
    data = [example.to_dict() for example in examples]
    data_string = json.dumps(data, indent=2)
    print(data_string)

# @dataclass
# class QuestionItem:
#     measurement: str
#     units: str

# @dataclass
# class QuestionFormat:
#     items: List[QuestionItem]
#     questions: List[str]

#     @staticmethod
#     def new(items: List[Tuple[str, str]], *questions: str):
#         return QuestionFormat([QuestionItem(*item) for item in items], questions)

# length_question_format = QuestionFormat.new([('length', 'm'), ('length', 'm')],
#                                             "How many *X* would it take ")

@click.command()
@click.option('--names', default=False)
@click.option('--seed', '-s', default="")
@click.option('--count', '-c', default=1)
@click.option('--manual', '-m', is_flag=True)
def main(names, seed, count, manual):
    context = OpenAICompletionContext()
    if names:
        create_called(context)
    names = load_names("./names.json")
    values_by_measurement = defaultdict(list)
    for value_dict in names.values():
        value = ExampleValue.from_dict(value_dict)
        values_by_measurement[value.measurement].append(value)
    values = dict(values_by_measurement)
    # create_questions(dict(values_by_measurement), context, seed, count=count)
    # print(manual)
    if manual:
        create_manual_questions(values, seed)

if __name__ == "__main__":
    main()