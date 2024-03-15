import json
from dataclasses import dataclass
from typing import List
from math import floor, log10

def scientific(num: float, precision: int=None):
    magnitude = floor(log10(num))
    if precision != None:
        num *= 10**(precision - magnitude - 1)
        num = round(num)/10**(precision - 1)
        return f"{num}e{magnitude}"
    return f"{num / 10**magnitude}e{magnitude}"

@dataclass
class ExampleValue:
    thing: str
    measurement: str
    name: str = ""
    value: float = 0
    units: str = ""
    called: str = ""

    def value_string(self):
        return f"{scientific(self.value, 1)} {self.units}"

    def to_string(self, thing_key: str="thing"):
        return "\n".join(f"{key}: {value}" for key, value in self.to_dict(thing_key).items() if value)

    # def to_string(self):
    #     if self.name:
    #         return f"{self.thing}: {self.name}, {self.measurement}"
    #     return f"{self.thing}, {self.measurement}"

    # def to_string(self):
    #     return json.dumps(self.to_dict)

    def to_dict(self, thing_key: str = "thing"):
        data = {
            thing_key: self.thing,
            "measurement": self.measurement
        }
        if self.name:
            data["name"] = self.name
        if self.value and self.units:
            data["value"] = f"{self.value_string()}"
        return data
    
    def to_messages(self, include_called=True):
        messages = [
            {
                "role": "user",
                "content": self.to_string()
            }
        ]
        if include_called and self.called:
            messages.append({
                "role": "assistant",
                "content": self.called
            })
        return messages

@dataclass
class Example:
    smaller: ExampleValue
    larger: ExampleValue
    question: str = ""

    def to_messages(self, include_question=True):
        messages = []
        user_content = f"smaller: {self.smaller.called}\nvalue: {self.smaller.value_string()}\nlarger: {self.larger.called}\nvalue: {self.larger.value_string()}"
        # user_content = f"{self.smaller.to_string('smaller')}\n{self.larger.to_string('larger')}"
        # user_content = f"1. {self.smaller.to_string()}\n2. {self.larger.to_string()}"
        # user_content = json.dumps([self.smaller.to_dict(), self.larger.to_dict()])
        messages.append({
            "role": "user",
            "content": user_content
        })
        if include_question and self.question:
            messages.append({
                "role": "assistant",
                "content": self.question
            })
        return messages

def examples(*examples: Example | ExampleValue):
    res = []
    for example in examples[:-1]:
        res.extend(example.to_messages())
    res.extend(examples[-1].to_messages(False))
    return res

golf_ball_diameter = ExampleValue("Golf ball", "length", "diameter", called="Diameter of a golf ball", value=4.3e-2, units="m")
eiffel_tower_length = ExampleValue("Eiffel tower", "length", called="Height of the Eiffel Tower", value=330, units="m")
earth_circumference = ExampleValue("Earth", "length", "circumference", called="Circumference of the earth", value=1.98e7, units="m")
water_bottle_volume = ExampleValue("Water bottle", "volume", called = "Volume of a water bottle", value=5e-4, units="m3")
corolla_trunk_volume = ExampleValue("Corolla", "volume", "trunk", called = "Volume of the trunk of a Corolla", value=0.34, units="m3")
iphone_mass = ExampleValue("iPhone", "mass", "battery", called = "Mass of an iPhone battery", value=50, units="g")
titanic_mass = ExampleValue("titanic", "mass", called = "Mass of the Titanic", value=4.2e10, units="g")

example_1 = Example(golf_ball_diameter, eiffel_tower_length, "Q: How many *golf balls* placed end to end would it take to reach the top of the *Eiffel tower*? A: (answer) Golf balls")
example_2 = Example(water_bottle_volume, corolla_trunk_volume, "Q: How many *water bottles* could fit in the *trunk of a Corolla*? A: (answer) Water bottles")
example_3 = Example(iphone_mass, titanic_mass, "Q: The *titanic* weighs as much as how many *iPhone batteries*? A: (answer) iPhone batteries")
example_4 = Example(eiffel_tower_length, earth_circumference, "Q: How many *eiffel towers* would it take to wrap all the way around *the Earth's equator*? A: (answer) Eiffel towers")

full_example_1 = examples(example_1, example_2, example_3)
full_example_2 = examples(example_2, example_3, example_1)

calling_example_1 = examples(golf_ball_diameter, eiffel_tower_length, titanic_mass, corolla_trunk_volume)

def completion(example: Example):
    return examples(example_1, example_2, example_3, example_4, example)

def completion_called(example: ExampleValue):
    return examples(golf_ball_diameter, titanic_mass, earth_circumference, corolla_trunk_volume, example)

# length_example_1 = [
#     {
#         "role": "user",
#         "content": "1. Titanic, mass\n2. iPhone: battery, mass"
#     },
#     {
#         "role": "assistant",
#         "content": "The Titanic weighs as much as how many iPhone batteries?"
#     },
#     {
#         "role": "user",
#         "content": "1. Eiffel tower, length\n2. Golf ball: diameter, length"
#     },
#     {
#         "role": "assistant",
#         "content": "How many golf balls stacked on top of each other would it take to reach the top of the Eiffel tower?"
#     },
#     {
#         "role": "user",
#         "content": "Pluto, mass\nMars helicopter ingenuity, mass"
#     }
# ]

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