import trio

from sovyak import application, config


def main():
    app = application.new(config)
    trio.run(app)
