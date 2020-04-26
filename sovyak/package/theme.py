from typing import List

import attr

from .question import Question


@attr.s(auto_attribs=True, repr=False)
class Theme:

    info: str
    questions: List[Question] = attr.Factory(list)

    def __repr__(self):
        return f"{type(self).__name__}({self.info!r})"

    def __len__(self):
        return len(self.questions)

    def __iter__(self):
        return iter(self.questions)
