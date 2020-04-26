import trio
import triogram
import attr

from .logging import configure_logging
from .root_handler import RootHandler


def new(config):
    bot = triogram.make_bot(config.TOKEN)
    configure_logging(config)
    root_handler = RootHandler(bot, config)
    return App(bot, root_handler)


@attr.s
class App:

    bot = attr.ib()
    root_handler = attr.ib()

    async def run(self):
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.bot)
            nursery.start_soon(self.root_handler)

    __call__ = run
