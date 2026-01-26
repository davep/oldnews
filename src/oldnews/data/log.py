"""Provides the application's logger."""

##############################################################################
# Python imports.
from functools import cache
from logging import DEBUG, INFO, Formatter, Logger, getLogger
from logging.handlers import RotatingFileHandler
from os import getenv

##############################################################################
# Local imports.
from .locations import data_dir


##############################################################################
def _build_logger() -> Logger:
    """Build a logger for the application.

    Returns:
        A configured `Logger` object.
    """
    logger = getLogger("oldnews")
    logger.setLevel(DEBUG if getenv("OLDNEWS_DEBUG") else INFO)
    file_handler = RotatingFileHandler(
        data_dir() / "oldnews.log", maxBytes=1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(
        Formatter("%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s")
    )
    logger.addHandler(file_handler)
    return logger


##############################################################################
Log = cache(_build_logger)
"""The application-wide logging object."""

### log.py ends here
