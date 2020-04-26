import trio

import sovyak


def main():
    app = sovyak.app.new(sovyak.config)
    trio.run(app)


if __name__ == "__main__":
    main()
