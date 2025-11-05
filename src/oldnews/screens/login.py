"""The login dialog."""

##############################################################################
# OldAS imports.
from oldas import OldASError, OldASInvalidLogin, Session

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input


##############################################################################
class Login(ModalScreen[Session | None]):
    """A login dialog for TheOldReader."""

    CSS = """
    Login {
        align: center middle;

        &> Vertical {
            padding: 1 2;
            width: 40%;
            min-width: 70;
            height: auto;
            background: $panel;
            border: panel $border;

            #password {
                margin-top: 1;
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

    def __init__(self, session: Session) -> None:
        """Initialise the login dialog.

        Args:
            session: The TOR session to work with.
        """
        super().__init__()
        self._session = session
        """The TOR session."""

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        with Vertical() as dialog:
            dialog.border_title = "Login"
            yield Input(id="user-name", placeholder="Username/Email")
            yield Input(id="password", password=True, placeholder="Password")
            with Horizontal():
                yield Button("Login", id="login", variant="primary")
                yield Button("Cancel [dim]\\[Esc][/]", id="cancel", variant="error")

    @on(Button.Pressed, "#login")
    async def login(self) -> None:
        """Log into TheOldReader."""
        if (user := self.query_one("#user-name", Input).value) and (
            password := self.query_one("#password", Input).value
        ):
            try:
                # TODO: Add some sort of busy effect as the login happens.
                await self._session.login(user, password)
            except OldASInvalidLogin:
                self.notify(
                    "Invalid user name or password",
                    title="Login failed",
                    severity="error",
                )
                return
            except OldASError as error:
                self.notify(str(error), title="Login failed", severity="error")
                return
            if self._session.logged_in:
                self.dismiss(self._session)
            else:
                self.notify("Login failed", severity="error")
        else:
            self.notify("Please input the user name and password", severity="warning")

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        """React to the user cancelling the login."""
        self.dismiss(None)


### login.py ends here
