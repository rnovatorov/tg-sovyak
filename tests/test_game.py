import attr
import trio
import pytest
from triogram import dispatcher as _dispatcher

from bot import logs, game, models


@attr.s
class Api:
    def __getattr__(self, method_name):
        async def method(*_, **kwargs):
            print(f"api: {method_name} {kwargs}")

        return method


@attr.s
class Bot:

    dispatcher = attr.ib(factory=_dispatcher.Dispatcher)
    api = attr.ib(factory=Api)

    @property
    def sub(self):
        return self.dispatcher.sub

    @property
    def pub(self):
        return self.dispatcher.pub


def message_from(id_, text):
    return {"message": {"from": {"id": id_}, "text": text}}


@pytest.mark.skip("not implemented")
async def test_sanity():
    logs.configure_bot("DEBUG")
    bot = Bot()
    players = {"Alice", "Bob"}
    pack = models.Pack(
        name="Test pack",
        themes=[
            models.Theme(
                info=f"Theme {t}",
                questions=[
                    models.Question(text=f"Question {q}", answer=f"Answer {q}")
                    for q in range(1, 4)
                ],
            )
            for t in range(1, 2)
        ],
    )
    g = game.Game(bot=bot, players=players, pack=pack, round_duration=5)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(g)

        # Answer + Review before end of round
        await trio.sleep(1)
        await bot.pub(message_from("Bob", "answer"))
        await bot.pub(message_from("Alice", "pass"))
        await trio.sleep(2)
        await bot.pub(message_from("Alice", "+"))
        await trio.sleep(2)

        # Positive review not on time, two answers, two reviews
        await trio.sleep(1)
        await bot.pub(message_from("Alice", "answer"))
        await bot.pub(message_from("Alice", "+"))
        await trio.sleep(1)
        await bot.pub(message_from("Bob", "answer"))
        await trio.sleep(1)
        await bot.pub(message_from("Alice", "+"))
        await bot.pub(message_from("Bob", "-"))
        await trio.sleep(2)
