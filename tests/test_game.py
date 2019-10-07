import trio
import attr

from triogram import dispatcher as _dispatcher

from sovyak import game as _game, models
from sovyak.bot import configure_sovyak_logger


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


async def test_sanity():
    configure_sovyak_logger()
    bot = Bot()
    players = {"Alice", "Bob"}
    adapter = _game.Adapter(bot, players)
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
    game = _game.Game(adapter, pack, round_duration=5)
    async with trio.open_nursery() as nursery:
        nursery.start_soon(game)
        await trio.sleep(2)
        await bot.pub(message_from("Bob", "Bob's 1-st answer"))
        await bot.pub(message_from("Alice", "pass"))
