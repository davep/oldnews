"""Defines commands related to the user interface."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class ToggleShowAll(Command):
    """Toggle between showing all and showing only unread"""

    BINDING_KEY = "f2"


##############################################################################
class ToggleCompact(Command):
    """Toggle a more compact user interface"""

    BINDING_KEY = "f5"


### ui.py ends here
