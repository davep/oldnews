"""Provides a widget that acts as a header for the article list."""

##############################################################################
# OldAS imports.
from oldas import Folder, Subscription

##############################################################################
# Textual imports.
from textual.reactive import var
from textual.widgets import Static


##############################################################################
class ArticleListHeader(Static):
    """A header to go above the article list."""

    DEFAULT_CSS = """
    ArticleListHeader {
        background: $secondary;
        padding: 1 2;
        color: $text-accent;
        &.--compact {
            padding: 0 2;
        }
    }
    """

    current_category: var[Folder | Subscription | None] = var(None)
    """The navigation category that is currently selected."""
    compact_ui: var[bool] = var(False, toggle_class="--compact")
    """Should we try and make the UI as compact as possible?"""

    def _watch_current_category(self) -> None:
        """React to the current category being updated."""
        if isinstance(self.current_category, Folder):
            self.update(self.current_category.name)
        elif isinstance(self.current_category, Subscription):
            self.update(self.current_category.title)
        else:
            self.update("")


### article_list_header.py ends here
