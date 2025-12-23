"""Code for working with the backend database."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# TypeDAL imports.
from typedal import TypeDAL
from typedal.config import TypeDALConfig

##############################################################################
# Local imports.
from .local_articles import LocalArticle, LocalArticleCategory
from .local_folders import LocalFolder
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
    # Note the passing of an empty TypeDALConfig. Not doing this seems to
    # result in a:
    #
    #    Could not load typedal config toml: 'typedal'
    #
    # warning to stdout, otherwise.
    dal = TypeDAL(f"sqlite://{db_file()}", folder=data_dir(), config=TypeDALConfig())
    dal.define(LocalArticleCategory)
    dal.define(LocalArticle)
    dal.define(LocalFolder)
    dal.define(NavigationState)
    return dal


### db.py ends here
