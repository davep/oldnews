"""Defines the models for holding local subscription data."""

##############################################################################
# Tortoise imports.
from tortoise import fields
from tortoise.models import Model


##############################################################################
class LocalSubscription(Model):
    """A local copy of a subscription."""

    subscription_id = fields.CharField(max_length=255, pk=True)
    """The ID of the subscription."""
    title = fields.TextField()
    """The title of the subscription."""
    sort_id = fields.CharField(max_length=255)
    """The sort ID of the subscription."""
    first_item_time = fields.DatetimeField()
    """The time of the first item."""
    url = fields.TextField()
    """The URL of the subscription."""
    html_url = fields.TextField()
    """The HTML URL of the subscription."""


##############################################################################
class LocalSubscriptionCategory(Model):
    """A local copy of the categories associated with a subscription."""

    subscription = fields.ForeignKeyField(
        "models.LocalSubscription", related_name="categories", on_delete=fields.CASCADE
    )
    """The ID of the subscription this category belongs to."""
    category_id = fields.CharField(max_length=255)
    """The ID for the category."""
    label = fields.CharField(max_length=255)
    """The label for the category."""


### local_subscription.py ends here
