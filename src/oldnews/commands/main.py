"""The main commands used within the application."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class RefreshFromTheOldReader(Command):
    """Connect to TheOldReader and refresh the local articles"""

    BINDING_KEY = "ctrl+r"
    SHOW_IN_FOOTER = True
    FOOTER_TEXT = "Refresh"


##############################################################################
class ToggleShowAll(Command):
    """Toggle between showing all and showing only unread"""

    BINDING_KEY = "f2"


##############################################################################
class Escape(Command):
    """Back out through the panes, or exit the app if the navigation pane has focus"""

    BINDING_KEY = "escape, q"


##############################################################################
class NextUnread(Command):
    """Navigate to the next unread article in the currently-selected category"""

    BINDING_KEY = "n"


##############################################################################
class PreviousUnread(Command):
    """Navigate to the previous unread article in the currently-selected category"""

    BINDING_KEY = "p"


##############################################################################
class OpenArticle(Command):
    """Open the current article in the web browser"""

    BINDING_KEY = "o"


### main.py ends here
