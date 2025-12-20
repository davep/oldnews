"""Provides a widget that shows an article's content."""

##############################################################################
# OldAS imports.
from oldas import Article

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import var
from textual.widgets import Static


##############################################################################
class ArticleContent(Vertical):
    """Shows the content of an article."""

    DEFAULT_CSS = """
    ArticleContent {
        display: none;

        &.has-article {
            display: block;
        }
    }
    """

    article: var[Article | None] = var(None)
    """The article being viewed."""

    def compose(self) -> ComposeResult:
        """Compose the content of the widget."""
        yield Static()

    def _watch_article(self) -> None:
        """React to the article being updated."""
        self.set_class(self.article is not None, "has-article")
        if self.article is not None:
            self.query_one(Static).update(self.article.summary.content)


### article_content.py ends here
