from dataclasses import dataclass
from typing import Dict, List
from units import scientific

from value import Value
from data import default, now
import uuid


@dataclass
class Question:
    values: List[Value]
    question: str = ""
    answer: float = 0.0
    quality: float = 0.0
    measurement: str = ""
    generated: str = default(now)
    style: str = ""
    qid: str = ""

    def __post_init__(self):
        if not self.measurement:
            self.measurement = self.values[0].measurement
        if not self.qid:
            self.qid = uuid.uuid4().hex

    def key(self):
        return (self.style, *[value.key() for value in self.values])

    # def to_prompt(self):
    #     answer = scientific(self.larger.value / self.smaller.value, 2)
    #     return f"{self.smaller.called}: {self.smaller.value_string()}\n{self.larger.called}: {self.larger.value_string()}\n{self.smaller.called} < {self.larger.called}"

    def serialize(self):
        return {
            "values": [value.serialize() for value in self.values],
            "question": self.question,
            "answer": self.answer,
            "measurement": self.measurement,
            "quality": self.quality,
            "generated": self.generated,
            "style": self.style,
            "id": self.qid,
        }

    @staticmethod
    def deserialize(data: Dict):
        return Question(
            [Value.deserialize(value) for value in data["values"]],
            answer=data["answer"],
            question=data["question"].removeprefix("Q: "),
            measurement=data.get("measurement", ""),
            quality=data.get("quality", 0.0),
            generated=data["generated"],
            style=data["style"],
            qid=data.get("id", ""),
        )

    def to_messages(self, include_question=True):
        messages = []
        user_content = self.to_prompt()
        # user_content = f"{self.smaller.to_string('smaller')}\n{self.larger.to_string('larger')}"
        # user_content = f"1. {self.smaller.to_string()}\n2. {self.larger.to_string()}"
        # user_content = json.dumps([self.smaller.to_dict(), self.larger.to_dict()])
        messages.append({"role": "user", "content": user_content})
        if include_question and self.question:
            messages.append({"role": "assistant", "content": f"Q: {self.question}"})
        return messages
