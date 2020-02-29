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

            queue = collections.deque()

            async def prohibit_answers_after_timeout():
                await trio.sleep(self.round_duration)
                await self.players.prohibit_answers()

            nursery.start_soon(prohibit_answers_after_timeout)

            while not await self.players.are_done():
                message = await messages.receive(timeout=1)

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
            nursery.start_soon(self.ask_for_review, reviewer, question, answer)

    async def ask_for_review(self, reviewer, question, answer):
        text = f"Ответ игрока: {answer.text}\nПравильный {question.answer}"
        reply_markup = {
            "keyboard": [[msg.Review.POSITIVE, msg.Review.NEGATIVE]],
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
            yield msg.Receiver(updates, self.players)

    async def anounce_pack(self):
        log.info("pack name: %s", self.pack.name)
        await self.broadcast(self.pack.name)

    async def anounce_theme(self, theme):
        log.info("theme info: %s", theme.info)
        await self.broadcast(theme.info)

    async def anounce_question(self, question):
        reply_markup = {
            "keyboard": [[msg.Pass.PATTERN]],
            "one_time_keyboard": True,
            "resize_keyboard": True,
        }
        log.info("question: %s", question)
        await self.broadcast(question.text, reply_markup=reply_markup)

    async def anounce_answer(self, question):
        await self.broadcast(question.answer)

    async def anounce_score(self):
        text = "\n".join(f"{player.id}: {player.score}" for player in self.players)
        await self.broadcast(text)

    async def anounce_winner(self, winner):
        log.info("winner: %s", winner)
        reply_markup = {"remove_keyboard": True}
        await self.broadcast(f"{winner.id}: {winner.score}", reply_markup=reply_markup)

    async def broadcast(self, text, **kwargs):
        async with trio.open_nursery() as nursery:
            for player in self.players:
                nursery.start_soon(lambda: self.send(player, text, **kwargs))

    async def send(self, player, text, **kwargs):
        await self.bot.api.send_message(
            json={"chat_id": player.id, "text": text, **kwargs}
        )
