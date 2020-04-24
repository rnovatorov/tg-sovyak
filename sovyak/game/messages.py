import attr


@attr.s
class Message:

    sender = attr.ib()
    text = attr.ib()


@attr.s
class Review(Message):

    POSITIVE = "+"
    NEGATIVE = "-"

    sign = attr.ib()

    @classmethod
    def parse(cls, sender, text):
        if text.strip() == cls.POSITIVE:
            return cls(sender, text, sign=1)

        if text.strip() == cls.NEGATIVE:
            return cls(sender, text, sign=-1)

        raise TypeError("not a Review")


class Spam(Message):
    pass


class Pass(Message):

    PATTERN = "-"

    @classmethod
    def parse(cls, sender, text):
        if text.strip() == cls.PATTERN:
            return cls(sender, text)

        raise TypeError("not a Pass")


class Answer(Message):
    pass
