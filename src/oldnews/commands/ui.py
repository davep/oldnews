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


##############################################################################
class JumpToSubscriptions(Command):
    """Jump to the subscriptions panel"""

    BINDING_KEY = "1"


##############################################################################
class JumpToArticles(Command):
    """Jump to the articles panel"""

    BINDING_KEY = "2"


##############################################################################
#
class JumpToArticle(Command):
    """Jump to the article panel"""

    BINDING_KEY = "3"


### ui.py ends here
