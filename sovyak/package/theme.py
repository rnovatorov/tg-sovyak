from typing import List

import attr

from .question import Question


@attr.s(auto_attribs=True)
class Theme:

    info: str
    questions: List[Question] = attr.Factory(list)

    def __len__(self):
        return len(self.questions)

    def __iter__(self):
        return iter(self.questions)
