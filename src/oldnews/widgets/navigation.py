"""Provides the main navigation widget."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from operator import attrgetter

##############################################################################
# OldAs imports.
from oldas import Folder, Folders, Subscription, Subscriptions, Unread

##############################################################################
# Rich imports.
from rich.console import Group
from rich.markup import escape
from rich.rule import Rule
from rich.table import Table

##############################################################################
# Textual imports.
from textual import on
from textual.message import Message
from textual.reactive import var
from textual.widgets.option_list import Option

##############################################################################
# Textual enhanced imports.
from textual_enhanced.widgets import EnhancedOptionList


##############################################################################
def _unread(item_id: str, type_getter: attrgetter, counts: Unread | None) -> int:
    """Get the given unread count for a given item.

    Args:
        item_id: The ID of the item to get the count for.
        type_getter: The getter for the type of unread item.
        counts: The unread counts.

    Returns:
        The unread count.
    """
    if counts is None:
        return 0
    count = [item for item in type_getter(counts) if item.id == item_id and item.unread]
    return count[0].unread if count else 0


##############################################################################
class FolderView(Option):
    """The view of a folder within the navigation widget."""

    def __init__(self, folder: Folder, expanded: bool, counts: Unread | None) -> None:
        """Initialise the folder view object.

        Args:
            folder: The folder to view.
            expanded: Should we show as being expanded?
            counts: The unread counts.
        """
        self._folder = folder
        """The folder we're viewing."""
        style = "bold dim"
        if unread := _unread(folder.id, attrgetter("folders"), counts):
            style = "bold"
        prompt = Table.grid(expand=True)
        prompt.add_column(width=2)
        prompt.add_column(ratio=1)
        prompt.add_column(width=1)
        prompt.add_column()
        prompt.add_row(
            "▼" if expanded else "▶",
            f"[{style}]{escape(folder.name)}[/]",
            "",
            str(unread) if unread else "",
        )
        super().__init__(
            Group(rule := Rule(style="dim"), prompt, rule) if expanded else prompt,
            id=folder.id,
        )

    @property
    def folder(self) -> Folder:
        """The folder we're viewing."""
        return self._folder


##############################################################################
class SubscriptionView(Option):
    """The view of a subscription within the navigation widget."""

    def __init__(self, subscription: Subscription, counts: Unread | None) -> None:
        """Initialise the subscription view object.

        Args:
            subscription: The subscription we're viewing.
            counts: The unread counts.
        """
        self._subscription = subscription
        """The subscription we're viewing."""
        style = "dim"
        if unread := _unread(subscription.id, attrgetter("feeds"), counts):
            style = f"not {style}"
        prompt = Table.grid(expand=True)
        prompt.add_column(width=2)
        prompt.add_column(ratio=1)
        prompt.add_column(width=1)
        prompt.add_column()
        prompt.add_row(
            "",
            f"[{style}]{escape(subscription.title)}[/]",
            "",
            str(unread) if unread else "",
        )
        super().__init__(prompt)

    @property
    def subscription(self) -> Subscription:
        """The subscription we're viewing."""
        return self._subscription


##############################################################################
class Navigation(EnhancedOptionList):
    """The main navigation widget."""

    folders: var[Folders] = var(Folders)
    """The folders that subscriptions are assigned to."""
    subscriptions: var[Subscriptions] = var(Subscriptions)
    """The list of subscriptions."""
    unread: var[Unread | None] = var(None)
    """The unread counts."""

    @dataclass
    class FolderSelected(Message):
        """Message sent when a folder is selected."""

        folder: Folder
        """The folder that was selected."""

    @dataclass
    class SubscriptionSelected(Message):
        """Message sent when a subscription is selected."""

        subscription: Subscription
        """The subscription that as selected."""

    def __init__(self, id: str | None = None, classes: str | None = None):
        """Initialise the navigation object.

        Args:
            id: The ID of the navigation widget in the DOM.
            classes: The CSS classes of the navigation widget.
        """
        super().__init__(id=id, classes=classes)
        self._expanded: set[str] = set()
        """The IDs of the folders that are expanded."""

    def _add_subscriptions(self, parent_folder: str) -> None:
        """Add the subscriptions for a given parent folder.

        Args:
            parent_folder: The parent folder to add the subscriptions for.
        """
        for subscription in self.subscriptions:
            if any(
                category.id == parent_folder for category in subscription.categories
            ):
                self.add_option(SubscriptionView(subscription, self.unread))

    def _add_folder(self, folder: Folder) -> None:
        """Add the given folder to the navigation.

        Args:
            folder: The folder to add.
        """
        self.add_option(
            FolderView(folder, expanded := folder.id in self._expanded, self.unread)
        )
        if expanded:
            self._add_subscriptions(folder.id)

    def _refresh_navigation(self) -> None:
        """Refresh the content of the navigation widget."""
        with self.preserved_highlight:
            self.clear_options()
            for folder in self.folders:
                self._add_folder(folder)

    def _watch_folders(self) -> None:
        """React to the folders being updated."""
        self._refresh_navigation()

    def _watch_subscriptions(self) -> None:
        """React to the subscriptions being updated."""
        self._refresh_navigation()

    def _watch_unread(self) -> None:
        """React to the unread data being updated."""
        self._refresh_navigation()

    def _select_folder(self, view: FolderView) -> None:
        """Perform the selection action for the given folder.

        Args:
            view: The folder we're viewing.
        """
        if view.folder.id is not None:
            self._expanded ^= {view.folder.id}
            self._refresh_navigation()

    @on(EnhancedOptionList.OptionSelected)
    def _handle_selection(self, message: EnhancedOptionList.OptionSelected) -> None:
        """Handle an item in the navigation widget being selected.

        Args:
            message: The message to handle.
        """
        message.stop()
        if isinstance(message.option, FolderView):
            self.post_message(self.FolderSelected(message.option.folder))
            self._select_folder(message.option)
        elif isinstance(message.option, SubscriptionView):
            self.post_message(self.SubscriptionSelected(message.option.subscription))


### navigation.py ends here
