#!/usr/bin/env python3

from collections import defaultdict
import logging
import os
from dataclasses import dataclass
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
SYSTEM = "Do not include any values in your questions"
# SYSTEM = "You are a thesaurus. Respond 'synonym1, synonym2, ... | antonym1, antonym2, ...'."
START_MESSAGE = {
    "role": "system",
    "content": SYSTEM,
}


@dataclass
class CompletionContext:
    openai_client: openai.OpenAI
    messages: List[dict]
    model: str = "3"
    live: bool = True


def complete_openai(context: CompletionContext):
    """Complete the current message using OpenAI."""
    try:
        response = ""
        stream = context.openai_client.chat.completions.create(
            messages=context.messages,
            model=OPENAI_MODELS.get(context.model, context.model),
            stream=True,
        )
        for part in stream:
            if part.choices[0].finish_reason == "stop":
                break
            content = part.choices[0].delta.content
            response += content
            if context.live:
                print(content, end="", flush=True)
    except openai.OpenAIError as e:
        print(f"An API error occurred: {e}")
    return response


COMPLETION = {v: complete_openai for v in OPENAI_MODELS.keys()}
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


def complete(example: Example, model: str = "3") -> None:
    """Create a question using GPT completion"""

    # Initialize the OpenAI client with API key from the environment
    client = openai.OpenAI()
    for example_value in (example.smaller, example.larger):
        example_messages = examples.complete_calling(example_value)
        messages = [START_MESSAGE]
        # messages = []
        messages.extend(example_messages)
        for message in messages:
            # print(f"{message['role']}: {message['content']}")
            print(message)
        response = COMPLETION[model](
                        CompletionContext(
                            openai_client=client,
                            messages=messages,
                            live=False
                        )
                    )
        print(response)
        example_value.called = response
    example_messages = examples.completion(example)
    for message in example_messages:
        print(message)
    response = COMPLETION[model](
                    CompletionContext(
                        openai_client=client,
                        messages=example_messages,
                        live=False
                    )
                )
    print(response)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        random.seed(sys.argv[1])
    values = load_values("../values.json")
    lengths = values.get('mass', [])
    # print(json.dumps(lengths[:2]))
    # length_values = values["length"]
    length_pair = random.sample(lengths, 2)
    length_pair.sort(key=lambda x: x.value)
    complete(Example(length_pair[0], length_pair[1]), "3")
    # print(values)
    # value = random.choice(lengths)
    # print(len(values))
    # complete(value)
