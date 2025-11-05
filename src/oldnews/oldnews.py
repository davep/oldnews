"""The main application class."""

##############################################################################
# Python imports.
from argparse import Namespace
from functools import partial

##############################################################################
# OldAs imports.
from oldas import Session

##############################################################################
# Textual imports.
from textual.app import InvalidThemeError

##############################################################################
# Textual enhanced imports.
from textual_enhanced.app import EnhancedApp

##############################################################################
# Local imports.
from . import __version__
from .data import (
    get_auth_token,
    load_configuration,
    set_auth_token,
    update_configuration,
)
from .screens import Login, Main


##############################################################################
class OldNews(EnhancedApp[None]):
    """The main application class."""

    HELP_TITLE = f"OldNews v{__version__}"
    HELP_ABOUT = """
    `OldNews` is a terminal-based client for [TheOldReader](https://www.theoldreader.com/);
    it was created by and is maintained by [Dave Pearson](https://www.davep.org/); it is
    Free Software and can be [found on GitHub](https://github.com/davep/oldnews).
    """
    HELP_LICENSE = """
    OldNews - A client for TheOldReader for the terminal.  \n    Copyright (C) 2025 Dave Pearson

    This program is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
    more details.

    You should have received a copy of the GNU General Public License along with
    this program. If not, see <https://www.gnu.org/licenses/>.
    """

    COMMANDS = set()

    def __init__(self, arguments: Namespace) -> None:
        """Initialise the application.

        Args:
            arguments: The command line arguments passed to the application.
        """
        self._arguments = arguments
        """The command line arguments passed to the application."""
        super().__init__()
        configuration = load_configuration()
        if configuration.theme is not None:
            try:
                self.theme = arguments.theme or configuration.theme
            except InvalidThemeError:
                pass
        self.update_keymap(configuration.bindings)

    def watch_theme(self) -> None:
        """Save the application's theme when it's changed."""
        with update_configuration() as config:
            config.theme = self.theme

    def login_bounce(self, session: Session | None) -> None:
        """handle the result of asking the user to log in.

        Args:
            session: The TOR session if we logged in, or `None`.
        """
        if session and session.auth_code:
            set_auth_token(session.auth_code)
            self.push_screen(Main(session))
        else:
            self.exit()

    def on_mount(self) -> None:
        """Display the main screen.

        Note:
            If the TOR access token isn't known, the login dialog will be
            shown; the main screen will then only be shown once a token as
            been acquired.
        """
        session = partial(Session, "OldNews")
        if token := get_auth_token():
            self.push_screen(Main(session(token)))
        else:
            self.push_screen(Login(session()), callback=self.login_bounce)


### oldnews.py ends here
