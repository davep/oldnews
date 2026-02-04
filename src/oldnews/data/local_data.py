"""Provides code for setting up the local database."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Tortoise imports.
from tortoise import Tortoise

##############################################################################
# Local imports.
from .locations import data_dir


##############################################################################
def local_db_file() -> Path:
    """Get the file that contains the database.

    Returns:
        The file that contains the database.
    """
    return data_dir() / "local.db"


##############################################################################
async def initialise_local_data() -> None:
    """Initialise the local storage."""
    await Tortoise.init(
        db_url=f"sqlite://{local_db_file()}",
        modules={"models": ["oldnews.data.models"]},
    )
    await Tortoise.generate_schemas()


##############################################################################
async def shutdown_local_data() -> None:
    """Close down the local connection."""
    await Tortoise.close_connections()


### local_data.py ends here
