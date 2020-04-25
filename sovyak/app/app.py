import trio
import triogram
import attr

from .logging import configure_logging
from .new_game_handler import NewGameHandler


def new(config):
    bot = triogram.make_bot(config.TOKEN)
    configure_logging(config)
    new_game_handler = NewGameHandler(bot, config)
    return App(bot, new_game_handler)


@attr.s
class App:

    bot = attr.ib()
    new_game_handler = attr.ib()

    async def run(self):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.bot)
            nursery.start_soon(self.new_game_handler)

    __call__ = run
