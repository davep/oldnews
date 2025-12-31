"""Provides the main navigation widget."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# OldAs imports.
from oldas import Folder, Folders, Subscription, Subscriptions

##############################################################################
# Rich imports.
from rich.console import Group
from rich.markup import escape
from rich.rule import Rule
from rich.table import Table

##############################################################################
# Textual imports.
from textual import on, work
from textual.message import Message
from textual.reactive import var
from textual.widgets.option_list import Option

##############################################################################
# Textual enhanced imports.
from textual_enhanced.binding import HelpfulBinding
from textual_enhanced.widgets import EnhancedOptionList

##############################################################################
# Local imports.
from ..data import LocalUnread, get_navigation_state, save_navigation_state


##############################################################################
class FolderView(Option):
    """The view of a folder within the navigation widget."""

    def __init__(self, folder: Folder, expanded: bool, counts: LocalUnread) -> None:
        """Initialise the folder view object.

        Args:
            folder: The folder to view.
            expanded: Should we show as being expanded?
            counts: The unread counts.
        """
        self._folder = folder
        """The folder we're viewing."""
        style = "bold dim"
        if unread := counts.get(folder.id, 0):
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

    def __init__(self, subscription: Subscription, counts: LocalUnread) -> None:
        """Initialise the subscription view object.

        Args:
            subscription: The subscription we're viewing.
            counts: The unread counts.
        """
        self._subscription = subscription
        """The subscription we're viewing."""
        style = "dim"
        if unread := counts.get(subscription.id, 0):
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

    HELP = """
    ## Navigation

    This panel shows the folders and subscriptions.
    """

    BINDINGS = [
        HelpfulBinding("ctrl+enter", "toggle_folder", tooltip="Expand/collapse folder")
    ]

    folders: var[Folders] = var(Folders)
    """The folders that subscriptions are assigned to."""
    subscriptions: var[Subscriptions] = var(Subscriptions)
    """The list of subscriptions."""
    unread: var[LocalUnread] = var(LocalUnread)
    """The unread counts."""

    @dataclass
    class CategorySelected(Message):
        """Message sent when some sort of category is selected."""

        category: Folder | Subscription
        """The category that was selected."""

    def __init__(self, id: str | None = None, classes: str | None = None):
        """Initialise the navigation object.

        Args:
            id: The ID of the navigation widget in the DOM.
            classes: The CSS classes of the navigation widget.
        """
        super().__init__(id=id, classes=classes)
        self._expanded = get_navigation_state()
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

    def _action_toggle_folder(self) -> None:
        """Action that toggles the expanded state of a folder."""
        if self.highlighted is None:
            return
        if not isinstance(
            option := self.get_option_at_index(self.highlighted), FolderView
        ):
            self.notify("Only folders can be collapsed/expanded", severity="warning")
            return
        if option.folder.id is not None:
            self._expanded ^= {option.folder.id}
            self._save_state()
            self._refresh_navigation()

    @work(thread=True)
    def _save_state(self) -> None:
        """Save the folder expanded/collapsed state."""
        save_navigation_state(self._expanded)

    @on(EnhancedOptionList.OptionSelected)
    def _handle_selection(self, message: EnhancedOptionList.OptionSelected) -> None:
        """Handle an item in the navigation widget being selected.

        Args:
            message: The message to handle.
        """
        message.stop()
        if isinstance(message.option, FolderView):
            self.post_message(self.CategorySelected(message.option.folder))
        elif isinstance(message.option, SubscriptionView):
            self.post_message(self.CategorySelected(message.option.subscription))

    @property
    def current_category(self) -> Folder | Subscription | None:
        """The current category that is highlighted, if any."""
        if self.highlighted is None:
            return None
        selected = self.get_option_at_index(self.highlighted)
        if isinstance(selected, FolderView):
            return selected.folder
        if isinstance(selected, SubscriptionView):
            return selected.subscription
        raise ValueError("Unknown category")


### navigation.py ends here
