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
