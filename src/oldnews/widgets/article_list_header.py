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
    }
    """

    current_category: var[Folder | Subscription | None] = var(None)
    """The navigation category that is currently selected."""

    def _watch_current_category(self) -> None:
        """React to the current category being updated."""
        if isinstance(self.current_category, Folder):
            self.update(self.current_category.name)
        elif isinstance(self.current_category, Subscription):
            self.update(self.current_category.title)
        else:
            self.update("")


### article_list_header.py ends here
