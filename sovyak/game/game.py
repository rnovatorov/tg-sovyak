import collections
import contextlib

import attr
import trio

from sovyak import package

from .receiver import Receiver
from .messages import Review, Pass, Answer
from .players import Players


async def new(bot, config, chat):
    players = Players.from_id_list(config.CHAT_MEMBERS)

    pack = await package.chgk_db.download(config.PACK)
    if config.PACK_SAMPLE is not None:
        pack = pack.sample(config.PACK_SAMPLE)

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
        await self.announce_pack()

        for theme in self.pack.themes:
            await self.announce_theme(theme)

            for n, question in enumerate(theme.questions, start=1):
                self.players.reset_state()
                await self.round(question, points=n)

        winner = self.determine_winner()
        await self.announce_winner(winner)

    def determine_winner(self):
        return max(self.players, key=lambda player: player.score)

    async def round(self, question, points):
        async with trio.open_nursery() as nursery, self.receive_messages() as messages:
            await self.announce_question(question)

            queue = collections.deque()

            async def prohibit_answers_after_timeout():
                await trio.sleep(self.round_duration)
                await self.players.prohibit_answers()

            nursery.start_soon(prohibit_answers_after_timeout)

            while not await self.players.are_done():
                message = await messages.receive(timeout=1)

                if isinstance(message, Review):
                    message.sender.reviewee.score += message.sign * points
                    message.sender.reviewee = None

                elif isinstance(message, Pass):
                    message.sender.can_answer = False

                elif isinstance(message, Answer):
                    queue.append((question, message))
                    message.sender.can_answer = False

                self.process_answers(queue, nursery)

            nursery.cancel_scope.cancel()

        await self.announce_answer(question)
        await self.announce_score()

    def process_answers(self, queue, nursery):
        for _ in range(len(queue)):
            question, answer = queue.pop()
            reviewer = self.players.choose_reviewer(answer)
            if reviewer is None:
                queue.appendleft((question, answer))
                continue

            reviewer.reviewee = answer.sender
            nursery.start_soon(self.ask_for_review, reviewer, question, answer)

    async def ask_for_review(self, reviewer, question, answer):
        text = f"Ответ игрока: {answer.text}\nПравильный {question.answer}"
        reply_markup = {
            "keyboard": [[Review.POSITIVE, Review.NEGATIVE]],
            "one_time_keyboard": True,
            "resize_keyboard": True,
        }
        await self.send(reviewer, text, reply_markup=reply_markup)

    @contextlib.asynccontextmanager
    async def receive_messages(self):
        async with self.bot.sub(
            lambda u: "message" in u
            and "text" in u["message"]
            and u["message"]["from"]["id"] in self.players
        ) as updates:
            yield Receiver(updates, self.players)

    async def announce_pack(self):
        text = f"Пакет: {self.pack.name}"
        await self.broadcast(text)

    async def announce_theme(self, theme):
        text = f"Тема: {theme.info}"
        await self.broadcast(text)

    async def announce_question(self, question):
        text = f"Вопрос: {question.text}"
        reply_markup = {
            "keyboard": [[Pass.PATTERN]],
            "one_time_keyboard": True,
            "resize_keyboard": True,
        }
        await self.broadcast(text, reply_markup=reply_markup)

    async def announce_answer(self, question):
        text = f"Ответ: {question.answer}"
        await self.broadcast(text)

    async def announce_score(self):
        text = "Счёт:\n" + "\n".join(
            f"- {player.id}: {player.score}" for player in self.players
        )
        await self.broadcast(text)

    async def announce_winner(self, winner):
        text = f"Победил {winner.id} со счётом {winner.score}"
        reply_markup = {"remove_keyboard": True}
        await self.broadcast(text, reply_markup=reply_markup)

    async def broadcast(self, text, **kwargs):
        async with trio.open_nursery() as nursery:
            for player in self.players:
                nursery.start_soon(lambda: self.send(player, text, **kwargs))

    async def send(self, player, text, **kwargs):
        await self.bot.api.send_message(
            json={"chat_id": player.id, "text": text, **kwargs}
        )
