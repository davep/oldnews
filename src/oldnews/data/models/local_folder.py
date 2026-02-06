"""Defines the model for the local folder information."""

##############################################################################
# Tortoise imports.
from tortoise import fields
from tortoise.models import Model


##############################################################################
class LocalFolder(Model):
    """A local copy of a folder's information."""

    folder_id = fields.CharField(max_length=256, index=True)
    """The ID of the folder."""
    sort_id = fields.TextField(max_length=30)
    """The sort ID of the folder."""


### local_folder.py ends here
