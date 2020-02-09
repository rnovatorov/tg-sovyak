import collections
import logging
import contextlib

import attr
import trio

from . import msg, play, pacman


log = logging.getLogger(__name__)


async def new(bot, config, chat):
    players = play.Ers.from_id_list(config.CHAT_MEMBERS)
    pack = await pacman.download(config.PACK)
    return Game(
        bot=bot, players=players, pack=pack, round_duration=config.ROUND_DURATION,
    )


@attr.s
class Game:

    bot = attr.ib()
    players = attr.ib()
    pack = attr.ib()
    round_duration = attr.ib()

    async def run(self):
        await self.anounce_pack()

        for theme in self.pack.themes:
            await self.anounce_theme(theme)

            for n, question in enumerate(theme.questions, start=1):
                self.players.reset_state()
                await self.round(question, points=n)

        winner = self.determine_winner()
        await self.anounce_winner(winner)

    def determine_winner(self):
        return max(self.players, key=lambda player: player.score)

    async def round(self, question, points):
        async with trio.open_nursery() as nursery, self.receive_messages() as messages:
            await self.anounce_question(question)

            mutex = trio.Lock()
            queue = collections.deque()

            async def prohibit_answers_after_timeout():
                await trio.sleep(self.round_duration)

                async with mutex:
                    for player in self.players:
                        player.can_answer = False

            nursery.start_soon(prohibit_answers_after_timeout)

            while not self.players.are_done:
                async with mutex:
                    message = await messages.receive(timeout=1)

                    if message is not None:
                        if isinstance(message, msg.Review):
                            message.sender.reviewee.score += message.sign * points
                            message.sender.reviewee = None

                        elif isinstance(message, msg.Pass):
                            message.sender.can_answer = False

                        elif isinstance(message, msg.Answer):
                            queue.append((question, message))
                            message.sender.can_answer = False

                    self.process_answers(queue, nursery)

            nursery.cancel_scope.cancel()

        await self.anounce_answer(question)
        await self.anounce_score()

    def process_answers(self, queue, nursery):
        for _ in range(len(queue)):
            question, answer = queue.pop()
            reviewer = self.players.choose_reviewer(answer)
            if reviewer is None:
                queue.appendleft((question, answer))
                continue

            reviewer.reviewee = answer.sender
            nursery.start_soon(self.send, reviewer, f"{answer.text} {question.answer}")

    @contextlib.asynccontextmanager
    async def receive_messages(self):
        async with self.bot.sub(
            lambda u: "message" in u
            and "text" in u["message"]
            and u["message"]["from"]["id"] in self.players
        ) as updates:
            yield msg.Receiver(updates, self.players)

    async def anounce_pack(self):
        log.info("pack name: %s", self.pack.name)
        await self.broadcast(self.pack.name)

    async def anounce_theme(self, theme):
        log.info("theme info: %s", theme.info)
        await self.broadcast(theme.info)

    async def anounce_question(self, question):
        log.info("question: %s", question)
        await self.broadcast(question.text)

    async def anounce_answer(self, question):
        await self.broadcast(question.answer)

    async def anounce_score(self):
        text = "\n".join(f"{player.id}: {player.score}" for player in self.players)
        await self.broadcast(text)

    async def anounce_winner(self, winner):
        log.info("winner: %s", winner)
        await self.broadcast(f"{winner.id}: {winner.score}")

    async def broadcast(self, text: str):
        async with trio.open_nursery() as nursery:
            for player in self.players:
                nursery.start_soon(self.send, player, text)

    async def send(self, player, text):
        await self.bot.api.send_message(json={"chat_id": player.id, "text": text})
