"""Provides a dialog for waiting for TheOldReader to add a subscription."""

##############################################################################
# OldAS imports.
from oldas import Session, Subscriptions
from oldas.subscriptions import SubscribeResult

##############################################################################
# Textual imports.
from textual import work
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, LoadingIndicator

##############################################################################
# Local data.
from .new_subscription import NewSubscriptionData


##############################################################################
class ProcessSubscription(ModalScreen[SubscribeResult]):
    """Dialog for waiting for TheOldReader to process a subscription."""

    CSS = """
    ProcessSubscription {
        align: center middle;

        &> Vertical {
            padding: 1 2;
            width: auto;
            height: auto;
            min-width: 60%;
            max-width: 90%;
            background: $panel;
            border: panel $border;
            LoadingIndicator {
                margin-top: 1;
            }
            Center {
                width: 100%;
            }
        }
    }
    """

    def __init__(self, session: Session, new_subscription: NewSubscriptionData) -> None:
        """Initialise the subscription processing dialog object.

        Args:
            session: The ToR API session object.
            new_subscription: The new subscription.
        """
        self._session = session
        """The API session object."""
        self._feed = new_subscription.feed
        """The feed to subscribe to."""
        self._folder = new_subscription.folder
        """The folder to place the subscription in."""
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        with Vertical() as dialog:
            dialog.border_title = "Waiting for TheOldReader to add the feed..."
            yield Label(
                f"Subscribing to {self._feed}"
                + (f" and adding it to {self._folder}" if self._folder else "")
                + ".\n\n"
                "TheOldReader can take a short while to scan and add a feed. Please wait...",
                shrink=True,
                markup=False,
            )
            with Center():
                yield LoadingIndicator()

    @work
    async def _request_subscription(self) -> None:
        """Process the request."""
        self.dismiss(await Subscriptions.add(self._session, self._feed))

    def on_mount(self) -> None:
        """Start the work once the DOM is ready."""
        self._request_subscription()


### process_subscription.py ends here
