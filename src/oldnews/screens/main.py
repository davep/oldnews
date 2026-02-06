"""Provides the main screen."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from webbrowser import open as open_url

##############################################################################
# BagOfStuff imports.
from bagofstuff.pipe import Pipe

##############################################################################
# Humanize imports.
from humanize import intcomma

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
from textual.getters import query_one
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
    Information,
    MarkAllRead,
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
from ..data import (
    LocalUnread,
    clean_old_read_articles,
    data_dump,
    get_local_articles,
    get_local_folders,
    get_local_subscriptions,
    get_local_unread,
    last_grabbed_data_at,
    load_configuration,
    locally_mark_article_ids_read,
    locally_mark_read,
    move_subscription_articles,
    remove_folder_from_articles,
    remove_subscription_articles,
    rename_folder_for_articles,
    total_unread,
    update_configuration,
)
from ..providers import MainCommands
from ..sync import TheOldReaderSync
from ..widgets import ArticleContent, ArticleList, Navigation
from .folder_input import FolderInput
from .information_display import InformationDisplay
from .new_subscription import NewSubscription
from .process_subscription import ProcessSubscription


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
        AddSubscription,
        ChangeTheme,
        Copy,
        CopyArticleToClipboard,
        CopyFeedToClipboard,
        CopyHomePageToClipboard,
        Escape,
        Information,
        MarkAllRead,
        MoveSubscription,
        Next,
        NextUnread,
        OpenArticle,
        OpenHomePage,
        Previous,
        PreviousUnread,
        Remove,
        Rename,
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

    navigation = query_one(Navigation)
    """The navigation panel."""
    article_view = query_one("#article-view", Vertical)
    """The panel that contains views of articles."""
    article_list = query_one(ArticleList)
    """The article list panel."""
    article_content = query_one(ArticleContent)
    """The article content panel."""

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
            MoveSubscription.action_name(),
        ):
            return self.navigation.current_subscription is not None
        if action in (Next.action_name(), Previous.action_name()):
            return self.articles is not None
        if action in (
            NextUnread.action_name(),
            PreviousUnread.action_name(),
            MarkAllRead.action_name(),
        ):
            # If we're inside the navigation panel...
            if self.navigation.has_focus:
                # ...we just care if there's anything unread somewhere.
                return any(self.unread.values())
            # Otherwise we care if we can see a current list of articles and
            # if there's something unread amongst them.
            return self.articles is not None and any(
                article.is_unread for article in self.articles
            )
        if action == Copy.action_name():
            return (
                self.navigation.has_focus
                and self.navigation.current_subscription is not None
            ) or self.article_view.has_focus_within
        if action == Information.action_name():
            return (
                self.navigation.has_focus
                and self.navigation.current_category is not None
            ) or (self.article_view.has_focus_within and self.article is not None)
        if action in (Rename.action_name(), Remove.action_name()):
            return self.navigation.current_category is not None
        return True

    @on(SubTitle)
    def _update_sub_title(self, message: SubTitle) -> None:
        """Handle a request to set the sub-title to something.

        Args:
            message: The message requesting the sub-title be updated.
        """
        self.sub_title = (
            message.title
            if message.title
            else f"{intcomma(total_unread(self.unread))} unread"
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
        self.post_message(self.SubTitle())

    async def _refresh_article_list(self) -> None:
        """Refresh the content of the article list."""
        if self.current_category:
            self.articles = await get_local_articles(
                self.current_category, not self.show_all
            )
            # If the result is there's nothing showing, tidy up the content
            # side of the display and maybe move focus back to navigation.
            if not self.articles:
                self.article = None
                if self.article_view.has_focus_within:
                    self.navigation.focus()
        self.article_view.set_class(bool(self.articles), "--has-articles")

    @work(exclusive=True)
    async def _load_locally(self) -> None:
        """Load up any locally-held data."""
        if subscriptions := await get_local_subscriptions():
            self.post_message(self.NewSubscriptions(subscriptions))
        if folders := await get_local_folders():
            self.post_message(self.NewFolders(folders))
        if cleaned := await clean_old_read_articles(
            timedelta(days=load_configuration().local_history)
        ):
            self.notify(f"Old read articles cleaned from local storage: {cleaned}")
        if unread := await get_local_unread(folders, subscriptions):
            self.post_message(self.NewUnread(unread))
        await self._refresh_article_list()
        # If we've never grabbed data from ToR before, or if it's been long enough...
        if (last_grabbed := await last_grabbed_data_at()) is None or (
            (datetime.now(UTC) - last_grabbed).seconds
            >= load_configuration().startup_refresh_holdoff_period
        ):
            # ...kick off a refresh from TheOldReader.
            self.post_message(RefreshFromTheOldReader())

    @on(SyncFinished)
    async def _sync_finished(self) -> None:
        """Clean up after a sync from TheOldReader has finished."""
        await self._refresh_article_list()
        self.post_message(self.SubTitle())

    @on(RefreshFromTheOldReader)
    @work(exclusive=True)
    async def action_refresh_from_the_old_reader_command(self) -> None:
        """Load the main data from TheOldReader."""
        await TheOldReaderSync(
            self._session,
            on_new_step=Pipe[str, bool](self.SubTitle, self.post_message),
            on_new_result=self.notify,
            on_new_folders=Pipe[Folders, bool](self.NewFolders, self.post_message),
            on_new_subscriptions=Pipe[Subscriptions, bool](
                self.NewSubscriptions, self.post_message
            ),
            on_new_unread=Pipe[LocalUnread, bool](self.NewUnread, self.post_message),
            on_sync_finished=Pipe[Pipe.Nullary, bool](
                self.SyncFinished, self.post_message
            ),
        ).sync()

    @on(Navigation.CategorySelected)
    async def _handle_navigaion_selection(
        self, message: Navigation.CategorySelected
    ) -> None:
        """Handle a navigation selection being made.

        Args:
            message: The message to react to.
        """
        self.current_category = message.category
        self.article = None
        await self._refresh_article_list()
        self.article_list.focus()

    async def _watch_show_all(self) -> None:
        """Handle changes to the show all flag."""
        await self._refresh_article_list()

    @work
    async def _mark_read(self, article: Article) -> None:
        """Mark the given article as read.

        Args:
            article: The article to mark as read.
        """
        await locally_mark_read(article)
        self.post_message(
            self.NewUnread(await get_local_unread(self.folders, self.subscriptions))
        )
        await self._refresh_article_list()
        await article.mark_read(self._session)

    @on(ArticleList.ViewArticle)
    def _view_article(self, message: ArticleList.ViewArticle) -> None:
        """Handle a request to view an article.

        Args:
            message: The message requesting an article be viewed.
        """
        self.article = message.article
        self.article_content.focus()
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
        if self.focused is not None and self.focused.parent is self.article_content:
            self.article_list.focus()
            self.article = None
        elif self.focused is self.article_list:
            self.navigation.focus()
        elif self.focused is self.navigation:
            self.app.exit()

    def action_next_command(self) -> None:
        """Go to the next article in the currently-viewed category."""
        if self.article is None:
            self.article_list.highlight_next_article()
        else:
            self.article_list.select_next_article()

    def action_previous_command(self) -> None:
        """Go to the previous article in the currently-viewed category."""
        if self.article is None:
            self.article_list.highlight_previous_article()
        else:
            self.article_list.select_previous_article()

    def action_next_unread_command(self) -> None:
        """Go to the next unread article in the currently-viewed category."""
        if self.navigation.has_focus:
            self.navigation.highlight_next_unread_category()
        elif self.article is None:
            self.article_list.highlight_next_unread_article()
        else:
            self.article_list.select_next_unread_article()

    def action_previous_unread_command(self) -> None:
        """Go to the previous unread article in the currently-viewed category"""
        if self.navigation.has_focus:
            self.navigation.highlight_previous_unread_category()
        elif self.article is None:
            self.article_list.highlight_previous_unread_article()
        else:
            self.article_list.select_previous_unread_article()

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
        if (current_category := self.navigation.current_category) is None:
            return
        if not (
            ids_to_mark_read := [
                article.id for article in self.articles if article.is_unread
            ]
        ):
            return
        category_description = (
            f"{current_category.__class__.__name__.lower()} "
            f"'{current_category.name if isinstance(current_category, Folder) else current_category.title}'"
        )
        plural = "s" if len(ids_to_mark_read) > 1 else ""
        if await self.app.push_screen_wait(
            Confirm(
                "Mark all read",
                f"Are you sure you want to mark all unread articles in the {category_description} as read?\n\n"
                f"This will mark {len(ids_to_mark_read)} article{plural} as read.",
            )
        ):
            if await self._session.add_tag(ids_to_mark_read, State.READ):
                await locally_mark_article_ids_read(ids_to_mark_read)
                self.post_message(
                    self.NewUnread(
                        await get_local_unread(self.folders, self.subscriptions)
                    )
                )
                await self._refresh_article_list()
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
        if subscription := self.navigation.current_subscription:
            if subscription.html_url:
                open_url(subscription.html_url)
            else:
                self.notify(
                    "No home page URL available for the subscription",
                    severity="error",
                    title="Can't visit",
                )

    def _copy_to_clipboard(
        self, content: str | None, empty_error: str, source: str = ""
    ) -> None:
        """Copy some content to the clipboard.

        Args:
            content: The content to copy to the clipboard.
            empty_error: The message to show if there's no content.
        """
        if content:
            self.app.copy_to_clipboard(content)
            self.notify("Copied to clipboard", title=source)
        else:
            self.notify(empty_error, severity="error", title="Can't copy")

    def action_copy_home_page_to_clipboard_command(self) -> None:
        """Copy the URL of the current subscription's homepage to the clipboard."""
        if subscription := self.navigation.current_subscription:
            self._copy_to_clipboard(
                subscription.html_url,
                "No home page URL available for the subscription",
                "Home page URL",
            )

    def action_copy_feed_to_clipboard_command(self) -> None:
        """Copy the URL of the current subscription's feed to the clipboard."""
        if subscription := self.navigation.current_subscription:
            self._copy_to_clipboard(
                subscription.url,
                "No feed URL available for the subscription",
                "Feed URL",
            )

    def action_copy_article_to_clipboard_command(self) -> None:
        """Copy the URL of the current article to the clipboard."""
        if self.article:
            self._copy_to_clipboard(
                self.article.html_url, "No URL available for the article", "Article URL"
            )

    def action_copy_command(self) -> None:
        """Copy a URL to the clipboard depending on the current context."""
        if (navigation := self.navigation).has_focus:
            if navigation.current_subscription:
                self.action_copy_home_page_to_clipboard_command()
        elif self.article_view.has_focus_within:
            if self.article:
                self.action_copy_article_to_clipboard_command()
            else:
                self.action_copy_home_page_to_clipboard_command()

    @work
    async def action_add_subscription_command(self) -> None:
        """Add a new subscription feed."""
        if subscription := await self.app.push_screen_wait(
            NewSubscription(self.folders)
        ):
            if (
                result := await self.app.push_screen_wait(
                    ProcessSubscription(self._session, subscription)
                )
            ).failed:
                self.notify(
                    result.error or "TheOldReader did not give a reason",
                    title="Failed to add subscription",
                    severity="error",
                    timeout=8,
                    markup=False,
                )
            else:
                self.notify("Subscription added")
                if result.stream_id and subscription.folder:
                    self.notify(f"Moving new subscription into '{subscription.folder}'")
                    if await Subscriptions.move(
                        self._session, result.stream_id, subscription.folder
                    ):
                        self.notify("Moved")
                    else:
                        self.notify(
                            f"Could not move the new subscription into '{subscription.folder}'",
                            title="Move failed",
                            timeout=8,
                            markup=False,
                        )
                self.post_message(RefreshFromTheOldReader())

    @work
    async def _rename_subscription(self, subscription: Subscription) -> None:
        """Rename the given subscription

        Args:
            subscription: The subscription to rename.
        """
        if new_name := await self.app.push_screen_wait(
            ModalInput("Subscription name", subscription.title)
        ):
            if await Subscriptions.rename(self._session, subscription, new_name):
                self.notify("Renamed")
                self.post_message(RefreshFromTheOldReader())
            else:
                self.notify("Rename failed", severity="error", timeout=8)

    @work
    async def _rename_folder(self, folder: Folder) -> None:
        """Rename the given subscription

        Args:
            subscription: The subscription to rename.
        """
        if new_name := await self.app.push_screen_wait(
            ModalInput("Subscription name", folder.name)
        ):
            if await Folders.rename(self._session, folder, new_name):
                await rename_folder_for_articles(folder, new_name)
                self.notify("Renamed")
                self.post_message(RefreshFromTheOldReader())
            else:
                self.notify("Rename failed", severity="error", timeout=8)

    def action_rename_command(self) -> None:
        """Rename the current subscription."""
        if category := self.navigation.current_category:
            if isinstance(category, Subscription):
                self._rename_subscription(category)
            elif isinstance(category, Folder):
                self._rename_folder(category)

    @work
    async def _remove_subscription(self, subscription: Subscription) -> None:
        """Remove the given subscription.

        Args:
            subscription: The subscription to remove
        """
        if await self.app.push_screen_wait(
            Confirm(
                f"Remove {subscription.title}?",
                "Are you sure you wish to remove the subscription?",
            )
        ):
            if await Subscriptions.remove(self._session, subscription):
                await remove_subscription_articles(subscription)
                self.notify(f"Removed {subscription.title}")
                self.post_message(RefreshFromTheOldReader())
            else:
                self.notify("Remove failed", severity="error", timeout=8)

    @work
    async def _remove_folder(self, folder: Folder) -> None:
        """Remove the given folder.

        Args:
            folder: The folder to remove
        """
        if await self.app.push_screen_wait(
            Confirm(
                f"Remove {folder.name}", "Are you sure you wish to remove the folder?"
            )
        ):
            if await Folders.remove(self._session, folder):
                await remove_folder_from_articles(folder)
                self.notify(f"Removed {folder.name}")
                self.post_message(RefreshFromTheOldReader())
            else:
                self.notify("Remove failed", severity="error", timeout=8)

    def action_remove_command(self) -> None:
        """Remove the current folder or subscription."""
        if category := self.navigation.current_category:
            if isinstance(category, Subscription):
                self._remove_subscription(category)
            elif isinstance(category, Folder):
                self._remove_folder(category)

    @work
    async def action_move_subscription_command(self) -> None:
        """Move a subscription to a different folder."""
        if not (subscription := self.navigation.current_subscription):
            return
        if (
            target_folder := await self.app.push_screen_wait(FolderInput(self.folders))
        ) is not None:
            if await Subscriptions.move(self._session, subscription, target_folder):
                await move_subscription_articles(
                    subscription, subscription.folder_id, target_folder
                )
                self.notify("Moved")
                self.post_message(RefreshFromTheOldReader())
            else:
                self.notify(
                    f"Could not move the subscription into '{target_folder}'",
                    title="Move failed",
                    timeout=8,
                    markup=False,
                )

    @work
    async def action_information_command(self) -> None:
        """Show some information about the current item."""
        information: InformationDisplay | None = None
        if self.navigation.has_focus and (category := self.navigation.current_category):
            information = InformationDisplay(
                category.__class__.__name__, data_dump(category)
            )
        elif self.article_view.has_focus_within and self.article:
            information = InformationDisplay("Article", data_dump(self.article))
        if information:
            await self.app.push_screen_wait(information)


### main.py ends here
