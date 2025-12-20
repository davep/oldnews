"""Provides a widget that shows an article's content."""

##############################################################################
# html-to-markdown imports.
from html_to_markdown import convert

##############################################################################
# OldAS imports.
from oldas import Article

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.reactive import var
from textual.widgets import Markdown


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
        with VerticalScroll():
            yield Markdown()

    def _watch_article(self) -> None:
        """React to the article being updated."""
        self.set_class(self.article is not None, "has-article")
        if self.article is not None:
            self.query_one(Markdown).update(convert(self.article.summary.content))


### article_content.py ends here
