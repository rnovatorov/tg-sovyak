import logging

import trio
import triogram

from . import handlers


def make_app(config):
    bot = triogram.make_bot(config.TOKEN)
    configure_logging(config)
    new_game_handler = handlers.NewGame(bot, config)

    async def app():
        async with trio.open_nursery() as nursery:
            nursery.start_soon(bot)
            nursery.start_soon(new_game_handler)

    return app


def configure_logging(config):
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger("sovyak")
    logger.setLevel(config.LOG_LEVEL)
    logger.addHandler(handler)

    logger = logging.getLogger("triogram")
    logger.setLevel(config.TRIOGRAM_LOG_LEVEL)
    logger.addHandler(handler)
