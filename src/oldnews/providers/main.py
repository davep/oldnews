"""Provides the main application commands for the command palette."""

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import (
    ChangeTheme,
    CommandHits,
    CommandsProvider,
    Help,
    Quit,
)

##############################################################################
# Local imports.
from ..commands import RefreshFromTheOldReader, ToggleShowAll


##############################################################################
class MainCommands(CommandsProvider):
    """Provides some top-level commands for the application."""

    def commands(self) -> CommandHits:
        """Provide the main application commands for the command palette.

        Yields:
            The commands for the command palette.
        """
        yield ToggleShowAll()
        yield RefreshFromTheOldReader()
        yield ChangeTheme()
        yield Help()
        yield Quit()


### main.py ends here
