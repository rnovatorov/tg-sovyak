import collections
import logging
import re

import attr
import trio


@attr.s
class Game:

    RE_POSITIVE_REVIEW = re.compile(r"\+")
    RE_NEGATIVE_REVIEW = re.compile(r"-")
    RE_PASS = re.compile(r"-")

    bot = attr.ib()
    players = attr.ib()
    pack = attr.ib()

    round_duration = attr.ib(default=10)
    score = attr.ib(factory=collections.Counter)
    logger = attr.ib(factory=lambda: logging.getLogger(__name__))

    async def start(self):
        self.logger.info("started")

        self.logger.info("pack name: %s", self.pack.name)
        await self.broadcast(self.pack.name)

        if not self.score:
            for player in self.players:
                self.score[player] = 0

        for theme in self.pack.themes:
            self.logger.info("theme info: %s", theme.info)
            await self.broadcast(theme.info)

            for i, question in enumerate(theme.questions, start=1):
                self.logger.info("question: %d", i)
                await self.round(question, points=i)

        (winner, score), = self.score.most_common(1)
        await self.broadcast(f"{winner}: {score}")

        self.logger.info("finished, winner: %s with %d", winner, score)

    __call__ = start

    async def round(self, question, points):
        self.logger.info("round started: %d", points)

        # Ask question
        self.logger.info("question text: %s", question.text)
        await self.broadcast(question.text)

        # Start handling updates
        async with trio.open_nursery() as nursery, self.sub() as updates:
            reviewers = {}
            answered = set()
            workers = set()
            queue = collections.deque()

            # Start timer
            timeout = await nursery.start(self.timer, self.round_duration)

            # Process updates
            self.logger.debug("start processing updates")

            while not timeout.is_set() or reviewers or queue:
                self.logger.debug("timeout: %s", timeout.is_set())
                self.logger.debug("reviewers: %s", reviewers)
                self.logger.debug("workers: %s", workers)
                self.logger.debug("queue: %s", queue)

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
                    if sender in reviewers:
                        self.logger.debug("handling as review")

                        mod = None
                        if self.RE_POSITIVE_REVIEW.match(text) is not None:
                            mod = 1
                        elif self.RE_NEGATIVE_REVIEW.match(text) is not None:
                            mod = -1

                        if mod is not None:
                            reviewed = reviewers.pop(sender)
                            self.score[reviewed] += mod * points
                            workers.add(sender)
                            if reviewed not in reviewers:
                                workers.add(reviewed)

                    # Handle pass
                    elif self.RE_PASS.match(text) is not None:
                        self.logger.debug("handling as pass")
                        workers.add(sender)

                    # Handle answer
                    elif sender not in answered and not timeout.is_set():
                        self.logger.debug("handling as answer")
                        queue.append((sender, text))
                        workers.add(sender)
                        answered.add(sender)

                # Process queue
                if queue:
                    self.logger.debug("processing queue")
                for _ in range(len(queue)):
                    reviewed, text = queue.pop()
                    for reviewer in workers - {reviewed}:
                        reviewers[reviewer] = reviewed
                        workers.remove(reviewer)
                        await self.send(reviewer, f"{question.answer} {text}")
                        break
                    else:
                        queue.appendleft((reviewed, text))

        # Reveal answer
        await self.broadcast(question.answer)

        # Show score
        await self.broadcast(str(self.score))

    @staticmethod
    async def timer(duration, task_status=trio.TASK_STATUS_IGNORED):
        timeout = trio.Event()
        task_status.started(timeout)
        await trio.sleep(duration)
        timeout.set()

    def sub(self):
        def new_message(u):
            return "message" in u and u["message"]["from"]["id"] in self.players

        return self.bot.sub(new_message)

    async def send(self, player: str, text: str):
        await self.bot.api.send_message(json={"chat_id": player, "text": text})

    async def broadcast(self, text: str):
        async with trio.open_nursery() as nursery:
            for player in self.players:
                nursery.start_soon(self.send, player, text)
