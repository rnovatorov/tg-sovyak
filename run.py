import trio

import sovyak, config


if __name__ == "__main__":
    app = sovyak.make_app(config)
    trio.run(app)
