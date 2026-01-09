"""Provides the main screen."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from webbrowser import open as open_url

##############################################################################
# OldAs imports.
from oldas import (
    Article,
    ArticleIDs,
    Articles,
    Folder,
    Folders,
    Session,
    Subscription,
    Subscriptions,
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
from ..commands import (
    Escape,
    NextUnread,
    OpenArticle,
    PreviousUnread,
    RefreshFromTheOldReader,
    ToggleShowAll,
)
from ..data import (
    LocalUnread,
    get_local_articles,
    get_local_folders,
    get_local_subscriptions,
    get_local_unread,
    get_unread_article_ids,
    last_grabbed_data_at,
    load_configuration,
    locally_mark_article_ids_read,
    locally_mark_read,
    remember_we_last_grabbed_at,
    save_local_articles,
    save_local_folders,
    save_local_subscriptions,
    total_unread,
    update_configuration,
)
from ..providers import MainCommands
from ..widgets import ArticleContent, ArticleList, Navigation


##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen for the application."""

    TITLE = f"OldNews v{__version__}"

    HELP = """
    ## Main application keys and commands

    The following keys and commands can be used anywhere here on the main screen.
    """

    CSS = """
    Main {
        layout: horizontal;
        hatch: right $surface;

        * {
            scrollbar-background: $surface;
            scrollbar-background-hover: $surface;
            scrollbar-background-active: $surface;
            &:focus, &:focus-within {
                scrollbar-background: $panel;
                scrollbar-background-hover: $panel;
                scrollbar-background-active: $panel;
            }
        }

        .panel {
            padding-right: 0;
            border: none;
            border-left: round $border 50%;
            background: $surface;
            scrollbar-gutter: stable;
            &:focus, &:focus-within {
                border: none;
                border-left: round $border;
                background: $panel 80%;
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
        ToggleShowAll,
        Quit,
        RefreshFromTheOldReader,
        # Everything else.
        Escape,
        NextUnread,
        PreviousUnread,
        OpenArticle,
        ChangeTheme,
    ]

    BINDINGS = Command.bindings(*COMMAND_MESSAGES)

    COMMANDS = {MainCommands}

    folders: var[Folders] = var(Folders)
    """The folders that subscriptions are assigned to."""
    subscriptions: var[Subscriptions] = var(Subscriptions)
    """The list of subscriptions."""
    current_category: var[Folder | Subscription | None] = var(None)
    """The navigation category that is currently selected."""
    unread: var[LocalUnread] = var(LocalUnread)
    """The unread counts."""
    articles: var[Articles] = var(Articles)
    """The currently-viewed list of articles."""
    article: var[Article | None] = var(None)
    """The currently-viewed article."""
    show_all: var[bool] = var(False)
    """Should we show all articles or only new?"""

    @dataclass
    class SubTitle(Message):
        """Message sent to set the sub-title to something."""

        title: str | None = None
        """The title to set."""

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

        counts: LocalUnread
        """The new unread counts."""

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
            yield ArticleList(classes="panel").data_bind(
                Main.articles, Main.current_category
            )
            yield ArticleContent(classes="panel").data_bind(Main.article)
        yield Footer()

    def on_mount(self) -> None:
        """Configure the application once the DOM is mounted."""
        self.show_all = load_configuration().show_all
        self._load_locally()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action is possible to perform right now.

        Args:
            action: The action to perform.
            parameters: The parameters of the action.

        Returns:
            `True` if it can perform, `False` or `None` if not.
        """
        if not self.is_mounted:
            # Surprisingly it seems that Textual's "dynamic bindings" can
            # cause this method to be called before the DOM is up and
            # running. This breaks the rule of least astonishment, I'd say,
            # but okay let's be defensive... (when I can come up with a nice
            # little MRE I'll report it).
            return True
        if action == OpenArticle.action_name():
            return self.article is not None
        if action in (NextUnread.action_name(), PreviousUnread.action_name()):
            return self.articles is not None and any(
                article.is_unread for article in self.articles
            )
        return True

    @on(SubTitle)
    def _update_sub_title(self, message: SubTitle) -> None:
        """Handle a request to set the sub-title to something.

        Args:
            message: The message requesting the sub-title be updated.
        """
        self.sub_title = (
            message.title if message.title else f"{total_unread(self.unread)} unread"
        )

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
        self.post_message(self.SubTitle(""))

    @work(thread=True, exclusive=True)
    def _load_locally(self) -> None:
        """Load up any locally-held data."""
        if folders := get_local_folders():
            self.post_message(self.NewFolders(folders))
        if subscriptions := get_local_subscriptions():
            self.post_message(self.NewSubscriptions(subscriptions))
        if unread := get_local_unread(folders, subscriptions):
            self.post_message(self.NewUnread(unread))
        # If we've never grabbed data from ToR before, or if it's been long enough...
        if (last_grabbed := last_grabbed_data_at()) is None or (
            (datetime.now() - last_grabbed).seconds
            >= load_configuration().startup_refresh_holdoff_period
        ):
            # ...kick off a refresh from TheOldReader.
            self.post_message(RefreshFromTheOldReader())

    async def _download_newest_articles(self) -> None:
        """Download the latest articles available."""
        last_grabbed = last_grabbed_data_at() or (
            datetime.now() - timedelta(days=load_configuration().local_history)
        )
        new_grab = datetime.now(timezone.utc)
        loaded = 0
        async for article in Articles.stream_new_since(
            self._session, last_grabbed, n=10
        ):
            # I've encountered articles that don't have an origin stream ID,
            # which means that I can't relate them back to a stream, which
            # means I'll never see them anyway...
            if not article.origin.stream_id:
                continue
            # TODO: Right now I'm saving articles one at a time; perhaps I
            # should save them in small batches? This would be simple enough
            # -- perhaps same them in batches the same size as the buffer
            # window I'm using right now (currently 10 articles per trip to
            # ToR).
            save_local_articles(Articles([article]))
            loaded += 1
            if (loaded % 10) == 0:
                self.post_message(
                    self.SubTitle(f"Downloading articles from TheOldReader: {loaded}")
                )
        if loaded:
            self.notify(f"Articles downloaded: {loaded}")
        else:
            self.notify("No new articles found on TheOldReader")
        remember_we_last_grabbed_at(new_grab)

    async def _refresh_read_status(self) -> None:
        """Refresh the read status from the server."""
        self.post_message(
            self.SubTitle("Getting list of unread articles from TheOldReader")
        )
        remote_unread_articles = set(
            article_id.full_id
            for article_id in await ArticleIDs.load_unread(self._session)
        )
        self.post_message(self.SubTitle("Comparing against locally-read articles"))
        local_unread_articles = set(get_unread_article_ids())
        if mark_as_read := local_unread_articles - remote_unread_articles:
            self.post_message(
                self.SubTitle(
                    f"Articles found read elsewhere on TheOldReader: {len(mark_as_read)}"
                )
            )
            locally_mark_article_ids_read(mark_as_read)

    @on(RefreshFromTheOldReader)
    @work(exclusive=True)
    async def action_refresh_from_the_old_reader_command(self) -> None:
        """Load the main data from TheOldReader."""

        # Get the folder list.
        self.post_message(self.SubTitle("Getting folder list"))
        self.post_message(
            self.NewFolders(save_local_folders(await Folders.load(self._session)))
        )

        # Get the subscriptions list.
        self.post_message(self.SubTitle("Getting subscriptions list"))
        self.post_message(
            self.NewSubscriptions(
                save_local_subscriptions(await Subscriptions.load(self._session))
            )
        )

        # Download the latest articles we don't know about.
        if never_grabbed_before := last_grabbed_data_at() is None:
            self.post_message(self.SubTitle("Getting available articles"))
        else:
            self.post_message(
                self.SubTitle(f"Getting articles new since {last_grabbed_data_at()}")
            )
        await self._download_newest_articles()

        # If we have grabbed data before, let's try and sync up what's been read.
        if not never_grabbed_before:
            await self._refresh_read_status()

        # Recalculate the unread counts.
        self.post_message(self.SubTitle("Calculating unread counts"))
        self.post_message(
            self.NewUnread(get_local_unread(self.folders, self.subscriptions))
        )

        # Finally we're all done.
        self.post_message(self.SubTitle(""))

    @on(Navigation.CategorySelected)
    def _handle_navigaion_selection(self, message: Navigation.CategorySelected) -> None:
        """Handle a navigation selection being made.

        Args:
            message: The message to react to.
        """
        self.current_category = message.category
        self.article = None
        self.articles = get_local_articles(message.category, not self.show_all)
        self.query_one(ArticleList).focus()

    def _refresh_article_list(self) -> None:
        """Refresh the content of the article list."""
        if category := self.query_one(Navigation).current_category:
            self.articles = get_local_articles(category, not self.show_all)

    def _watch_show_all(self) -> None:
        """Handle changes to the show all flag."""
        self._refresh_article_list()

    @work
    async def _mark_read(self, article: Article) -> None:
        """Mark the given article as read.

        Args:
            article: The article to mark as read.
        """
        locally_mark_read(article)
        self.post_message(
            self.NewUnread(get_local_unread(self.folders, self.subscriptions))
        )
        self._refresh_article_list()
        await article.mark_read(self._session)

    @on(ArticleList.ViewArticle)
    def _view_article(self, message: ArticleList.ViewArticle) -> None:
        """Handle a request to view an article.

        Args:
            message: The message requesting an article be viewed.
        """
        self.article = message.article
        self.query_one(ArticleContent).focus()
        self.set_timer(
            min(0.1, load_configuration().mark_read_on_read_timeout),
            lambda: self._mark_read(message.article),
        )

    def action_toggle_show_all_command(self) -> None:
        """Toggle showing all/unread."""
        self.show_all = not self.show_all
        with update_configuration() as config:
            config.show_all = self.show_all
        self.notify(
            f"Showing {'all available' if self.show_all else 'only unread'} articles"
        )

    def action_escape_command(self) -> None:
        """Handle escaping.

        The action's approach is to step-by-step back out from the 'deepest'
        level to the topmost, and if we're at the topmost then exit the
        application.
        """
        if self.focused is not None and self.focused.parent is self.query_one(
            ArticleContent
        ):
            self.query_one(ArticleList).focus()
            self.article = None
        elif self.focused is self.query_one(ArticleList):
            self.query_one(Navigation).focus()
        elif self.focused is self.query_one(Navigation):
            self.app.exit()

    def action_next_unread_command(self) -> None:
        """Go to the next unread article in the currently-viewed category."""
        if self.article is None:
            self.query_one(ArticleList).highlight_next_unread()
        else:
            self.query_one(ArticleList).select_next_unread()

    def action_previous_unread_command(self) -> None:
        """Go to the previous unread article in the currently-viewed category"""
        if self.article is None:
            self.query_one(ArticleList).highlight_previous_unread()
        else:
            self.query_one(ArticleList).select_previous_unread()

    def action_open_article_command(self) -> None:
        """Open the current article in a web browser."""
        if self.article is not None:
            if self.article.html_url:
                open_url(self.article.html_url)
            else:
                self.notify(
                    "No URL available for this article",
                    severity="error",
                    title="Can't visit",
                )


### main.py ends here
