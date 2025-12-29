"""The main commands used within the application."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class RefreshFromTheOldReader(Command):
    """Connect to TheOldReader and refresh the local articles."""

    BINDING_KEY = "ctrl+r"
    SHOW_IN_FOOTER = True
    FOOTER_TEXT = "Refresh"


##############################################################################
class ToggleShowAll(Command):
    """Toggle between showing all and showing only unread"""

    BINDING_KEY = "f2"


### main.py ends here
