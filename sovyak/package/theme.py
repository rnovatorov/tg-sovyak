from typing import List

import attr

from .question import Question


@attr.s(auto_attribs=True)
class Theme:

    info: str
    questions: List[Question] = attr.Factory(list)
