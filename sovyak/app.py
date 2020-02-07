import trio
import triogram

from . import handlers, logs


def make_app(config):
    bot = triogram.make_bot(config.TOKEN)

    logs.configure_triogram(config.TRIOGRAM_LOGGING_LEVEL)
    logs.configure_bot(config.BOT_LOGGING_LEVEL)

    new_game_handler = handlers.NewGameHandler(bot)

    async def app():
        async with trio.open_nursery() as nursery:
            nursery.start_soon(bot)
            nursery.start_soon(new_game_handler)

    return app
