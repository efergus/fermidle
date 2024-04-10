

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import random
from typing import List
from dotenv import load_dotenv

import openai

# Load environment variables
load_dotenv()

OPENAI_MODELS = {
    "3": "gpt-3.5-turbo",
    "4": "gpt-4-turbo-preview",
    "gpt-3.5": "gpt-3.5",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-4": "gpt-4",
    "gpt-4-turbo": "gpt-4-turbo-preview"
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

def create_names(values, context: OpenAICompletionContext, sample_size: int = 12):
    context = OpenAICompletionContext()
    randomized_values = [value for vals in values.values() for value in vals]
    random.shuffle(randomized_values)
    named_values = {value.key(): value for value in randomized_values if value.name}
    existing_values = set(value.key() for value in randomized_values)
    for key in list(named_values.keys()):
        if key not in existing_values:
            print(key)
            del named[key]
    all_named = list(named.values())
    random.shuffle(all_named)
    all_named.sort(key=lambda x: x.quality, reverse=True)
    print("To generate:", len(randomized_values)-len(all_named))
    named_examples = all_named[:sample_size]
    named_example_messages = [message for example in named_examples for message in example.to_messages()]
    added = []
    try:
        for value in randomized_values:
            key = name_key(value)
            if key in named:
                continue
            # print(value.to_string())
            called = context.complete([
                START_MESSAGE,
                *named_example_messages,
                *value.to_messages()
            ])
            print(called)
            if manual_quality:
                quality = float(input("Quality (0-5): "))
                value.quality = min(quality/5, 0.99)
            value.called = called
            value.generated = now()
            added.append(value)
    except KeyboardInterrupt:
        pass
    for value in added:
        named[value.key()] = value
        # print(value)
    if len(named):
        with open(labels_file, 'w') as f:
            json.dump([value.to_dict() for value in named.values()], f, indent=2)
    return named