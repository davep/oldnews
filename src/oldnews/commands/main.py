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


##############################################################################
class OpenArticle(Command):
    """Open the current article in the web browser"""

    BINDING_KEY = "o"


##############################################################################
class OpenHomePage(Command):
    """Open the home page for the current subscription in the web browser"""

    BINDING_KEY = "O"


##############################################################################
class MarkAllRead(Command):
    """Mark all unread articles in the current category as read"""

    BINDING_KEY = "R"


##############################################################################
class CopyHomePageToClipboard(Command):
    """Copy the URL of the current subscription's home page to the clipboard"""

    BINDING_KEY = "f3"


##############################################################################
class CopyFeedToClipboard(Command):
    """Copy the URL of the current subscription's feed to the clipboard"""

    BINDING_KEY = "f4"


##############################################################################
class CopyArticleToClipboard(Command):
    """Copy the URL for the current article to the clipboard"""

    BINDING_KEY = "f5"


##############################################################################
class Copy(Command):
    """Copy a URL to the clipboard depending on the context"""

    BINDING_KEY = "ctrl+c"


##############################################################################
class AddSubscription(Command):
    """Add a subscription feed"""

    BINDING_KEY = "plus"


##############################################################################
class Rename(Command):
    """Rename the current folder or subscription"""

    BINDING_KEY = "f6"


##############################################################################
class Remove(Command):
    """Remove the current folder or subscription"""

    BINDING_KEY = "delete"


##############################################################################
class MoveSubscription(Command):
    """Move the current subscription to folder"""

    BINDING_KEY = "f7"


##############################################################################
class Information(Command):
    """Show low-level information about the selected item"""

    BINDING_KEY = "f8"


### main.py ends here
