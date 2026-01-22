"""Code relating to persisting subscriptions."""

##############################################################################
# Python imports.
from datetime import datetime

##############################################################################
# OldAS subscriptions.
from oldas import Subscription, Subscriptions
from oldas.subscriptions import Categories, Category

##############################################################################
# TypeDAL imports.
from typedal import TypedTable

##############################################################################
# Local imports.
from .tools import commit


##############################################################################
class LocalSubscription(TypedTable):
    """A local copy of a subscription."""

    subscription_id: str
    """The ID of the subscription."""
    title: str
    """The title of the subscription."""
    sort_id: str
    """The sort ID of the subscription."""
    first_item_time: datetime
    """The time of the first item."""
    url: str
    """The URL of the subscription."""
    html_url: str
    """The HTML URL of the subscription."""


##############################################################################
class LocalSubscriptionCategory(TypedTable):
    """A local copy of the categories associated with a subscription."""

    subscription: str
    """The ID of the subscription this category belongs to."""
    category_id: str
    """The ID for the category."""
    label: str
    """The label for the category."""


##############################################################################
def get_local_subscriptions() -> Subscriptions:
    """Gets the local cache of known subscriptions.

    Return:
        The locally-known `Subscriptions`.
    """
    return Subscriptions(
        Subscription(
            id=subscription.subscription_id,
            title=subscription.title,
            sort_id=subscription.sort_id,
            first_item_time=subscription.first_item_time,
            url=subscription.url,
            html_url=subscription.html_url,
            categories=Categories(
                Category(
                    id=category.category_id,
                    label=category.label,
                )
                for category in LocalSubscriptionCategory.where(
                    subscription=subscription.subscription_id
                )
            ),
        )
        for subscription in LocalSubscription.select(LocalSubscription.ALL)
    )


##############################################################################
def save_local_subscriptions(subscriptions: Subscriptions) -> Subscriptions:
    """Local save the given subscriptions.

    Args:
        subscriptions: The subscriptions to save.

    Returns:
        The subscriptions.
    """
    LocalSubscription.truncate()
    LocalSubscriptionCategory.truncate()
    LocalSubscription.bulk_insert(
        [
            {
                "subscription_id": subscription.id,
                "title": subscription.title,
                "sort_id": subscription.sort_id,
                "first_item_time": subscription.first_item_time,
                "url": subscription.url,
                "html_url": subscription.html_url,
            }
            for subscription in subscriptions
        ]
    )
    LocalSubscriptionCategory.bulk_insert(
        [
            {
                "subscription": subscription.id,
                "category_id": category.id,
                "label": category.label,
            }
            for subscription in subscriptions
            for category in subscription.categories
        ]
    )
    commit(LocalSubscription)
    return subscriptions


### local_subscriptions.py ends here
