import logging


def configure(config):
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    configure_sovyak(config.LOG_LEVEL, formatter)
    configure_triogram(config.TRIOGRAM_LOG_LEVEL, formatter)


def configure_sovyak(level, formatter):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)

    logger = logging.getLogger("sovyak")
    logger.setLevel(level)
    logger.addHandler(handler)


def configure_triogram(level, formatter):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)

    logger = logging.getLogger("triogram")
    logger.setLevel(level)
    logger.addHandler(handler)
