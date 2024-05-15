from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
import random
from typing import List
from dotenv import load_dotenv

import openai

from value import Value

# Load environment variables
load_dotenv()

OPENAI_MODELS = {
    "3": "gpt-3.5-turbo",
    "4": "gpt-4-turbo-preview",
    "gpt-3.5": "gpt-3.5",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-4": "gpt-4",
    "gpt-4-turbo": "gpt-4-turbo-preview",
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

class ManualCompletionContext(CompletionContext):
    def complete(self, _messages: List[dict]):
        response = input("response: ")
        return response


SYSTEM = "Convert data to what you'd call it. Don't include any values"
START_MESSAGE = {
    "role": "system",
    "content": SYSTEM,
}


def create_names(
    values: List[Value],
    sample_size: int = 12,
    start_message=START_MESSAGE,
    manual_quality=False,
    manual = False
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
        print(json.dumps(message, indent=2))
    try:
        for value in randomized_values:
            if value.name:
                continue

            messages = value.to_messages()
            print()
            print(messages[-1]["content"])
            name = context.complete([START_MESSAGE, *named_example_messages, *messages])
            print(name)
            if manual:
                value.quality = 1.0
            if manual_quality:
                quality = float(input("Quality (0-5): "))
                value.quality = min(quality / 5, 0.99)
            value.name = name
    except KeyboardInterrupt:
        pass
    return values
