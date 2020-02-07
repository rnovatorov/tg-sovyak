import trio

from . import sovyak, config


if __name__ == "__main__":
    bot = sovyak.make_bot(config)
    trio.run(bot)
