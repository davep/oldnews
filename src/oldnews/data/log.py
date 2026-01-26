"""Provides the application's logger."""

##############################################################################
# Python imports.
from logging import DEBUG, INFO, Formatter, Logger, getLogger
from logging.handlers import RotatingFileHandler
from os import getenv

##############################################################################
# Local imports.
from .locations import data_dir


##############################################################################
class Log:
    """The application log."""

    _logger: Logger | None = None
    """The Python logger object."""

    def __new__(cls) -> Logger:
        """Create or return the logger.

        Returns:
            A configured Python logger.
        """
        if cls._logger is None:
            cls._logger = cls._initialise_logger()
        return cls._logger

    @staticmethod
    def _initialise_logger() -> Logger:
        """Configure the application logger.

        Returns:
            A configured `Logger` object.
        """
        logger = getLogger("oldnews")
        logger.setLevel(DEBUG if getenv("OLDNEWS_DEBUG") else INFO)
        file_handler = RotatingFileHandler(
            data_dir() / "oldnews.log", maxBytes=1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(
            Formatter(
                "%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
            )
        )
        logger.addHandler(file_handler)
        return logger


### log.py ends here
