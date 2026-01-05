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
from ..commands import (
    Escape,
    NextUnread,
    OpenArticle,
    PreviousUnread,
    RefreshFromTheOldReader,
    ToggleShowAll,
)


##############################################################################
class MainCommands(CommandsProvider):
    """Provides some top-level commands for the application."""

    def commands(self) -> CommandHits:
        """Provide the main application commands for the command palette.

        Yields:
            The commands for the command palette.
        """
        yield Escape()
        yield from self.maybe(NextUnread)
        yield from self.maybe(PreviousUnread)
        yield from self.maybe(OpenArticle)
        yield ToggleShowAll()
        yield RefreshFromTheOldReader()
        yield ChangeTheme()
        yield Help()
        yield Quit()


### main.py ends here
