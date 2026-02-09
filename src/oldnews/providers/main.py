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
    AddSubscription,
    Copy,
    CopyArticleToClipboard,
    CopyFeedToClipboard,
    CopyHomePageToClipboard,
    Escape,
    Information,
    MarkAllRead,
    MarkRead,
    MarkUnread,
    MoveSubscription,
    Next,
    NextUnread,
    OpenArticle,
    OpenHomePage,
    Previous,
    PreviousUnread,
    RefreshFromTheOldReader,
    Remove,
    Rename,
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
        yield AddSubscription()
        yield ChangeTheme()
        yield from self.maybe(Copy)
        yield from self.maybe(CopyArticleToClipboard)
        yield from self.maybe(CopyFeedToClipboard)
        yield from self.maybe(CopyHomePageToClipboard)
        yield Escape()
        yield Help()
        yield from self.maybe(Information)
        yield from self.maybe(MarkAllRead)
        yield from self.maybe(MarkRead)
        yield from self.maybe(MarkUnread)
        yield from self.maybe(MoveSubscription)
        yield from self.maybe(Next)
        yield from self.maybe(NextUnread)
        yield from self.maybe(OpenArticle)
        yield from self.maybe(OpenHomePage)
        yield from self.maybe(Previous)
        yield from self.maybe(PreviousUnread)
        yield Quit()
        yield RefreshFromTheOldReader()
        yield from self.maybe(Rename)
        yield from self.maybe(Remove)
        yield ToggleShowAll()


### main.py ends here
