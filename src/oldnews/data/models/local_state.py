"""Defines modules relating to local state."""

##############################################################################
# Tortoise imports.
from tortoise import fields
from tortoise.models import Model


##############################################################################
class LastGrabbed(Model):
    """Holds details of when we last grabbed data."""

    at_time = fields.DatetimeField(use_tz=True)
    """The time at which data was last grabbed."""


### local_state.py ends here
