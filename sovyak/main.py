import trio

from sovyak import app, config


def main():
    trio.run(app.new(config))
