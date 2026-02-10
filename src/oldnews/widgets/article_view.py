"""Provides the panel for viewing things related to articles."""

##############################################################################
# OldAS imports.
from oldas import Articles

##############################################################################
# Textual imports.
from textual.containers import Vertical
from textual.reactive import var


##############################################################################
class ArticleView(Vertical):
    """A container widget for holding the widgets related to articles."""

    DEFAULT_CSS = """
    ArticleView {
        display: none;
        &.--has-articles {
            display: block;
        }
    }
    """

    articles: var[Articles] = var(Articles)
    """The currently-viewed list of articles."""

    def _watch_articles(self) -> None:
        """React to the articles list changing."""
        self.set_class(bool(self.articles), "--has-articles")


### article_view.py ends here
