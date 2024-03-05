
from dataclasses import dataclass

@dataclass
class ExampleValue:
    thing: str
    kind: str
    name: str = ""

    def to_string(self):
        if self.name:
            return f"{self.thing}: {self.name}, {self.kind}"
        return f"{self.thing}, {self.kind}"

@dataclass
class Example:
    smaller: ExampleValue
    larger: ExampleValue
    question: str = ""

    def to_messages(self):
        messages = []
        user_content = f"1. {self.smaller.to_string()}\n2. {self.larger.to_string()}"
        messages.append({
            "role": "user",
            "content": user_content
        })
        if self.question:
            messages.append({
                "role": "assistant",
                "content": self.question
            })
        return messages

golf_ball_diameter = ExampleValue("Golf ball", "length", "diameter")
eiffel_tower_length = ExampleValue("Eiffel tower", "length")

length_example_1 = [
    {
        "role": "user",
        "content": "1. Golf ball, diameter (length)\n2. Eiffel tower, length"
    },
    {
        "role": "assistant",
        "content": "How many golf balls stacked on top of each other would it take to reach the top of the Eiffel tower?"
    },
    {
        "role": "user",
        "content": "1. iPhone, battery (mass)\n2. Titanic, mass"
    }
]

length_example_1 = [
    {
        "role": "user",
        "content": "1. Titanic, mass\n2. iPhone: battery, mass"
    },
    {
        "role": "assistant",
        "content": "The Titanic weighs as much as how many iPhone batteries?"
    },
    {
        "role": "user",
        "content": "1. Eiffel tower, length\n2. Golf ball: diameter, length"
    },
    {
        "role": "assistant",
        "content": "How many golf balls stacked on top of each other would it take to reach the top of the Eiffel tower?"
    },
    {
        "role": "user",
        "content": "Pluto, mass\nMars helicopter ingenuity, mass"
    }
]

length_example_2 = [
    {
        "role": "user",
        "content": "1. Golf ball, diameter (length)\n2. Eiffel tower, length"
    },
    {
        "role": "assistant",
        "content": "How many golf balls stacked on top of each other would it take to reach the top of the Eiffel tower?"
    },
    {
        "role": "user",
        "content": "1. Water bottle, volume\n2. Corolla, trunk (volume)"
    },
    {
        "role": "assistant",
        "content": "How many water bottles could fit in the trunk of a Corolla"
    },
    {
        "role": "user",
        "content": "1. Australia, surface area\n2. Penny, face area (surface area)"
    }
]

length_example_3 = [
    {
        "role": "user",
        "content": "1. Golf ball, diameter (length)\n2. Eiffel tower, length"
    },
    {
        "role": "assistant",
        "content": "How many golf balls stacked on top of each other would it take to reach the top of the Eiffel tower?"
    },
    {
        "role": "user",
        "content": "1. Water bottle, volume\n2. Corolla, trunk (volume)"
    },
    {
        "role": "assistant",
        "content": "How many water bottles could fit in the trunk of a Corolla"
    },
    {
        "role": "user",
        "content": "1. Hydrogen atom, volume\n2. Mug, volume"
    }
]