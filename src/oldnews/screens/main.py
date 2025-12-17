"""Provides the main screen."""

##############################################################################
# OldAs imports.
from oldas import Folders, Session

##############################################################################
# Textual imports.
from textual import work
from textual.app import ComposeResult
from textual.reactive import var
from textual.widgets import Footer, Header

##############################################################################
# Textual enhanced imports.
from textual_enhanced.screen import EnhancedScreen

##############################################################################
# Local imports.
from .. import __version__
from ..widgets import Navigation


##############################################################################
class Main(EnhancedScreen[None]):
    """The main screen for the application."""

    TITLE = f"OldNews v{__version__}"

    CSS = """
    Main {
        layout: horizontal;
        hatch: right $surface;

        .panel {
            height: 1fr;
            padding-right: 0;
            border: none;
            border-left: round $border 50%;
            background: $surface;
            scrollbar-gutter: stable;
            scrollbar-background: $surface;
            scrollbar-background-hover: $surface;
            scrollbar-background-active: $surface;
            &:focus, &:focus-within {
                border: none;
                border-left: round $border;
                background: $panel 80%;
                scrollbar-background: $panel;
                scrollbar-background-hover: $panel;
                scrollbar-background-active: $panel;
            }
            &> .option-list--option {
                padding: 0 1;
            }
        }

        Navigation {
            min-width: 20%;
            max-width: 40%;
            width: auto;
        }
    }
    """

    COMMAND_MESSAGES = []

    folders: var[Folders] = var(Folders)
    """The folders."""

    def __init__(self, session: Session) -> None:
        """Initialise the main screen."""
        super().__init__()
        self._session = session
        """The TOR session."""

    def compose(self) -> ComposeResult:
        """Compose the content of the main screen."""
        yield Header()
        yield Navigation(classes="panel").data_bind(Main.folders)
        yield Footer()

    def on_mount(self) -> None:
        """Configure the application once the DOM is mounted."""
        self.load_from_tor()

    @work(exclusive=True)
    async def load_from_tor(self) -> None:
        """Load the main data from TheOldReader."""
        self.folders = await Folders.load(self._session)


### main.py ends here
