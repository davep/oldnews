"""Code relating to persisting subscriptions."""

##############################################################################
# OldAS subscriptions.
from oldas import Subscription, Subscriptions
from oldas.subscriptions import Categories, Category

##############################################################################
# Tortoise imports.
from tortoise.transactions import in_transaction

##############################################################################
# Local imports.
from .models import (
    LocalSubscription,
    LocalSubscriptionCategory,
    LocalSubscriptionGrabFilter,
)


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


##############################################################################
async def get_content_grab_filter_for(subscription: Subscription | str) -> str | None:
    """Get any content grab filter associated with the subscription.

    Args:
        subscription: The subscription to get the content grab filter for.

    Returns:
        `None` if there is no filter, otherwise the CSS selector to use.
    """
    if isinstance(subscription, Subscription):
        subscription = subscription.id
    if grab_filter := await LocalSubscriptionGrabFilter.get_or_none(
        subscription_id=subscription
    ):
        return grab_filter.selector
    return None


##############################################################################
async def set_content_grab_filter_for(
    subscription: Subscription | str, selector: str
) -> None:
    """Set the content grab filter associated with the subscription.

    Args:
        subscription: The subscription to set the content grab filter for.
    """
    if isinstance(subscription, Subscription):
        subscription = subscription.id
    if selector:
        await LocalSubscriptionGrabFilter.update_or_create(
            subscription_id=subscription, defaults={"selector": selector}
        )
    else:
        await LocalSubscriptionGrabFilter.filter(subscription_id=subscription).delete()


##############################################################################
async def get_all_content_grab_filters() -> set[str]:
    """Get the full set of used content grab filters.

    Returns:
        The set of content filters the user as set up.
    """
    return {
        content_filter.selector
        for content_filter in await LocalSubscriptionGrabFilter.all()
    }


### local_subscriptions.py ends here
