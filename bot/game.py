import re
import logging
import collections

import attr
import trio


@attr.s
class Adapter:

    _bot = attr.ib()
    players = attr.ib()

    def sub(self):
        return self._bot.sub(self._new_message)

    def _new_message(self, u):
        return "message" in u and u["message"]["from"]["id"] in self.players

    async def send(self, player: str, text: str):
        await self._bot.api.send_message(json={"chat_id": player, "text": text})

    async def broadcast(self, text: str):
        async with trio.open_nursery() as nursery:
            for player in self.players:
                nursery.start_soon(self.send, player, text)


@attr.s
class Game:

    RE_POSITIVE_REVIEW = re.compile(r"\+")
    RE_PASS = re.compile(r"pass")

    _adapter = attr.ib()
    pack = attr.ib()

    logger = attr.ib(factory=lambda: logging.getLogger(__name__))

    score = attr.ib(factory=collections.Counter)
    round_duration = attr.ib(default=10)
    reviewers = attr.ib(factory=dict)
    workers = attr.ib(factory=set)
    queue = attr.ib(factory=list)

    async def start(self):
        self.logger.info("started")

        self.logger.info("pack name: %s", self.pack.name)
        await self._adapter.broadcast(self.pack.name)

        if not self.score:
            for player in self._adapter.players:
                self.score[player] = 0

        for theme in self.pack.themes:
            self.logger.info("theme info: %s", theme.info)
            await self._adapter.broadcast(theme.info)

            for i, question in enumerate(theme.questions, start=1):
                self.logger.info("question: %d", i)
                await self.round(question, points=100 * i)

        (winner, score), = self.score.most_common(1)
        await self._adapter.broadcast(f"{winner}: {score}")

        self.logger.info("finished, winner: %s with %d", winner, score)

    __call__ = start

    @staticmethod
    async def timer(duration, task_status=trio.TASK_STATUS_IGNORED):
        timeout = trio.Event()
        task_status.started(timeout)
        await trio.sleep(duration)
        timeout.set()

    async def round(self, question, points):
        self.logger.info("round started")

        # Ask question
        self.logger.info("question text: %s", question.text)
        await self._adapter.broadcast(question.text)

        # Start handling updates
        async with trio.open_nursery() as nursery:
            # Start timer
            timeout = await nursery.start(self.timer, self.round_duration)

            # Process updates
            self.logger.debug("start processing updates")
            updates = self._adapter.sub()

            while not timeout.is_set() or self.reviewers or self.queue:
                self.logger.debug("timeout is set: %s", timeout.is_set())
                self.logger.debug("reviewers: %s", self.reviewers)
                self.logger.debug("queue: %s", self.queue)

                # Get next update
                with trio.move_on_after(1) as cancel_scope:
                    self.logger.debug("waiting for an update...")
                    u = await updates.receive()
                    self.logger.debug("got update: %s", u)

                if cancel_scope.cancelled_caught:
                    self.logger.debug("got nothing")
                    u = None

                if u is not None:
                    self.logger.debug("processing update")
                    sender, text = u["message"]["from"]["id"], u["message"]["text"]

                    # Handle review
                    if sender in self.reviewers:
                        self.logger.debug("handling as review")
                        reviewed = self.reviewers.pop(sender)
                        positive = self.RE_POSITIVE_REVIEW.match(text) is not None
                        delta = points if positive else -points
                        self.score[reviewed] += delta
                        self.workers.update({sender, reviewed})

                    # Handle pass
                    elif self.RE_PASS.match(text) is not None:
                        self.logger.debug("handling as pass")
                        self.workers.add(sender)

                    # Handle answer
                    elif not timeout.is_set():
                        self.logger.debug("handling as answer")
                        self.queue.append((sender, text))

                # Process queue
                if self.queue and self.workers:
                    self.logger.debug("processing queue")
                    reviewed, text = self.queue.pop()
                    reviewer = self.workers.pop()
                    self.reviewers[reviewer] = reviewed
                    await self._adapter.send(reviewer, f"{question.answer} {text}")

        # Reveal answer
        await self._adapter.broadcast(question.answer)

        # Show score
        await self._adapter.broadcast(str(self.score))
