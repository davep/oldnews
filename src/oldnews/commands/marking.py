"""Provides commands related to marking things in some way."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class MarkRead(Command):
    """Mark the current article as read"""

    BINDING_KEY = "r"


##############################################################################
class MarkAllRead(Command):
    """Mark all unread articles in the current category as read"""

    BINDING_KEY = "R"


##############################################################################
class MarkUnread(Command):
    """Mark the current article as unread"""

    BINDING_KEY = "u"


### marking.py ends here
