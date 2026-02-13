"""Provides the dialog for editing a subscription's content filter."""

##############################################################################
# OldAS imports.
from oldas import Subscription

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.getters import query_one
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

##############################################################################
# Textual Enhanced imports.
from textual_enhanced.tools import add_key


##############################################################################
class SubscriptionContentFilter(ModalScreen[str | None]):
    """Dialog for editing the content filter for a subscription."""

    CSS = """
    SubscriptionContentFilter {
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
                &.preamble {
                    width: 1fr;
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

    selector_input = query_one(Input)
    """The selector input."""

    def __init__(self, subscription: Subscription, content_filter: str) -> None:
        """Initialise the dialog.

        Args:
            subscription: The subscription to edit the filter for.
            content_filter: The content filter to use.
        """
        self._subscription = subscription
        """The subscription that we're editing the filter for."""
        self._content_filter = content_filter
        """The content filter."""
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        with Vertical() as dialog:
            dialog.border_title = "Subscription content filter"
            yield Label(
                "When using the 'grab' facility to view the content of an article "
                "you'll sometimes find there's a lot of extra text on a page that "
                "you're not interested in. If you know the layout of the HTML for the "
                "blog, etc, set a CSS selector to get to the real text of an article.",
                classes="preamble value",
            )
            yield Label("Subscription:")
            yield Label(self._subscription.title, classes="value")
            yield Label("CSS selector for the interesting content:")
            yield Input(
                self._content_filter,
                placeholder="Provide a CSS selector or leave blank to remove",
            )
            with Horizontal():
                yield Button(add_key("Set", "Enter", self), id="set")
                yield Button(
                    add_key("Cancel", "Esc", self), id="cancel", variant="error"
                )

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        """React to the user cancelling the dialog."""
        self.dismiss(None)

    @on(Button.Pressed, "#set")
    @on(Input.Submitted)
    def action_move(self) -> None:
        """React to the user deciding to set the selector."""
        self.dismiss(self.selector_input.value.strip())


### subscription_content_filter.py ends here
