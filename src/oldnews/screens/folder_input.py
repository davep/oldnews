"""Provides a dialog for entering a folder name."""

##############################################################################
# OldAS imports.
from oldas import Folders

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.containers import Vertical

##############################################################################
# Textual-autocomplete imports.
from textual_autocomplete import AutoComplete

##############################################################################
# Textual-enhanced imports.
from textual_enhanced.dialogs import ModalInput


##############################################################################
class FolderInput(ModalInput):
    """A dialog for entering the name of a folder."""

    CSS = (
        ModalInput.CSS.replace("ModalInput", "FolderInput")
        + """
    FolderInput {
        &> Vertical {
            align: center middle;
            height: auto;
            /* Some nonsense to keep AutoComplete stable. */
            visibility: hidden;
            * {
                visibility: visible;
            }
        }
    }
    """
    )

    def __init__(self, folders: Folders) -> None:
        """Initialise the folder input dialog.

        Args:
            folders: The folders to prompt with.
        """
        self._folders = folders
        """The folders that already exist."""
        super().__init__(
            placeholder="Enter the name of the folder to move to; leaving empty means top-level (no folder)"
        )

    def compose(self) -> ComposeResult:
        with Vertical():
            yield from super().compose()
            yield AutoComplete(
                "Input", candidates=[folder.name for folder in self._folders]
            )


### folder_input.py ends here
