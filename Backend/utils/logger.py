import logging
from config import settings


def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with the specified name"""
    logger = logging.getLogger(name)

    if settings.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Only add handler if none exists (to prevent duplicate logs)
    if not logger.handlers:
        handler = logging.StreamHandler()

        if settings.DEBUG:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        else:
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
