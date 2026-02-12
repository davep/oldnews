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
class Information(Command):
    """Show low-level information about the selected item"""

    BINDING_KEY = "i"


##############################################################################
class UserInformation(Command):
    """Show the information known about the logged-in account"""

    BINDING_KEY = "f4"


### main.py ends here
