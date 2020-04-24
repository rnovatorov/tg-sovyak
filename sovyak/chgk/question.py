import attr


@attr.s(auto_attribs=True)
class Question:

    text: str
    answer: str
