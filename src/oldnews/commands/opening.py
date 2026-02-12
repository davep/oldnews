"""Provides commands related to opening things."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import Command


##############################################################################
class OpenArticle(Command):
    """Open the current article in the web browser"""

    BINDING_KEY = "o"


##############################################################################
class OpenHomePage(Command):
    """Open the home page for the current subscription in the web browser"""

    BINDING_KEY = "O"


### opening.py ends here
