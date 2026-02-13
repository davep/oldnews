"""Provides the main screen."""

##############################################################################
# Python imports.
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import partial
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
    User,
)

##############################################################################
# Pyperclip imports.
from pyperclip import PyperclipException
from pyperclip import copy as to_clipboard

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.getters import query_one
from textual.message import Message
from textual.reactive import var
from textual.widgets import Footer, Header
from textual.worker import Worker

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
    SetSubscriptionContentFilter,
    ToggleCompact,
    ToggleShowAll,
    UserInformation,
)
from ..data import (
    LocalUnread,
    clean_old_read_articles,
    data_dump,
    get_content_grab_filter_for,
    get_local_articles,
    get_local_folders,
    get_local_subscriptions,
    get_local_unread,
    last_grabbed_data_at,
    load_configuration,
    locally_mark_article_ids_read,
    locally_mark_read,
    locally_mark_unread,
    move_subscription_articles,
    remove_folder_from_articles,
    remove_subscription_articles,
    rename_folder_for_articles,
    rename_folder_in_navigation_state,
    set_content_grab_filter_for,
    total_unread,
    update_configuration,
)
from ..providers import MainCommands
from ..sync import TheOldReaderSync
from ..widgets import (
    ArticleContent,
    ArticleList,
    ArticleListHeader,
    ArticleView,
    Navigation,
)
from .information_display import InformationDisplay
from .move_subscription import MoveSubscriptionTo
from .new_subscription import NewSubscription
from .process_subscription import ProcessSubscription
from .subscription_content_filter import SubscriptionContentFilter


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
            pointer: default; /* https://github.com/Textualize/textual/issues/6349 */
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
        AddSubscription,
        ChangeTheme,
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
        Remove,
        Rename,
        UserInformation,
        ToggleCompact,
        SetSubscriptionContentFilter,
    ]

    BINDINGS = Command.bindings(*COMMAND_MESSAGES)

    COMMANDS = {MainCommands}

    folders: var[Folders] = var(Folders)
    """The folders that subscriptions are assigned to."""
    subscriptions: var[Subscriptions] = var(Subscriptions)
    """The list of subscriptions."""
    selected_category: var[Folder | Subscription | None] = var(None)
    """The navigation category that is currently selected."""
    unread: var[LocalUnread] = var(LocalUnread)
    """The unread counts."""
    articles: var[Articles] = var(Articles)
    """The currently-viewed list of articles."""
    article: var[Article | None] = var(None)
    """The currently-viewed article."""
    show_all: var[bool] = var(False)
    """Should we show all articles or only new?"""
    compact_ui: var[bool] = var(False)
    """Should we try and make the UI as compact as possible?"""

    navigation = query_one(Navigation)
    """The navigation panel."""
    article_view = query_one(ArticleView)
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
            Main.folders, Main.subscriptions, Main.unread, Main.compact_ui
        )
        with ArticleView().data_bind(Main.articles):
            yield ArticleListHeader().data_bind(Main.selected_category, Main.compact_ui)
            yield ArticleList(classes="panel").data_bind(
                Main.articles, Main.selected_category, Main.compact_ui
            )
            yield ArticleContent().data_bind(Main.article, Main.compact_ui)
        yield Footer()

    def on_mount(self) -> None:
        """Configure the application once the DOM is mounted."""
        self.show_all = load_configuration().show_all
        self.compact_ui = load_configuration().compact_ui
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
            SetSubscriptionContentFilter.action_name(),
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
        if action in (
            Information.action_name(),
            Rename.action_name(),
            Remove.action_name(),
        ):
            return self._current_category_in_context is not None
        if action in (MarkRead.action_name(), MarkUnread.action_name()):
            return self.article_view.has_focus_within and bool(
                self.article or self.article_list.highlighted_article
            )
        if action == UserInformation.action_name():
            return self._session.logged_in
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
        if self.selected_category:
            self.articles = await get_local_articles(
                self.selected_category, not self.show_all
            )
            # If the result is there's nothing showing, tidy up the content
            # side of the display and maybe move focus back to navigation.
            if not self.articles:
                self.article = None
                if self.article_view.has_focus_within:
                    self.navigation.focus()

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
        # Ensure the selected category (if there is one) is refreshed
        # because it could be that a folder or subscription got renamed.
        if self.selected_category:
            self.selected_category = self.navigation.current_category
        # Ensure that any article list that is showing gets a refresh.
        await self._refresh_article_list()
        # Put the title of the application in its default state.
        self.post_message(self.SubTitle())

    @on(RefreshFromTheOldReader)
    @work(exclusive=True)
    async def action_refresh_from_the_old_reader_command(self) -> None:
        """Load the main data from TheOldReader."""
        await TheOldReaderSync(
            self._session,
            on_new_step=Pipe[str, bool](self.SubTitle, self.post_message),
            on_new_result=partial(self.notify, markup=False),
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
        self.selected_category = message.category
        self.article = None
        await self._refresh_article_list()
        self.article_list.focus()

    async def _watch_show_all(self) -> None:
        """Handle changes to the show all flag."""
        await self._refresh_article_list()

    @work
    async def _remotely_mark_read(self, article: Article) -> None:
        """Mark an article as read on the TheOldReader server.

        Args:
            article: The article to mark as read.
        """
        await article.mark_read(self._session)

    @work
    async def _remotely_mark_unread(self, article: Article) -> None:
        """Mark an article as unread on the TheOldReader server.

        Args:
            article: The article to mark as unread.
        """
        await article.mark_unread(self._session)

    async def _mark(
        self,
        locally_mark: Callable[[Article], Awaitable[None]],
        remotely_mark: Callable[[Article], Worker[None]],
        article: Article,
    ) -> None:
        """Mark an article with the given methods and then update the display.

        Args:
            locally_mark: The function to locally mark the article.
            remotely_mark: The function to locally mark the article.
            article: The article to mark.
        """
        remotely_mark(article)
        await locally_mark(article)
        self.post_message(
            self.NewUnread(await get_local_unread(self.folders, self.subscriptions))
        )
        await self._refresh_article_list()

    async def _mark_read(self, article: Article) -> None:
        """Mark the given article as read.

        Args:
            article: The article to mark as read.
        """
        await self._mark(locally_mark_read, self._remotely_mark_read, article)

    async def _mark_unread(self, article: Article) -> None:
        """Mark the given article as unread.

        Args:
            article: The article to mark as unread.
        """
        await self._mark(locally_mark_unread, self._remotely_mark_unread, article)

    @on(ArticleContent.Displayed)
    async def _article_in_view(self, message: ArticleContent.Displayed) -> None:
        """Do some work once an article has been shown.

        Args:
            message: The message letting us known which article was displayed.
        """
        self.article_content.focus()
        await self._mark_read(message.article)

    @on(ArticleList.ViewArticle)
    def _view_article(self, message: ArticleList.ViewArticle) -> None:
        """Handle a request to view an article.

        Args:
            message: The message requesting an article be viewed.
        """
        self.article = message.article

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
        if self.selected_category is None:
            return
        if not (
            ids_to_mark_read := [
                article.id for article in self.articles if article.is_unread
            ]
        ):
            return
        category_name = (
            self.selected_category.name
            if isinstance(self.selected_category, Folder)
            else self.selected_category.title
        )
        category_description = (
            f"{self.selected_category.__class__.__name__.lower()} '{category_name}'"
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
                    f"{intcomma(len(ids_to_mark_read))} article{plural} marked read for {category_description}",
                    markup=False,
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
            # Copy the link to the clipboard using Textual's own facility;
            # this has the benefit of pushing it through remote connections,
            # where possible.
            self.app.copy_to_clipboard(content)
            # Having done that copy, we'll also try and use pyperclip too.
            # It's possible the user is within a Terminal that doesn't
            # support the Textual approach, so this will belt-and-braces
            # make sure the link gets to some clipboard.
            try:
                to_clipboard(content)
            except PyperclipException:
                pass
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
                    self.notify(
                        f"Moving new subscription into '{subscription.folder}'",
                        markup=False,
                    )
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
                await rename_folder_in_navigation_state(folder, new_name)
                self.notify("Renamed")
                self.post_message(RefreshFromTheOldReader())
            else:
                self.notify("Rename failed", severity="error", timeout=8)

    @property
    def _current_category_in_context(self) -> Folder | Subscription | None:
        """The current category, depending on the user's focus."""
        if self.article_view.has_focus_within:
            return self.selected_category
        return self.navigation.current_category

    def action_rename_command(self) -> None:
        """Rename the current subscription."""
        if category := self._current_category_in_context:
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
                self.notify(f"Removed {subscription.title}", markup=False)
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
        if category := self._current_category_in_context:
            if isinstance(category, Subscription):
                self._remove_subscription(category)
            elif isinstance(category, Folder):
                self._remove_folder(category)

    @work
    async def action_move_subscription_command(self) -> None:
        """Move a subscription to a different folder."""
        if not isinstance(
            subscription := self._current_category_in_context, Subscription
        ):
            return
        if (
            target_folder := await self.app.push_screen_wait(
                MoveSubscriptionTo(subscription, self.folders)
            )
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
        if self.article_content.has_focus_within and self.article:
            information = InformationDisplay("Article", data_dump(self.article))
        elif self.article_list.has_focus and self.article_list.selected_category:
            information = InformationDisplay(
                self.article_list.selected_category.__class__.__name__,
                data_dump(self.article_list.selected_category),
            )
        elif self._current_category_in_context:
            information = InformationDisplay(
                self._current_category_in_context.__class__.__name__,
                data_dump(self._current_category_in_context),
            )
        if information:
            await self.app.push_screen_wait(information)

    async def action_mark_read_command(self) -> None:
        """Mark the current article as read."""
        if article := self.article or self.article_list.highlighted_article:
            await self._mark_read(article)

    async def action_mark_unread_command(self) -> None:
        """Mark the current article as unread."""
        if article := self.article or self.article_list.highlighted_article:
            await self._mark_unread(article)

    async def action_user_information_command(self) -> None:
        """Show information about the logged-in user."""
        self.app.push_screen(
            InformationDisplay(
                "Current User Information", data_dump(await User.load(self._session))
            )
        )

    def action_toggle_compact_command(self) -> None:
        """Toggle a more compact user interface."""
        with update_configuration() as config:
            config.compact_ui = not config.compact_ui
            self.compact_ui = config.compact_ui

    @work
    async def action_set_subscription_content_filter_command(self) -> None:
        """Set a subscription's content filter when grabbing more content."""
        if (
            isinstance(subscription := self._current_category_in_context, Subscription)
            and (
                new_filter := await self.app.push_screen_wait(
                    SubscriptionContentFilter(
                        subscription,
                        (await get_content_grab_filter_for(subscription)) or "",
                    )
                )
            )
            is not None
        ):
            await set_content_grab_filter_for(subscription, new_filter)
            if new_filter:
                self.notify(
                    f"Content grab filter for {subscription.title} set to {new_filter}",
                    title="Filter set",
                    markup=False,
                )
            else:
                self.notify(
                    f"Content grab filter for {subscription.title} removed",
                    markup=False,
                )


### main.py ends here
