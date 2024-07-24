"""Use LLMs with memory of past prompts, so you can just re-run code without waiting/paying for API requests"""

__version__ = "0.0.1"

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
from typing import Dict, List
from dotenv import load_dotenv
import atexit
import platformdirs
import hashlib
from pathlib import Path

import openai

# Load environment variables
load_dotenv()

OPENAI_MODELS = {
    "3": "gpt-4o-mini",
    "4": "gpt-4o",
    "gpt-3.5": "gpt-3.5",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-4": "gpt-4",
    "gpt-4o": "gpt-4o",
    "gpt-4-turbo": "gpt-4-turbo-preview",
}

ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"

CACHE_DIR = platformdirs.user_cache_dir("LLMem")
cache = {}

def set_cache_dir(to: str):
    CACHE_DIR = to

def get_cache(key: str):
    if key in cache:
        val = cache.get(key, {})
    else:
        path = Path(CACHE_DIR, f"{key}.json")
        if path.exists():
            with path.open() as f:
                val = json.load(f)
        else:
            val = {}
        cache[key] = val
    return val

@dataclass
class Message:
    content: str
    role: str = ROLE_USER

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content
        }

class CompletionContext(ABC):
    @abstractmethod
    def complete(self, messages: List[Message]):
        pass

@dataclass
class OpenAICompletionContext(CompletionContext):
    model: str = "3"
    live: bool = False
    client: openai.OpenAI = field(init=False)
    cache: Dict[str, str] = field(init=False)

    def __post_init__(self):
        self.client = openai.OpenAI()
        self.model = OPENAI_MODELS.get(self.model, self.model)
        self.cache = get_cache(f"openai-{self.model}")

    def complete(self, messages: List[Message]):
        """Complete the current message using OpenAI."""
        digest, messages = message_digest(messages)
        response = self.cache.get(digest)
        if response:
            print("RESPONSE", response)
            return response
    
        try:
            response = ""
            completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                stream=False,
            )
            response = completion.choices[0].message.content
            # print(stream)
            # for part in stream:
            #     print(part)
            #     if part.choices[0].finish_reason:
            #         break
            #     content = part.choices[0].delta.content
            #     response += content
            #     if self.live:
            #         print(content, end="", flush=True)
        except openai.OpenAIError as e:
            print(f"An API error occurred: {e}")
        self.cache[digest] = response
        return response

class ManualCompletionContext(CompletionContext):
    cache: Dict[str, str] = field(init=False)

    def __post__init__(self):
        self.cache = get_cache(f"openai-{self.model}")

    def complete(self, messages: List[Message]):
        digest, _ = message_digest(messages)
        if digest in self.cache:
            return self.cache[digest]
        response = input("response: ")
        self.cache[digest] = response
        return response
    
def message_digest(messages: List[Message]):
    messages = [message.to_dict() for message in messages]

    string = json.dumps(messages)
    digest = hashlib.sha256(string.encode()).hexdigest()
    return digest, messages

def message_chain(messages: List[str], roles=[ROLE_USER, ROLE_ASSISTANT]):
    chain = []
    i = 0
    for message in messages:
        chain.append(Message(message, roles[i % len(roles)]))
        i += 1
    return chain

def save_on_exit():
    for key, value in cache.items():
        path = Path(CACHE_DIR, f"{key}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            json.dump(value, f)

atexit.register(save_on_exit)