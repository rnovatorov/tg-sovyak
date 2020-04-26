import attr
import trio

from .messages import Review, Spam, Pass, Answer


@attr.s
class Receiver:

    updates = attr.ib()
    players = attr.ib()

    async def receive(self, *, timeout):
        update = None
        with trio.move_on_after(timeout):
            update = await self.updates.receive()

        if update is None:
            return update

        sender, text = self.parse(update)
        return self.classify(sender, text)

    def parse(self, update):
        sender = self.players.by_id(update["message"]["from"]["id"])
        text = update["message"]["text"]
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
