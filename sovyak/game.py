import re
import collections

import attr
import trio

from . import utils


@attr.s
class Base:

    _bot = attr.ib()
    _players = attr.ib()

    async def _wait(self) -> str:
        return await self._bot.wait(self._new_message)

    async def _sub(self) -> str:
        return self._bot.sub(self._new_message)

    def _new_message(self, u):
        return "message" in u and u["message"]["from"]["id"] in self._players

    async def _send(self, player: str, text: str):
        await self._bot.api.send_message(json={"chat_id": player, "text": text})

    async def _broadcast(self, text: str):
        async with trio.open_nursery() as nursery:
            for player in self._players:
                nursery.start_soon(self._send, player, text)


@attr.s
class Game(Base):

    RE_POSITIVE_REVIEW = re.compile(r"\+")
    RE_PASS = re.compile(r"pass")

    pack = attr.ib()

    score = attr.ib(factory=collections.Counter)
    round_duration = attr.ib(default=10)
    reviewers = attr.ib(factory=dict)
    workers = attr.ib(factory=set)
    queue = attr.ib(factory=list)

    async def start(self):
        await self._broadcast(self.pack.name)

        for theme in self.pack.themes:
            for points, question in enumerate(theme.questions):
                await self.round(question, points)

        (winner, score), = self.score.most_common(1)
        await self._broadcast(f"{winner}: {score}")

    __call__ = start

    async def timer(self, task_status=trio.TASK_STATUS_IGNORED):
        timeout = trio.Event()
        task_status.started(timeout)
        await trio.sleep(self.round_duration)
        timeout.set()

    async def round(self, question, points):
        # Ask question
        await self._broadcast(question.text)

        # Start handling updates
        async with trio.open_nursery() as nursery, self._sub() as us:
            # Start timer
            timeout = await nursery.start(self.timer)

            # Process updates
            while not timeout.is_set() or self.reviewers or self.queue:
                # Get next update
                u = await utils.aiter(us)
                sender, text = u["message"]["from"]["id"], u["message"]["text"]

                # Handle review
                if sender in self.reviewers:
                    reviewed = self.reviewers.pop(sender)
                    positive = self.RE_POSITIVE_REVIEW.match(text) is not None
                    delta = points if positive else -points
                    self.score[reviewed] += delta
                    self.workers.update({sender, reviewed})

                # Handle pass
                elif self.RE_PASS.match(text) is not None:
                    self.workers.add(sender)

                # Handle answer
                elif not timeout.is_set():
                    self.queue.append((sender, text))

                # Process queue
                if self.queue and self.workers:
                    reviewed, text = self.queue.pop()
                    reviewer = self.workers.pop()
                    self.reviewers[reviewer] = reviewed
                    await self._send(reviewer, f"{question.answer} {text}")

        # Reveal answer
        await self._broadcast(question.answer)

        # Show score
        await self._broadcast(str(self.score))
