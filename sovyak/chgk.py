import random
from typing import List

import attr


@attr.s(auto_attribs=True)
class Question:

    text: str
    answer: str


@attr.s(auto_attribs=True)
class Theme:

    info: str
    questions: List[Question] = attr.Factory(list)


@attr.s(auto_attribs=True)
class Pack:

    name: str
    themes: List[Theme] = attr.Factory(list)

    def sample(self, n: int) -> "Pack":
        name = f"{self.name} - sample {n}/{len(self.themes)}"
        themes = random.sample(self.themes, n)
        return Pack(name, themes)
