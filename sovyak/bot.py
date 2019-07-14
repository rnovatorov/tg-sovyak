import logging

import trio
import triogram

from . import config, handlers


async def run():
    bot = triogram.make_bot(config.TOKEN)

    configure_logging()

    async with trio.open_nursery() as nursery:
        nursery.start_soon(bot)
        handlers.start_all(nursery, bot)


def configure_logging():
    # Triogram
    logger = logging.getLogger("triogram")
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(name)s %(request_id)s %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Sovyak
    logger = logging.getLogger("sovyak")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
