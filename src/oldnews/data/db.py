"""Code for working with the backend database."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# TypeDAL imports.
from typedal import TypeDAL

##############################################################################
# Local imports.
from .locations import data_dir
from .navigation_state import NavigationState


##############################################################################
def db_file() -> Path:
    """Get the file that contains the database.

    Returns:
        The file that contains the database.
    """
    return data_dir() / "oldnews.db"


##############################################################################
def initialise_database() -> TypeDAL:
    """Create the database.

    Returns:
        The database.
    """
    dal = TypeDAL(f"sqlite://{db_file()}", folder=data_dir())
    dal.define(NavigationState)
    return dal


### db.py ends here
