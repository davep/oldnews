"""Defines commands related to folder and feed administration."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class AddSubscription(Command):
    """Add a subscription feed"""

    BINDING_KEY = "plus"


##############################################################################
class Rename(Command):
    """Rename the current folder or subscription"""

    BINDING_KEY = "apostrophe"


##############################################################################
class Remove(Command):
    """Remove the current folder or subscription"""

    BINDING_KEY = "delete"


##############################################################################
class MoveSubscription(Command):
    """Move the current subscription to folder"""

    BINDING_KEY = "vertical_line"


### admin.py ends here
