"""Provides commands related to navigating the application."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class Escape(Command):
    """Back out through the panes, or exit the app if the navigation pane has focus"""

    BINDING_KEY = "escape, q"


##############################################################################
class NextUnread(Command):
    """Navigate to the next unread article in the currently-selected category"""

    BINDING_KEY = "n"


##############################################################################
class Next(Command):
    """Navigate to the next article regardless of read status"""

    BINDING_KEY = "N, ctrl+down"


##############################################################################
class PreviousUnread(Command):
    """Navigate to the previous unread article in the currently-selected category"""

    BINDING_KEY = "p"


##############################################################################
class Previous(Command):
    """Navigate to the next article regardless of read status"""

    BINDING_KEY = "P, ctrl+up"


### navigation.py ends here
