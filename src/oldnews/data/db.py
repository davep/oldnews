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
from .last_grab import LastGrabbed
from .local_articles import LocalArticle, LocalArticleAlternate, LocalArticleCategory
from .local_subscriptions import LocalSubscription, LocalSubscriptionCategory
from .locations import data_dir
from .navigation_state import NavigationState
from .tools import safely_index


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

    dal.define(LocalArticle)
    safely_index(LocalArticle, "idx_local_article_article_id", LocalArticle.article_id)
    safely_index(
        LocalArticle,
        "idx_local_article_origin_stream_id",
        LocalArticle.origin_stream_id,
    )

    dal.define(LocalArticleCategory)
    safely_index(
        LocalArticleCategory,
        "idx_local_article_category_article",
        LocalArticleCategory.article,
    )
    safely_index(
        LocalArticleCategory,
        "idx_local_article_category_category",
        LocalArticleCategory.category,
    )

    dal.define(LocalArticleAlternate)

    dal.define(LocalSubscription)
    safely_index(
        LocalSubscription,
        "idx_local_subscription_subscription_id",
        LocalSubscription.subscription_id,
    )

    dal.define(LocalSubscriptionCategory)
    safely_index(
        LocalSubscriptionCategory,
        "idx_local_subscription_category_subscription",
        LocalSubscriptionCategory.subscription,
    )
    safely_index(
        LocalSubscriptionCategory,
        "idx_local_subscription_category_category_id",
        LocalSubscriptionCategory.category_id,
    )

    dal.define(NavigationState)
    dal.define(LastGrabbed)

    return dal


### db.py ends here
