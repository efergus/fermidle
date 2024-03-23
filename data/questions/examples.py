import json
from dataclasses import dataclass
from typing import Dict, List
from math import floor, log10

def scientific(num: float, precision: int=None, pad=False):
    magnitude = floor(log10(num))
    if precision != None:
        num *= 10**(precision - magnitude - 1)
        num = round(num)/10**(precision - 1)
        num_str = str(num)
        if precision == 1:
            num_str = str(int(num))
        elif pad:
            num_str = num_str.ljust(precision+1, '0')
        return f"{num_str}e{magnitude}"
    return f"{num / 10**magnitude}e{magnitude}"

@dataclass
class ExampleValue:
    thing: str
    measurement: str
    name: str = ""
    value: float = 0
    units: str = ""
    called: str = ""

    def key(self):
        return (self.thing, self.measurement, self.name)

    def value_string(self):
        formatted = scientific(self.value, 2)
        if not self.units:
            return formatted
        return f"{formatted} {self.units}"

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
        if self.value:
            data["value"] = f"{self.value_string()}"
        if self.called:
            data["called"] = self.called
        return data
    
    @staticmethod
    def from_dict(data: dict):
        value, _, units = data.get("value", "").partition(' ')
        if value:
            value = float(value)
        else:
            value = 0.0
        return ExampleValue(data["thing"], data["measurement"], data.get("name", ""), value, units, data.get("called", ""))
    
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
class Question:
    smaller: ExampleValue
    larger: ExampleValue
    question: str = ""
    quality: float = 0.0
    measurement: str = ""

    def __post_init__(self):
        if not self.measurement:
            self.measurement = self.smaller.measurement

    def key(self):
        return (self.smaller.key(), self.larger.key())

    def to_prompt(self):
        return f"{self.smaller.called}: {self.smaller.value_string()}\n{self.larger.called}: {self.larger.value_string()}"

    def to_dict(self):
        return {
            "smaller": self.smaller.to_dict(),
            "larger": self.larger.to_dict(),
            "question": self.question,
            "quality": self.quality
        }
    
    @staticmethod
    def from_dict(data: Dict):
        smaller = data["smaller"]
        larger = data["larger"]
        if type(smaller) == dict:
            smaller = ExampleValue.from_dict(smaller)
        if type(larger) == dict:
            larger = ExampleValue.from_dict(larger)
        return Question(smaller, larger, data["question"], data.get("quality", 1.0))

    def to_messages(self, include_question=True):
        messages = []
        user_content = self.to_prompt()
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
                "content": f"Q: {self.question}"
            })
        return messages

def examples(*examples: Question | ExampleValue):
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
anger_volume = ExampleValue("anger", "volume", called="NO", value=18, units="m3")

example_1 = Question(golf_ball_diameter, eiffel_tower_length, "Q: How many *golf balls* tall is the *Eiffel Tower*?\nA: (answer) Golf balls")
example_2 = Question(water_bottle_volume, corolla_trunk_volume, "Q: How many *water bottles* could fit in the *trunk of a Corolla*?\nA: (answer) Water bottles")
example_3 = Question(iphone_mass, titanic_mass, "Q: The *titanic* weighs as much as how many *iPhone batteries*?\nA: (answer) iPhone batteries")
example_4 = Question(eiffel_tower_length, earth_circumference, "Q: How many *Eiffel Towers* would it take to wrap all the way around *the Earth's equator*?\nA: (answer) Eiffel towers")

orange_diameter = ExampleValue("orange", "length", "diameter", called="Diameter of an orange", value=7.2e-2, units="m")
pacific_depth = ExampleValue("Pacific ocean", "length", "max depth", called="Maximum depth of the Pacific Ocean", value=10.9e3, units="m")
giza_height = ExampleValue("Pyramid of Giza", "length", "height", called="Height of the Pyramid of Giza", value=1.0e2, units="m")
great_white_length = ExampleValue("great white shark", "length", called="Length of a great white shark", value=5, units="m")
moon_circumference = ExampleValue("Moon", "length", "circumference", called="Circumference of the moon", value=1e7, units="m")

length = [
    Question(golf_ball_diameter, eiffel_tower_length, "Q: How many *golf balls* tall is the *Eiffel Tower*?\nA: (answer) Golf balls"),
    Question(orange_diameter, pacific_depth, "Q: How many *orange circumferences* deep is the *Pacific Ocean*?\nA: (answer) Oranges"),
    Question(great_white_length, giza_height, "Q: How many *Great white sharks* tall is the *Pyramid of Giza*?\nA: (answer) Sharks"),
]
# length = [
#     Example(golf_ball_diameter, eiffel_tower_length, "How many *X* tall is the *Y*?"),
#     Example(orange_diameter, pacific_depth, "How many *X* deep is the *Y*?"),
#     ExampleValue(orange_diameter, moon_circumference, "How many *X* would it take to wrap around *Y*"),
#     Example(great_white_length, giza_height, "How many *X* tall is the *Y*?")
# ]

full_example_1 = examples(example_1, example_2, example_3)
full_example_2 = examples(example_2, example_3, example_1)

calling_example_1 = examples(golf_ball_diameter, eiffel_tower_length, anger_volume, titanic_mass, corolla_trunk_volume)

def completion(example: Question):
    return examples(*length, example)

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