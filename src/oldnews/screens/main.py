"""Provides the main screen."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.screen import EnhancedScreen

##############################################################################
# Local imports.
from .. import __version__

##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen for the application."""

    TITLE = f"OldNews v{__version__}"

    COMMAND_MESSAGES = []

### main.py ends here

