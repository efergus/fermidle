#!/usr/bin/env python3

from abc import ABC, abstractmethod
from collections import defaultdict
import logging
import os
from dataclasses import dataclass, field
import random
from typing import List

import openai
from dotenv import load_dotenv
import examples
from examples import Example, ExampleValue, example_1
import json
import sys

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
SYSTEM = "Don't include any values"
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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        random.seed(sys.argv[1])
    values = load_values("./values.json")
    try:
        with open("./names.json", "r") as f:
            named = json.load(f)
    except FileNotFoundError:
        named = []
    named_set = {(value["thing"], value["measurement"], value.get('name', '')) for value in named}
    context = OpenAICompletionContext()
    added = []
    try:
        for values in values.values():
            for value in values:
                if (value.thing, value.measurement, value.name) in named_set:
                    continue
                value.called = complete_called(value, context).strip()
                added.append(value)
    except:
        pass
    print(added)
    for value in added:
        named.append({
            **value.to_dict(),
            "called": value.called
            })
    with open('./names.json', 'w') as f:
        json.dump(named, f, indent=2)
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
