"""Code relating to persisting subscriptions."""

##############################################################################
# Tortoise imports.
##############################################################################
# OldAS subscriptions.
from oldas import Subscription, Subscriptions
from oldas.subscriptions import Categories, Category
from tortoise.transactions import in_transaction

##############################################################################
# Local imports.
from .models import LocalSubscription, LocalSubscriptionCategory


##############################################################################
async def get_local_subscriptions() -> Subscriptions:
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
                for category in subscription.categories  # type: ignore
            ),
        )
        for subscription in await LocalSubscription.all().prefetch_related("categories")
    )


##############################################################################
async def save_local_subscriptions(subscriptions: Subscriptions) -> Subscriptions:
    """Local save the given subscriptions.

    Args:
        subscriptions: The subscriptions to save.

    Returns:
        The subscriptions.
    """
    async with in_transaction():
        await LocalSubscription.all().delete()
        await LocalSubscription.bulk_create(
            LocalSubscription(
                subscription_id=subscription.id,
                title=subscription.title,
                sort_id=subscription.sort_id,
                first_item_time=subscription.first_item_time,
                url=subscription.url,
                html_url=subscription.html_url,
            )
            for subscription in subscriptions
        )
        await LocalSubscriptionCategory.bulk_create(
            LocalSubscriptionCategory(
                subscription_id=subscription.id,
                category_id=category.id,
                label=category.label,
            )
            for subscription in subscriptions
            for category in subscription.categories
        )
    return subscriptions


### local_subscriptions.py ends here
