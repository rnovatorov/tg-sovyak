import trio

from sovyak import factory, config

if __name__ == "__main__":
    bot = factory.make_bot(config)
    trio.run(bot)
