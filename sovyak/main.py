import trio

from . import app, config


def main():
    trio.run(app.make(config))
