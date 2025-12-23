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

    # This need to try/except/pass seems massively unnecessary. Everything
    # I'm reading seems to suggest that the migration system should handle
    # this, not try and create the index if it exists, but it does and it
    # gives an error. So, for now, this...

    dal.define(LocalArticleCategory)
    try:
        LocalArticleCategory.create_index(
            "idx_local_article_category_article", LocalArticleCategory.article
        )
    except RuntimeError:
        pass
    try:
        LocalArticleCategory.create_index(
            "idx_local_article_category_category", LocalArticleCategory.category
        )
    except RuntimeError:
        pass

    dal.define(LocalArticle)
    try:
        LocalArticle.create_index(
            "idx_local_article_article_id", LocalArticle.article_id
        )
    except RuntimeError:
        pass
    try:
        LocalArticle.create_index(
            "idx_local_article_origin_stream_id", LocalArticle.origin_stream_id
        )
    except RuntimeError:
        pass

    dal.define(LocalFolder)

    dal.define(LocalSubscription)
    try:
        LocalSubscription.create_index(
            "idx_local_subscription_subscription_id", LocalSubscription.subscription_id
        )
    except RuntimeError:
        pass

    dal.define(LocalSubscriptionCategory)
    try:
        LocalSubscriptionCategory.create_index(
            "idx_local_subscription_category_subscription",
            LocalSubscriptionCategory.subscription,
        )
    except RuntimeError:
        pass
    try:
        LocalSubscriptionCategory.create_index(
            "idx_local_subscription_category_category_id",
            LocalSubscriptionCategory.category_id,
        )
    except RuntimeError:
        pass

    dal.define(NavigationState)

    return dal


### db.py ends here
