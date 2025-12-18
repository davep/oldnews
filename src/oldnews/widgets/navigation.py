"""Provides the main navigation widget."""

##############################################################################
# OldAs imports.
from oldas import Folder, Folders, Subscription, Subscriptions, Unread

##############################################################################
# Textual imports.
from textual import on
from textual.reactive import var
from textual.widgets.option_list import Option

##############################################################################
# Textual enhanced imports.
from textual_enhanced.widgets import EnhancedOptionList


##############################################################################
class FolderView(Option):
    """The view of a folder within the navigation widget."""

    def __init__(self, folder: Folder, expanded: bool) -> None:
        """Initialise the folder view object.

        Args:
            folder: The folder to view.
            expanded: Should we show as being expanded?
        """
        self._folder = folder
        """The folder we're viewing."""
        super().__init__(
            f"[bold $text-primary]{'▼' if expanded else '▶'} {folder.name}[/]",
            id=folder.id,
        )

    def folder(self) -> Folder:
        """The folder we're viewing."""
        return self._folder


##############################################################################
class SubscriptionView(Option):
    """The view of a subscription within the navigation widget."""

    def __init__(self, subscription: Subscription) -> None:
        """Initialise the subscription view object.

        Args:
            subscription: The subscription we're viewing.
        """
        self._subscription = subscription
        """The subscription we're viewing."""
        super().__init__(f"  [$text-secondary]{subscription.title}[/]")

    def subscription(self) -> Subscription:
        """The subscription we're viewing."""
        return self._subscription


##############################################################################
class Navigation(EnhancedOptionList):
    """The main navigation widget."""

    DEFAULT_CSS = """
    Navigation {
        text-wrap: nowrap;
        text-overflow: ellipsis;
    }
    """

    folders: var[Folders] = var(Folders)
    """The folders that subscriptions are assigned to."""
    subscriptions: var[Subscriptions] = var(Subscriptions)
    """The list of subscriptions."""
    unread: var[Unread | None] = var(None)
    """The unread counts."""

    _expanded: var[dict[str, bool]] = var(dict)
    """Tracks the expanded state of each folder."""

    def _add_subscriptions(self, parent_folder: str) -> None:
        """Add the subscriptions for a given parent folder.

        Args:
            parent_folder: The parent folder to add the subscriptions for.
        """
        for subscription in self.subscriptions:
            if any(
                category.id == parent_folder for category in subscription.categories
            ):
                self.add_option(SubscriptionView(subscription))

    def _add_folder(self, folder: Folder) -> None:
        """Add the given folder to the navigation.

        Args:
            folder: The folder to add.
        """
        self.add_option(
            FolderView(folder, expanded := self._expanded.get(folder.id, False))
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
        self._expanded = {folder.id: False for folder in self.folders}
        self._refresh_navigation()

    def _watch_subscriptions(self) -> None:
        """React to the subscriptions being updated."""
        self._refresh_navigation()

    def _watch_unread(self) -> None:
        """React to the unread data being updated."""
        self._refresh_navigation()

    def _select_folder(self, folder: FolderView) -> None:
        """Perform the selection action for the given folder.

        Args:
            folder: The folder to perform the action for.
        """
        if (folder_id := folder.id) is not None:
            self._expanded[folder_id] = not self._expanded[folder_id]
            self._refresh_navigation()

    @on(EnhancedOptionList.OptionSelected)
    def _handle_selection(self, message: EnhancedOptionList.OptionSelected) -> None:
        """Handle an item in the navigation widget being selected.

        Args:
            message: The message to handle.
        """
        if isinstance(message.option, FolderView):
            self._select_folder(message.option)


### navigation.py ends here
