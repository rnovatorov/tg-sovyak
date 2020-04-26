import random
from typing import List

import attr

from .theme import Theme


@attr.s(auto_attribs=True, repr=False)
class Pack:

    name: str
    themes: List[Theme] = attr.Factory(list)

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r}, themes={self.themes!r})"

    def __len__(self):
        return len(self.themes)

    def __iter__(self):
        return iter(self.themes)

    def sample(self, n: int) -> "Pack":
        name = f"{self.name} - sample {n}/{len(self.themes)}"
        themes = random.sample(self.themes, n)
        return Pack(name, themes)
