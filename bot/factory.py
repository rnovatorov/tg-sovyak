import trio
import triogram

from . import handlers, logs


def make_bot(config):
    bot = triogram.make_bot(config.TOKEN)

    logs.configure_triogram(config.TRIOGRAM_LOGGING_LEVEL)
    logs.configure_bot(config.BOT_LOGGING_LEVEL)

    async def run():
        async with trio.open_nursery() as nursery:
            nursery.start_soon(bot)
            handlers.start_all(nursery, bot)

    return run
