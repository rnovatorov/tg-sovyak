import trio
import triogram

from .logging import configure_logging
from .new_game_handler import NewGameHandler


def make(config):
    bot = triogram.make_bot(config.TOKEN)
    configure_logging(config)
    new_game_handler = NewGameHandler(bot, config)

    async def app():
        async with trio.open_nursery() as nursery:
            nursery.start_soon(bot)
            nursery.start_soon(new_game_handler)

    return app
