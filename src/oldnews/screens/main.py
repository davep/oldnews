"""Provides the main screen."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from datetime import datetime, timedelta
from webbrowser import open as open_url

##############################################################################
# OldAs imports.
from oldas import (
    Article,
    Articles,
    Folder,
    Folders,
    Session,
    State,
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
from textual_enhanced.dialogs import Confirm, ModalInput
from textual_enhanced.screen import EnhancedScreen

##############################################################################
# Local imports.
from .. import __version__
from ..commands import (
    AddSubscription,
    Copy,
    CopyArticleToClipboard,
    CopyFeedToClipboard,
    CopyHomePageToClipboard,
    Escape,
    MarkAllRead,
    Next,
    NextUnread,
    OpenArticle,
    OpenHomePage,
    Previous,
    PreviousUnread,
    RefreshFromTheOldReader,
    RenameSubscription,
    ToggleShowAll,
)
from ..data import (
    LocalUnread,
    clean_old_read_articles,
    get_local_articles,
    get_local_folders,
    get_local_subscriptions,
    get_local_unread,
    last_grabbed_data_at,
    load_configuration,
    locally_mark_article_ids_read,
    locally_mark_read,
    total_unread,
    update_configuration,
)
from ..providers import MainCommands
from ..sync import ToRSync
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

        #article-view {
            display: none;
            &.--has-articles {
                display: block;
            }
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
        MarkAllRead,
        Next,
        NextUnread,
        Previous,
        PreviousUnread,
        OpenArticle,
        OpenHomePage,
        ChangeTheme,
        CopyHomePageToClipboard,
        CopyFeedToClipboard,
        CopyArticleToClipboard,
        Copy,
        AddSubscription,
        RenameSubscription,
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

    class SyncFinished(Message):
        """Message sent when a sync from TheOldReader is finished."""

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
        with Vertical(id="article-view"):
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
        if action in (OpenArticle.action_name(), CopyArticleToClipboard.action_name()):
            return self.article is not None
        if action in (
            OpenHomePage.action_name(),
            CopyFeedToClipboard.action_name(),
            CopyHomePageToClipboard.action_name(),
            RenameSubscription.action_name(),
        ):
            return self.query_one(Navigation).current_subscription is not None
        if action in (Next.action_name(), Previous.action_name()):
            return self.articles is not None
        if action in (
            NextUnread.action_name(),
            PreviousUnread.action_name(),
            MarkAllRead.action_name(),
        ):
            # If we're inside the navigation panel...
            if self.query_one(Navigation).has_focus:
                # ...we just care if there's anything unread somewhere.
                return any(total for total in self.unread.values())
            # Otherwise we care if we can see a current list of articles and
            # if there's something unread amongst them.
            return self.articles is not None and any(
                article.is_unread for article in self.articles
            )
        if action == Copy.action_name():
            return (
                (navigation := self.query_one(Navigation)).has_focus
                and navigation.current_subscription is not None
            ) or self.query_one("#article-view").has_focus_within
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

    def _refresh_article_list(self) -> None:
        """Refresh the content of the article list."""
        if self.current_category:
            self.articles = get_local_articles(self.current_category, not self.show_all)
            # If the result is there's nothing showing, tidy up the content
            # side of the display and maybe move focus back to navigation.
            if not self.articles:
                self.article = None
                if self.query_one("#article-view").has_focus_within:
                    self.query_one(Navigation).focus()
        self.query_one("#article-view").set_class(bool(self.articles), "--has-articles")

    @work(thread=True, exclusive=True)
    def _load_locally(self) -> None:
        """Load up any locally-held data."""
        if folders := get_local_folders():
            self.post_message(self.NewFolders(folders))
        if subscriptions := get_local_subscriptions():
            self.post_message(self.NewSubscriptions(subscriptions))
        if cleaned := clean_old_read_articles(
            timedelta(days=load_configuration().local_history)
        ):
            self.notify(f"Old read articles cleaned from local storage: {cleaned}")
        if unread := get_local_unread(folders, subscriptions):
            self.post_message(self.NewUnread(unread))
        self._refresh_article_list()
        # If we've never grabbed data from ToR before, or if it's been long enough...
        if (last_grabbed := last_grabbed_data_at()) is None or (
            (datetime.now() - last_grabbed).seconds
            >= load_configuration().startup_refresh_holdoff_period
        ):
            # ...kick off a refresh from TheOldReader.
            self.post_message(RefreshFromTheOldReader())

    @on(SyncFinished)
    def _sync_finished(self) -> None:
        """Clean up after a sync from TheOldReader has finished."""
        self._refresh_article_list()
        self.post_message(self.SubTitle(""))

    @on(RefreshFromTheOldReader)
    @work(exclusive=True)
    async def action_refresh_from_the_old_reader_command(self) -> None:
        """Load the main data from TheOldReader."""
        await ToRSync(
            self._session,
            on_new_step=lambda step: self.post_message(self.SubTitle(step)),
            on_new_result=lambda result: self.notify(result),
            on_new_folders=lambda folders: self.post_message(self.NewFolders(folders)),
            on_new_subscriptions=lambda subscriptions: self.post_message(
                self.NewSubscriptions(subscriptions)
            ),
            on_new_unread=lambda unread: self.post_message(self.NewUnread(unread)),
            on_sync_finished=lambda: self.post_message(self.SyncFinished()),
        ).refresh()

    @on(Navigation.CategorySelected)
    def _handle_navigaion_selection(self, message: Navigation.CategorySelected) -> None:
        """Handle a navigation selection being made.

        Args:
            message: The message to react to.
        """
        self.current_category = message.category
        self.article = None
        self._refresh_article_list()
        self.query_one(ArticleList).focus()

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

    def action_next_command(self) -> None:
        """Go to the next article in the currently-viewed category."""
        if self.article is None:
            self.query_one(ArticleList).highlight_next_article()
        else:
            self.query_one(ArticleList).select_next_article()

    def action_previous_command(self) -> None:
        """Go to the previous article in the currently-viewed category."""
        if self.article is None:
            self.query_one(ArticleList).highlight_previous_article()
        else:
            self.query_one(ArticleList).select_previous_article()

    def action_next_unread_command(self) -> None:
        """Go to the next unread article in the currently-viewed category."""
        if (navigation := self.query_one(Navigation)).has_focus:
            navigation.highlight_next_unread_category()
        elif self.article is None:
            self.query_one(ArticleList).highlight_next_unread_article()
        else:
            self.query_one(ArticleList).select_next_unread_article()

    def action_previous_unread_command(self) -> None:
        """Go to the previous unread article in the currently-viewed category"""
        if (navigation := self.query_one(Navigation)).has_focus:
            navigation.highlight_previous_unread_category()
        elif self.article is None:
            self.query_one(ArticleList).highlight_previous_unread_article()
        else:
            self.query_one(ArticleList).select_previous_unread_article()

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

    @work
    async def action_mark_all_read_command(self) -> None:
        """Mark all unread articles in the current category as read."""
        if (current_category := self.query_one(Navigation).current_category) is None:
            return
        if not (
            ids_to_mark_read := [
                article.id for article in self.articles if article.is_unread
            ]
        ):
            return
        category_description = f"{current_category.__class__.__name__.lower()} '{current_category.name if isinstance(current_category, Folder) else current_category.title}'"
        plural = "s" if len(ids_to_mark_read) > 1 else ""
        if await self.app.push_screen_wait(
            Confirm(
                "Mark all read",
                f"Are you sure you want to mark all unread articles in the {category_description} as read?\n\n"
                f"This will mark {len(ids_to_mark_read)} article{plural} as read.",
            )
        ):
            if await self._session.add_tag(ids_to_mark_read, State.READ):
                locally_mark_article_ids_read(ids_to_mark_read)
                self.post_message(
                    self.NewUnread(get_local_unread(self.folders, self.subscriptions))
                )
                self._refresh_article_list()
                self.notify(
                    f"{len(ids_to_mark_read)} article{plural} marked read for {category_description}"
                )
            else:
                self.notify(
                    "Failed to mark as read on TheOldReader",
                    severity="error",
                )

    def action_open_home_page_command(self) -> None:
        """Open the home page of the current subscription in the web browser."""
        if subscription := self.query_one(Navigation).current_subscription:
            if subscription.html_url:
                open_url(subscription.html_url)
            else:
                self.notify(
                    "No home page URL available for the subscription",
                    severity="error",
                    title="Can't visit",
                )

    def _copy_to_clipboard(self, content: str | None, empty_error: str) -> None:
        """Copy some content to the clipboard.

        Args:
            content: The content to copy to the clipboard.
            empty_error: The message to show if there's no content.
        """
        if content:
            self.app.copy_to_clipboard(content)
            self.notify("Copied to clipboard")
        else:
            self.notify(empty_error, severity="error", title="Can't copy")

    def action_copy_home_page_to_clipboard_command(self) -> None:
        """Copy the URL of the current subscription's homepage to the clipboard."""
        if subscription := self.query_one(Navigation).current_subscription:
            self._copy_to_clipboard(
                subscription.html_url, "No home page URL available for the subscription"
            )

    def action_copy_feed_to_clipboard_command(self) -> None:
        """Copy the URL of the current subscription's feed to the clipboard."""
        if subscription := self.query_one(Navigation).current_subscription:
            self._copy_to_clipboard(
                subscription.url, "No feed URL available for the subscription"
            )

    def action_copy_article_to_clipboard_command(self) -> None:
        """Copy the URL of the current article to the clipboard."""
        if self.article:
            self._copy_to_clipboard(
                self.article.html_url, "No URL available for the article"
            )

    def action_copy_command(self) -> None:
        """Copy a URL to the clipboard depending on the current context."""
        if (navigation := self.query_one(Navigation)).has_focus:
            if navigation.current_subscription:
                self.action_copy_home_page_to_clipboard_command()
        elif self.query_one("#article-view").has_focus_within:
            if self.article:
                self.action_copy_article_to_clipboard_command()
            else:
                self.action_copy_home_page_to_clipboard_command()

    @work
    async def action_add_subscription_command(self) -> None:
        """Add a new subscription feed."""
        if feed := await self.app.push_screen_wait(ModalInput("Subscription URL")):
            self.notify(feed, title="Subscription request sent to TheOldReader...")
            if (result := await Subscriptions.add(self._session, feed)).failed:
                self.notify(
                    result.error or "TheOldReader did not give a reason",
                    title="Failed to add subscription",
                    severity="error",
                    timeout=8,
                    markup=False,
                )
            else:
                self.notify("Subscription added")
                self.post_message(RefreshFromTheOldReader())

    @work
    async def action_rename_subscription_command(self) -> None:
        """Rename the current subscription."""
        if subscription := self.query_one(Navigation).current_subscription:
            if new_name := await self.app.push_screen_wait(
                ModalInput("Subscription name", subscription.title)
            ):
                if await Subscriptions.rename(self._session, subscription, new_name):
                    self.notify("Renamed")
                    self.post_message(RefreshFromTheOldReader())
                else:
                    self.notify("Rename failed", severity="error", timeout=8)


### main.py ends here
