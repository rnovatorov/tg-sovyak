import logging

import trio
import triogram

from . import config, handlers


async def run():
    bot = triogram.make_bot(config.TOKEN)

    configure_triogram_logger()
    configure_sovyak_logger()

    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        handlers.start_all(nursery, bot)


def configure_triogram_logger(level=logging.DEBUG):
    logger = logging.getLogger("triogram")
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter("%(asctime)s %(name)s %(request_id)s %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def configure_sovyak_logger(level=logging.DEBUG):
    logger = logging.getLogger("sovyak")
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
