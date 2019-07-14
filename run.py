import trio

from sovyak import bot


if __name__ == "__main__":
    trio.run(bot.run)
