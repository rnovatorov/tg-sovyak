import re
import logging

import attr
import trio


log = logging.getLogger(__name__)


@attr.s
class Receiver:

    updates = attr.ib()
    players = attr.ib()

    async def receive(self, *, timeout):
        update = None
        with trio.move_on_after(timeout):
            log.debug("waiting for a message...")
            update = await self.updates.receive()

        log.debug("update: %s", update)
        if update is None:
            return update

        sender, text = self.parse(update)
        return self.classify(sender, text)

    def parse(self, update):
        sender = self.players.by_id(update["message"]["from"]["id"])
        log.debug("sender: %s", sender)

        text = update["message"]["text"]
        log.debug("text: %s", text)

        return sender, text

    def classify(self, sender, text):
        if sender.reviewee is not None:
            try:
                return Review.parse(sender, text)
            except TypeError:
                return Spam(sender, text)

        try:
            return Pass.parse(sender, text)
        except TypeError:
            pass

        if sender.can_answer:
            return Answer(sender, text)

        return Spam(sender, text)


@attr.s
class Message:

    sender = attr.ib()
    text = attr.ib()


@attr.s
class Review(Message):

    RE_POSITIVE = re.compile(r"\+")
    RE_NEGATIVE = re.compile(r"-")

    sign = attr.ib()

    @classmethod
    def parse(cls, sender, text):
        if cls.RE_POSITIVE.match(text) is not None:
            return cls(sender, text, sign=1)

        if cls.RE_NEGATIVE.match(text) is not None:
            return cls(sender, text, sign=-1)

        raise TypeError("not a Review")


class Spam(Message):
    pass


class Pass(Message):

    RE = re.compile(r"-")

    @classmethod
    def parse(cls, sender, text):
        if cls.RE.match(text) is not None:
            return cls(sender, text)

        raise TypeError("not a Pass")


class Answer(Message):
    pass
