"""Provides the main navigation widget."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import cast

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
from ._next_matching_option import Direction, next_matching_option


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
        super().__init__(prompt, id=subscription.id)

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
        HelpfulBinding("ctrl+enter", "toggle_folder", tooltip="Expand/collapse folder"),
        HelpfulBinding(
            "ctrl+right_square_bracket", "expand_all", tooltip="Expand all folders"
        ),
        HelpfulBinding(
            "ctrl+left_square_bracket", "collapse_all", tooltip="Collapse all folders"
        ),
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

    @staticmethod
    def _key(attr: str) -> Callable[[object], str]:
        """Create a key to use with `sorted`.

        Args:
            attr: The attribute to sort on.

        Returns:
            A function to get a `casefold` version of the attribute.
        """

        def _casefold(value: object) -> str:
            return cast(str, getattr(value, attr)).casefold()

        return _casefold

    def _viewable(
        self, subscriptions: Iterable[Subscription]
    ) -> Iterator[SubscriptionView]:
        """Given a iterable of subscriptions, make them viewable.

        Args:
            subscriptions: The subscriptions to make viewable.

        Yields:
            Views of the subscriptions.
        """
        yield from (
            SubscriptionView(subscription, self.unread)
            for subscription in sorted(subscriptions, key=self._key("title"))
        )

    def _gather_subscriptions_for_folder(
        self, parent_folder: Folder
    ) -> Iterator[SubscriptionView]:
        """Gather the subscriptions for a given parent folder.

        Args:
            parent_folder: The parent folder to add the subscriptions for.

        Yields:
            The subscriptions within that folder.
        """
        yield from self._viewable(
            subscription
            for subscription in self.subscriptions
            if parent_folder in subscription.categories
        )

    def _gather_folders(self) -> Iterator[FolderView | SubscriptionView]:
        """Gather up all the folders and their subscriptions.

        Yields:
            Folder and subscription options.
        """
        for folder in sorted(self.folders, key=self._key("name")):
            yield FolderView(
                folder, expanded := folder.id in self._expanded, self.unread
            )
            if expanded:
                yield from self._gather_subscriptions_for_folder(folder)

    def _gather_folderless_subscrtiptions(self) -> Iterator[SubscriptionView]:
        """Gather up all the subscriptions that don't live in a folder.

        Yields:
            Subscription options for folderless subscriptions.
        """
        yield from self._viewable(
            subscription
            for subscription in self.subscriptions
            if not subscription.categories
        )

    def _refresh_navigation(self) -> None:
        """Refresh the content of the navigation widget."""
        with self.preserved_highlight:
            self.set_options(
                (*self._gather_folderless_subscrtiptions(), *self._gather_folders())
            )

    def _watch_folders(self) -> None:
        """React to the folders being updated."""
        self._refresh_navigation()

    def _watch_subscriptions(self) -> None:
        """React to the subscriptions being updated."""
        self._refresh_navigation()

    def _watch_unread(self) -> None:
        """React to the unread data being updated."""
        self._refresh_navigation()

    @work(thread=True)
    def _save_state(self, state: set[str]) -> None:
        """Save the folder expanded/collapsed state.

        Args:
            state: The state to save.
        """
        save_navigation_state(state)

    def _set_expansion(self, new_state: set[str]) -> None:
        """Set the new navigation state.

        Args:
            new_state: The new state to set.
        """
        self._expanded = new_state
        self._save_state(new_state)
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
            self._set_expansion(self._expanded ^ {option.folder.id})

    def _action_expand_all(self) -> None:
        """Action that expands all folders."""
        self._set_expansion({folder.id for folder in self.folders})

    def _action_collapse_all(self) -> None:
        """Action that collapses all folders."""
        self._set_expansion(set())

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

    @property
    def current_folder(self) -> Folder | None:
        """The current folder, if one is highlighted, or `None`"""
        if isinstance(current := self.current_category, Folder):
            return current
        return None

    @property
    def current_subscription(self) -> Subscription | None:
        """The current subscription, if one is highlighted, or `None`."""
        if isinstance(current := self.current_category, Subscription):
            return current
        return None

    def _contains_unread(self, category: FolderView | SubscriptionView) -> bool:
        """Does the given folder or subscription have unread items?

        Args:
            category: The folder or subscription to check.

        Returns:
            `True` if there are unread items, `False` if not.
        """
        return bool(category.id and self.unread.get(category.id))

    def _highlight_unread(self, direction: Direction) -> bool:
        """Highlight the next category with unread articles, if there is one.

        Args:
            direction: The direction to search.

        Returns:
            `True` if an unread category was found and highlighted, `False`
            if not.
        """
        if (
            next_hit := next_matching_option(
                cast(list[FolderView | SubscriptionView], self.options),
                self.highlighted,
                direction,
                self._contains_unread,
            )
        ) and next_hit.id is not None:
            self.highlighted = self.get_option_index(next_hit.id)
            return True
        self.notify("No more folders or subscriptions with unread articles")
        return False

    def highlight_next_unread_category(self) -> None:
        """Highlight the next unread category."""
        self._highlight_unread("forward")

    def highlight_previous_unread_category(self) -> None:
        """Highlight the previous unread category."""
        self._highlight_unread("backward")


### navigation.py ends here
