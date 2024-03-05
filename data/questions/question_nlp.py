#!/usr/bin/env python3

import logging
import os
from dataclasses import dataclass
from typing import List

import openai
from dotenv import load_dotenv
import examples

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
SYSTEM = 'Give a short middle-school level numerical question given a data specification'
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


COMPLETION = {v: complete_openai for v in OPENAI_MODELS.values()}
# Utilities


def complete(model: str = "gpt-3.5-turbo") -> None:
    """Create a question using GPT completion"""

    # Initialize the OpenAI client with API key from the environment
    client = openai.OpenAI()

    messages = [START_MESSAGE]
    messages.extend(examples.length_example_1)
    enabled = True
    response = COMPLETION[model](
                    CompletionContext(
                        openai_client=client,
                        messages=messages,
                        live=False
                    )
                )
    print(response)

if __name__ == "__main__":
    complete()
