"""Code relating to persisting subscriptions."""

##############################################################################
# Python imports.
from datetime import datetime

##############################################################################
# OldAS subscriptions.
from oldas import Subscriptions

##############################################################################
# TypeDAL imports.
from typedal import TypedTable


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
def save_local_subscriptions(subscriptions: Subscriptions) -> Subscriptions:
    """Local save the given subscriptions.

    Args:
        subscriptions: The subscriptions to save.

    Returns:
        The subscriptions.
    """
    assert LocalSubscription._db is not None
    for subscription in subscriptions:
        LocalSubscriptionCategory.where(subscription=subscription.id).delete()
        LocalSubscriptionCategory.bulk_insert(
            [
                {
                    "subscription": subscription.id,
                    "category_id": category.id,
                    "label": category.label,
                }
                for category in subscription.categories
            ]
        )
        LocalSubscription.update_or_insert(
            LocalSubscription.subscription_id == subscription.id,
            subscription_id=subscription.id,
            title=subscription.title,
            sort_id=subscription.sort_id,
            first_item_time=subscription.first_item_time,
            url=subscription.url,
            html_url=subscription.html_url,
        )
    LocalSubscription._db.commit()
    return subscriptions


### local_subscriptions.py ends here
