import trio
import triogram

from . import handlers, logs


def make_app(config):
    bot = triogram.make_bot(config.TOKEN)
    logs.configure(config)
    new_game_handler = handlers.NewGame(bot, config)

    async def app():
        async with trio.open_nursery() as nursery:
            nursery.start_soon(bot)
            nursery.start_soon(new_game_handler)

    return app
