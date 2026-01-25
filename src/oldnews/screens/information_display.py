"""Provides a dialog for showing some information in a table."""

##############################################################################
# Python imports.
from typing import Iterable

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.getters import query_one
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable


##############################################################################
class InformationDisplay(ModalScreen[None]):
    """A modal dialog for showing some data in a table."""

    CSS = """
    InformationDisplay {
        align: center middle;

        &> Vertical {
            width: auto;
            height: auto;
            background: $panel;
            border: panel $border;
            &> Center {
                width: 100%;
            }
        }

        DataTable {
            width: auto;
            margin: 1 2;
        }

    }
    """

    table = query_one(DataTable)
    """The table for showing the data."""

    BINDINGS = [("escape", "close"), ("ctrl+c", "copy")]

    def __init__(self, title: str, information: Iterable[tuple[str, str]]) -> None:
        """Initialise the dialog.

        Args:
            title: The title for the dialog.
            information: The information to show.
        """
        self._title = title
        """The title for the dialog."""
        self._information = list(information)
        """The information to show in the table."""
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the content of the dialog."""
        with Vertical() as dialog:
            dialog.border_title = f"{self._title} Information"
            yield DataTable(show_header=False, cursor_type="row")
            with Center():
                yield Button("Close")

    def on_mount(self) -> None:
        """Populate the dialog once the DOM is ready."""
        self.table.add_columns("", "")
        for data in self._information:
            self.table.add_row(*data)

    @on(Button.Pressed)
    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss(None)

    def action_copy(self) -> None:
        """Copy the current data to the clipboard."""
        self.app.copy_to_clipboard(self._information[self.table.cursor_row][1])
        self.notify("Copied")


### information_display.py ends here
