import collections

import attr
import trio


@attr.s
class Base:

    bot = attr.ib()
    players = attr.ib()

    async def wait(self) -> str:
        return await self.bot.wait(self._new_message)

    async def sub(self) -> str:
        return self.bot.sub(self._new_message)

    def _new_message(self, update):
        return "message" in update and update["message"]["from"]["id"] in self.players

    async def send(self, player: str, text: str):
        await self.bot.api.send_message(json={"chat_id": player, "text": text})

    async def broadcast(self, text: str):
        async with trio.open_nursery() as nursery:
            for player in self.players:
                nursery.start_soon(self.send, player, text)


@attr.s
class Game(Base):

    pack = attr.ib()
    score = attr.ib(factory=collections.Counter)
    round_duration = attr.ib(default=10)

    reviewers = attr.ib(factory=dict)
    workers = attr.ib(factory=set)
    queue = attr.ib(factory=list)

    async def __call__(self):
        for theme in self.pack.themes:
            for points, question in enumerate(theme.questions):
                await self.round(question, points)

    def get_sender(self, update):
        return update["message"]["from"]["id"]

    def get_text(self, update):
        return update["message"]["text"]

    def is_review(self, update):
        return self.get_sender(update) in self.reviewers

    def review_is_positive(self, update):
        return "+" in self.get_text(update)

    def is_pass(self, update):
        return "pass" in self.get_text(update)

    async def round(self, question, points):
        await self.broadcast(question.text)

        timeout = trio.Event()

        async def timer():
            await trio.sleep(self.round_duration)
            timeout.set()

        async with trio.open_nursery() as nursery, self.sub() as updates:
            nursery.start_soon(timer)

            async for update in updates:
                while not timeout.is_set() or self.reviewers or self.queue:
                    if self.is_review(update):
                        reviewer = self.get_sender(update)
                        reviewed = self.reviewers.pop(reviewer)
                        delta = points if self.review_is_positive(update) else -points
                        self.score[reviewed] += delta
                        self.workers.update({reviewer, reviewed})

                    elif self.is_pass(update):
                        worker = self.get_sender(update)
                        self.workers.add(worker)

                    elif not timeout.is_set():
                        self.queue.append(update)

                    if self.queue and self.workers:
                        update = self.queue.pop()
                        reviewer = self.workers.pop()
                        reviewed = self.get_sender(update)
                        self.reviewers[reviewer] = reviewed
                        await self.send(
                            reviewer, f"{question.answer} {self.get_text(update)}"
                        )

        await self.broadcast(question.answer)
        await self.broadcast(str(self.score))
