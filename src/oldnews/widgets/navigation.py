"""Provides the main navigation widget."""

##############################################################################
# OldAs imports.
from operator import attrgetter

from oldas import Folder, Folders

##############################################################################
# Textual imports.
from textual import on
from textual.reactive import var
from textual.widgets.option_list import Option

##############################################################################
# Textual enhanced imports.
from textual_enhanced.widgets import EnhancedOptionList


##############################################################################
class Navigation(EnhancedOptionList):
    """The main navigation widget."""

    folders: var[Folders] = var(Folders)
    """The folders."""
    _expanded: var[dict[str, bool]] = var(dict)
    """Tracks the expanded state of each folder."""

    def _add_folder(self, folder: Folder) -> None:
        expanded = self._expanded[folder.id]
        self.add_option(
            Option(f"{'▼' if expanded else '▶'} {folder.name}", id=folder.id)
        )

    def _refresh_navigation(self) -> None:
        """Refresh the content of the navigation widget."""
        with self.preserved_highlight:
            self.clear_options()
            for folder in sorted(self.folders, key=attrgetter("sort_id")):
                self._add_folder(folder)

    def _watch_folders(self) -> None:
        """React to the list of folders being changed."""
        self._expanded = {folder.id: False for folder in self.folders}
        self._refresh_navigation()

    @on(EnhancedOptionList.OptionSelected)
    def _handle_selection(self, message: EnhancedOptionList.OptionSelected) -> None:
        """Handle an item in the navigation widget being selected.

        Args:
            message: The message to handle.
        """
        if (folder := message.option.id) is not None:
            self._expanded[folder] = not self._expanded[folder]
            self._refresh_navigation()


### navigation.py ends here
