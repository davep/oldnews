"""Provides a dialog for getting details for a new subscription."""

##############################################################################
# Python imports.
from typing import NamedTuple

##############################################################################
# BagOfStuff imports.
from bagofstuff.url_tools import looks_webish

##############################################################################
# OldAS imports.
from oldas import Folders

##############################################################################
# Pyperclip imports.
from pyperclip import PyperclipException
from pyperclip import paste as from_clipboard

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.getters import query_one
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

##############################################################################
# Textual-autocomplete imports.
from textual_autocomplete import AutoComplete


##############################################################################
class NewSubscriptionData(NamedTuple):
    """Class that holds details of a new subscription."""

    feed: str
    """The feed for the subscription."""
    folder: str
    """The folder to add the subscription to."""


##############################################################################
class NewSubscription(ModalScreen[NewSubscriptionData | None]):
    """Dialog for getting details of a new subscription."""

    CSS = """
    NewSubscription {
        align: center middle;

        &> Vertical {
            padding: 1 2;
            width: 40%;
            min-width: 70;
            height: auto;
            background: $panel;
            border: panel $border;

            Label {
                margin-left: 1;
            }

            &> Horizontal {
                margin-top: 1;
                height: auto;
                align-horizontal: right;

                Button {
                    margin-right: 1;
                }
            }
        }
    }
    """

    BINDINGS = [("escape", "cancel")]

    feed_input = query_one("#feed", Input)
    """The feed input widget."""
    folder_input = query_one("#folder", Input)
    """The folder input widget."""
    add_button = query_one("#add", Button)
    """The add button."""

    def __init__(self, folders: Folders) -> None:
        """Initialise the dialog object.

        Args:
            folders: The folders a subscription might be placed in.
        """
        self._folders = folders
        """The folders to complete with."""
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        with Vertical() as dialog:
            dialog.border_title = "New Subscription"
            yield Label("Feed:")
            yield Input(id="feed", placeholder="https://example.com/feed.rss")
            yield Label("Folder:")
            yield (
                folder_input := Input(
                    id="folder", placeholder="Leave blank for no folder"
                )
            )
            with Horizontal():
                yield Button("Add", id="add", variant="primary", disabled=True)
                yield Button("Cancel [dim]\\[Esc][/]", id="cancel", variant="error")
            yield AutoComplete(
                folder_input, candidates=[folder.name for folder in self._folders]
            )

    def on_mount(self) -> None:
        """Configure the dialog once the DOM is mounted."""
        self._suggest_feed()

    @on(Input.Changed, "#feed")
    def _refresh_state(self) -> None:
        """Refresh the state of the dialog."""
        self.add_button.disabled = not bool(self.feed_input.value.strip())

    @on(Button.Pressed, "#add")
    def action_add(self) -> None:
        """React to the user pressing the add button."""
        if feed := self.feed_input.value.strip():
            self.dismiss(
                NewSubscriptionData(
                    feed=feed,
                    folder=self.folder_input.value.strip(),
                )
            )

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        """React to the user cancelling the dialog."""
        self.dismiss(None)

    def _paste(self, url: str) -> None:
        """Paste the given URL into the feed field.

        Args:
            url: The URL to paste.

        Notes:
            The given URL will only be pasted into the feed input field if
            that field is empty.
        """
        if not self.feed_input.value:
            self.feed_input.value = url

    @work(thread=True)
    def _suggest_feed(self) -> None:
        """Get a feed suggestion by peeking in the user's clipboard."""
        # Look for something in the external clipboard.
        try:
            external = from_clipboard()
        except PyperclipException:
            external = ""
        # Looking at the Textual-internal clipboard, then the external
        # clipboard...
        for candidate in (self.app.clipboard, external):
            # ...only looking at the first line of what we find...
            try:
                candidate = candidate.strip().splitlines()[0]
            except IndexError:
                candidate = ""
            # If it looks like it might be a URL...
            if looks_webish(candidate):
                # ...paste it into the feed field.
                self.app.call_from_thread(self._paste, candidate)
                break


### new_subscription.py ends here
