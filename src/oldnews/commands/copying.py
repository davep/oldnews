"""Defines commands related to copying things."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class CopyHomePageToClipboard(Command):
    """Copy the URL of the current subscription's home page to the clipboard"""

    BINDING_KEY = "f3"


##############################################################################
class CopyFeedToClipboard(Command):
    """Copy the URL of the current subscription's feed to the clipboard"""

    BINDING_KEY = "shift+f3"


##############################################################################
class CopyArticleToClipboard(Command):
    """Copy the URL for the current article to the clipboard"""

    BINDING_KEY = "super+f3"


##############################################################################
class Copy(Command):
    """Copy a URL to the clipboard depending on the context"""

    BINDING_KEY = "ctrl+c"


### copying.py ends here
