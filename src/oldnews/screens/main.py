"""Provides the main screen."""

##############################################################################
# OldAs imports.
from oldas import (
    Article,
    Articles,
    Folder,
    Folders,
    Session,
    Subscription,
    Subscriptions,
    Unread,
)

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import var
from textual.widgets import Footer, Header

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import ChangeTheme, Command, Help, Quit
from textual_enhanced.screen import EnhancedScreen

##############################################################################
# Local imports.
from .. import __version__
from ..providers import MainCommands
from ..widgets import ArticleContent, ArticleList, Navigation


##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen for the application."""

    TITLE = f"OldNews v{__version__}"

    CSS = """
    Main {
        layout: horizontal;
        hatch: right $surface;

        .panel {
            padding-right: 0;
            border: none;
            border-left: round $border 50%;
            background: $surface;
            scrollbar-gutter: stable;
            scrollbar-background: $surface;
            scrollbar-background-hover: $surface;
            scrollbar-background-active: $surface;
            &:focus, &:focus-within {
                border: none;
                border-left: round $border;
                background: $panel 80%;
                scrollbar-background: $panel;
                scrollbar-background-hover: $panel;
                scrollbar-background-active: $panel;
            }
            &> .option-list--option {
                padding: 0 1;
            }
        }

        Navigation {
            height: 1fr;
            width: 25%;
        }

        ArticleList {
            height: 1fr;
        }

        ArticleContent {
            height: 2fr;
        }
    }
    """

    COMMAND_MESSAGES = [
        # Keep these together as they're bound to function keys and destined
        # for the footer.
        Help,
        Quit,
        # Everything else.
        ChangeTheme,
    ]

    BINDINGS = Command.bindings(*COMMAND_MESSAGES)

    COMMANDS = {MainCommands}

    folders: var[Folders] = var(Folders)
    """The folders that subscriptions are assigned to."""
    subscriptions: var[Subscriptions] = var(Subscriptions)
    """The list of subscriptions."""
    unread: var[Unread | None] = var(None)
    """The unread counts."""
    articles: var[Articles] = var(Articles)
    """The currently-viewed list of articles."""
    article: var[Article | None] = var(None)
    """The currently-viewed article."""

    def __init__(self, session: Session) -> None:
        """Initialise the main screen."""
        super().__init__()
        self._session = session
        """The TOR session."""

    def compose(self) -> ComposeResult:
        """Compose the content of the main screen."""
        yield Header()
        yield Navigation(classes="panel").data_bind(
            Main.folders, Main.subscriptions, Main.unread
        )
        with Vertical():
            yield ArticleList(classes="panel").data_bind(Main.articles)
            yield ArticleContent(classes="panel").data_bind(Main.article)
        yield Footer()

    def on_mount(self) -> None:
        """Configure the application once the DOM is mounted."""
        self.load_from_tor()

    @work(exclusive=True)
    async def load_from_tor(self) -> None:
        """Load the main data from TheOldReader."""
        self.folders = await Folders.load(self._session)
        self.subscriptions = await Subscriptions.load(self._session)
        self.unread = await Unread.load(self._session)

    @work(exclusive=True)
    async def _get_related_unread_articles(
        self, category: Folder | Subscription
    ) -> None:
        """Get the unread articles related to the given category.

        Args:
            category: The category to get the unread articles for.
        """
        with self.busy_looking(ArticleList):
            self.articles = await Articles.load_unread(self._session, category)

    @on(Navigation.CategorySelected)
    def _handle_navigaion_selection(self, message: Navigation.CategorySelected) -> None:
        """Handle a navigation selection being made.

        Args:
            message: The message to react to.
        """
        self.article = None
        self._get_related_unread_articles(message.category)

    @on(ArticleList.ViewArticle)
    def _view_article(self, message: ArticleList.ViewArticle) -> None:
        """Handle a request to view an article.

        Args:
            message: The message requesting an article be viewed.
        """
        self.article = message.article


### main.py ends here
