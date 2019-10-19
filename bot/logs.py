import logging


def configure_triogram(level):
    logger = logging.getLogger("triogram")
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter("%(asctime)s %(name)s %(request_id)s %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def configure_bot(level):
    logger = logging.getLogger("bot")
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
