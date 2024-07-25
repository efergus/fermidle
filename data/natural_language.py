import random
from typing import List
import re

import openai

from llmem import Message, ManualCompletionContext, OpenAICompletionContext
from value import Value

START_MESSAGE = Message(
    """
    Convert data to what you'd call it. Don't include any values. For example, if you got
    "thing: Eiffel Tower, measurement: length" you should respond "The height of the Eiffel Tower".
    If the thing is generic, use generic language, like "The volume of an apple".
    You can fix language/grammar to be more precise, so "thing: 50 cal rifle, measurement: energy"
    would become "The energy of a bullet fired from a .50 cal rifle".
    """,
    "system"
)

START_MESSAGE.content = re.sub(r"(\s|\n)+", " ", START_MESSAGE.content).strip()

def create_names(
    values: List[Value],
    sample_size: int = 0,
    start_message=START_MESSAGE,
    manual_quality=False,
    manual=False,
    overwrite=False
):
    context = ManualCompletionContext() if manual else OpenAICompletionContext()
    randomized_values = values.copy()
    random.shuffle(randomized_values)
    all_named = [value for value in randomized_values if value.name]
    all_named.sort(key=lambda x: x.quality, reverse=True)
    print("To generate:", len(randomized_values) - len(all_named))
    named_examples = all_named[:sample_size].copy()
    random.shuffle(named_examples)
    named_example_messages = [
        message for example in named_examples for message in example.to_messages()
    ]
    for message in named_example_messages:
        print(f"{message.role}:")
        print(repr(message.content))
        print()
    try:
        i = 1
        total = len(randomized_values)
        for value in randomized_values:
            if value.name and not overwrite:
                continue

            messages = value.to_messages(False)
            print()
            print(messages[-1].content)
            name = context.complete([START_MESSAGE, *named_example_messages, *messages]).rstrip(".")
            print(f"{i:03d}/{total}", name)
            i+=1
            if manual:
                value.quality = 1.0
            if manual_quality:
                quality = float(input("Quality (0-5): "))
                value.quality = min(quality / 5, 0.99)
            value.name = name
    except KeyboardInterrupt:
        pass
    return values
