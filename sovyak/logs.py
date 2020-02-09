import logging


def configure(config):
    configure_sovyak(config.LOG_LEVEL)
    configure_triogram(config.TRIOGRAM_LOG_LEVEL)


def configure_sovyak(level):
    logger = logging.getLogger("sovyak")
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def configure_triogram(level):
    logger = logging.getLogger("triogram")
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)

    formatter = logging.Formatter("%(asctime)s %(name)s %(request_id)s %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
