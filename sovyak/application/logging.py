import logging


def configure_logging(config):
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger("triogram")
    logger.setLevel(config.TRIOGRAM_LOG_LEVEL)
    logger.addHandler(handler)
