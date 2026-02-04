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


##############################################################################
class NavigationState(Model):
    """Table that holds state of the navigation table."""

    expanded_folder_id = fields.CharField(max_length=256)
    """The ID of a folder that is in the expanded state."""


### local_state.py ends here
