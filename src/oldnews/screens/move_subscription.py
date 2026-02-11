"""Provides a dialog that gets the folder to move a subscription to."""

##############################################################################
# OldAS imports.
from oldas import Folder, Folders, Subscription

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.getters import query_one
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

##############################################################################
# Textual-autocomplete imports.
from textual_autocomplete import AutoComplete

##############################################################################
# Textual Enhanced imports.
from textual_enhanced.tools import add_key


##############################################################################
class MoveSubscriptionTo(ModalScreen[str | None]):
    """Dialog for getting the folder name to move a subscription to."""

    CSS = """
    MoveSubscriptionTo {
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
                &.value {
                    color: $accent;
                    padding-bottom: 1;
                }
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

    folder_input = query_one(Input)
    """The folder input."""

    def __init__(self, subscription: Subscription, folders: Folders) -> None:
        """Initialise the dialog.

        Args:
            subscription: The subscription being moved.
        """
        self._subscription = subscription
        """The subscription that is being moved."""
        self._moving_from = (
            Folder(self._subscription.folder_id, "").name
            if self._subscription.folder_id
            else "[i dim]Top Level[/]"
        )
        """The name of the location we're moving from."""
        self._folders = folders
        """The folders we could move to."""
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        with Vertical() as dialog:
            dialog.border_title = "Move Subscription"
            yield Label("Subscription:")
            yield Label(self._subscription.title, classes="value")
            yield Label("Move from:")
            yield Label(self._moving_from, classes="value")
            yield Label("Move to:")
            yield (
                folder_input := Input(
                    placeholder="Leave blank to move to the top level"
                )
            )
            with Horizontal():
                yield Button(add_key("Move", "Enter", self), id="move")
                yield Button(
                    add_key("Cancel", "Esc", self), id="cancel", variant="error"
                )
            yield AutoComplete(
                folder_input,
                candidates=[
                    folder.name
                    for folder in self._folders
                    if folder.name != self._moving_from
                ],
            )

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        """React to the user cancelling the dialog."""
        self.dismiss(None)

    @on(Button.Pressed, "#move")
    @on(Input.Submitted)
    def action_move(self) -> None:
        """React to the user deciding to do the move."""
        self.dismiss(self.folder_input.value.strip())


### move_subscription.py ends here
