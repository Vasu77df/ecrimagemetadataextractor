import logging
import sys


def init_logger(log_level=logging.INFO) -> None:
    """
    Init a logger called 'ecrimagemetadataextractor',
    modules in the project can getLogger this namespace
    """
    log_group = "ecrimagemetadataextractor"

    logger = logging.getLogger(log_group)

    logger.setLevel(log_level)

    if not logger.hasHandlers():
        # print to console
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(levelname)s -- %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)
