"""Code for working with the backend database."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# TypeDAL imports.
from typedal import TypeDAL, TypedTable
from typedal.config import TypeDALConfig

##############################################################################
# Local imports.
from .last_grab import LastGrabbed
from .local_articles import LocalArticle, LocalArticleAlternate, LocalArticleCategory
from .local_folders import LocalFolder
from .local_subscriptions import LocalSubscription, LocalSubscriptionCategory
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
def _safely_index(table: type[TypedTable], name: str, field: str) -> None:
    """Create an index on a type, but handle errors.

    Args:
        table: The table to create the index against.
        name: The name of the index.
        field: The field to index.

    Notes:
        From what I can gather TypeDAL *should* only create the index if it
        doesn't exist. Instead it throws an error if it exists. So here I
        swallow the `RuntimeError`. Hopefully there is a better way and I've
        just missed it.
    """
    try:
        table.create_index(name, field)
    except RuntimeError:
        pass


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

    dal.define(LocalArticle)
    _safely_index(LocalArticle, "idx_local_article_article_id", LocalArticle.article_id)
    _safely_index(
        LocalArticle,
        "idx_local_article_origin_stream_id",
        LocalArticle.origin_stream_id,
    )

    dal.define(LocalArticleCategory)
    # TODO: Need to make `field` more open.
    # _safely_index(
    #     LocalArticleCategory,
    #     "idx_local_article_category_article",
    #     LocalArticleCategory.article,
    # )
    _safely_index(
        LocalArticleCategory,
        "idx_local_article_category_category",
        LocalArticleCategory.category,
    )

    dal.define(LocalArticleAlternate)

    dal.define(LocalFolder)

    dal.define(LocalSubscription)
    _safely_index(
        LocalSubscription,
        "idx_local_subscription_subscription_id",
        LocalSubscription.subscription_id,
    )

    dal.define(LocalSubscriptionCategory)
    _safely_index(
        LocalSubscriptionCategory,
        "idx_local_subscription_category_subscription",
        LocalSubscriptionCategory.subscription,
    )
    _safely_index(
        LocalSubscriptionCategory,
        "idx_local_subscription_category_category_id",
        LocalSubscriptionCategory.category_id,
    )

    dal.define(NavigationState)
    dal.define(LastGrabbed)

    return dal


### db.py ends here
