"""Provides a tool to reset all the data."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Local imports.
from .locations import data_dir


##############################################################################
def reset_data(logout: bool) -> None:
    """Erase all the data.

    Args:
        logout: Should any token file be removed too?
    """
    to_remove: list[Path] = []
    for pattern in (
        "*.db",
        "*.db-shm",
        "*.db-wal",
        "*.log",
        *((".token",) if logout else ()),
    ):
        to_remove.extend(data_dir().glob(pattern))
    for data_file in to_remove:
        data_file.unlink()


### reset.py ends here
