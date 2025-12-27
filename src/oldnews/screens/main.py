"""Provides the main screen."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from datetime import datetime, timezone

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
from textual.message import Message
from textual.reactive import var
from textual.widgets import Footer, Header

##############################################################################
# Textual enhanced imports.
from textual_enhanced.commands import ChangeTheme, Command, Help, Quit
from textual_enhanced.screen import EnhancedScreen

##############################################################################
# Local imports.
from .. import __version__
from ..data import (
    get_local_folders,
    get_local_subscriptions,
    get_local_unread,
    get_local_unread_articles,
    last_grabbed_data_at,
    remember_we_last_grabbed_at,
    save_local_articles,
    save_local_folders,
    save_local_subscriptions,
    save_local_unread,
)
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

    @dataclass
    class BusyWith(Message):
        """Message sent to indicate we're busy with something."""

        operation: str
        """The operation we're busy with."""

    @dataclass
    class NewFolders(Message):
        """Message sent when new folders are acquired."""

        folders: Folders
        """The new folders."""

    @dataclass
    class NewSubscriptions(Message):
        """Message sent when new subscriptions are acquired."""

        subscriptions: Subscriptions
        """The new subscriptions."""

    @dataclass
    class NewUnread(Message):
        """Message sent when new unread counts are acquired."""

        counts: Unread
        """The new unread counts."""

    class ReloadFromToR(Message):
        """Message that requests that we reload from TheOldReader."""

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
        self._load_locally()

    @on(BusyWith)
    def _indicate_busy_with(self, message: BusyWith) -> None:
        """Indicate we're busy with something."""
        self.sub_title = message.operation

    @on(NewFolders)
    def _new_folders(self, message: NewFolders) -> None:
        """Handle new folders being found.

        Args:
            message: The message with the new folders.
        """
        self.folders = message.folders

    @on(NewSubscriptions)
    def _new_subscriptions(self, message: NewSubscriptions) -> None:
        """Handle new subscriptions being found.

        Args:
            message: The message with the new subscriptions.
        """
        self.subscriptions = message.subscriptions

    @on(NewUnread)
    def _new_unread(self, message: NewUnread) -> None:
        """Handle new unread counts being found.

        Args:
            message: The message with the new unread counts.
        """
        self.unread = message.counts

    @work(thread=True, exclusive=True)
    def _load_locally(self) -> None:
        """Load up any locally-held data."""
        if folders := get_local_folders():
            self.post_message(self.NewFolders(folders))
        if subscriptions := get_local_subscriptions():
            self.post_message(self.NewSubscriptions(subscriptions))
        if unread := get_local_unread():
            self.post_message(self.NewUnread(unread))
        # Now that we've loaded everything that we have locally, kick off a
        # refresh from TheOldReader.
        #
        # TODO: I might want to delay this a moment, or not. Have a think.
        self.post_message(self.ReloadFromToR())

    async def _download_newest_articles(self) -> None:
        """Download the latest articles available."""
        last_grabbed = last_grabbed_data_at()
        new_grab = datetime.now(timezone.utc)
        save_local_articles(
            await (
                Articles.load_unread(self._session, "")
                if last_grabbed is None
                else Articles.load_new_since(self._session, "", last_grabbed)
            )
        )
        remember_we_last_grabbed_at(new_grab)

    @on(ReloadFromToR)
    @work(exclusive=True)
    async def load_from_tor(self) -> None:
        """Load the main data from TheOldReader."""

        # Get the folder list.
        self.post_message(self.BusyWith("Getting folder list"))
        self.post_message(
            self.NewFolders(save_local_folders(await Folders.load(self._session)))
        )

        # Get the subscriptions list.
        self.post_message(self.BusyWith("Getting subscriptions list"))
        self.post_message(
            self.NewSubscriptions(
                save_local_subscriptions(await Subscriptions.load(self._session))
            )
        )

        # Get the unread counts.
        self.post_message(self.BusyWith("Getting unread counts"))
        self.post_message(
            self.NewUnread(save_local_unread(await Unread.load(self._session)))
        )

        # Get unread articles. Get all available unread articles if we've
        # never grabbed any before, otherwise get all those new since we
        # last grabbed sone.
        if last_grabbed_data_at() is None:
            self.post_message(self.BusyWith("Getting available articles"))
        else:
            self.post_message(
                self.BusyWith(f"Getting articles new since {last_grabbed_data_at()}")
            )
        await self._download_newest_articles()

        # Finally we're all done.
        self.post_message(self.BusyWith(""))

    @on(Navigation.CategorySelected)
    def _handle_navigaion_selection(self, message: Navigation.CategorySelected) -> None:
        """Handle a navigation selection being made.

        Args:
            message: The message to react to.
        """
        self.article = None
        self.articles = get_local_unread_articles(message.category)

    @on(ArticleList.ViewArticle)
    def _view_article(self, message: ArticleList.ViewArticle) -> None:
        """Handle a request to view an article.

        Args:
            message: The message requesting an article be viewed.
        """
        self.article = message.article


### main.py ends here
