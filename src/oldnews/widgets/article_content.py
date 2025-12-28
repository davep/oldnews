"""Provides a widget that shows an article's content."""

##############################################################################
# Python imports.
from typing import Self

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
from textual.message import Message
from textual.reactive import var
from textual.widgets import Label, Markdown

##############################################################################
# Textual enhanced imports.
from textual_enhanced.binding import HelpfulBinding


##############################################################################
class ArticleContent(Vertical):
    """Shows the content of an article."""

    DEFAULT_CSS = """
    ArticleContent {
        display: none;

        &.--has-article {
            display: block;
        }

        #header {
            height: auto;
            padding: 0 1 0 1;

            #title {
                color: $text-accent;
            }
            #published {
                color: $text-muted;
            }
        }

        Markdown {
            padding: 0 1 0 1;
        }
    }
    """

    HELP = """
    ## The article

    This panel is the view of the summary of the current article; here you
    can read the text of the article as is provided in the feed.
    """

    BINDINGS = [
        HelpfulBinding(
            "escape, q",
            "close_article",
            "Close",
            show=False,
            tooltip="Close the view of the current article",
        )
    ]

    article: var[Article | None] = var(None)
    """The article being viewed."""

    class Close(Message):
        """Message sent when the user wants to close the current article."""

    def compose(self) -> ComposeResult:
        """Compose the content of the widget."""
        with Vertical(id="header"):
            yield Label(id="title")
            yield Label(id="published")
        with VerticalScroll():
            yield Markdown()

    def _watch_article(self) -> None:
        """React to the article being updated."""
        self.set_class(self.article is not None, "--has-article")
        if self.article is not None:
            self.query_one("#title", Label).update(self.article.title)
            self.query_one("#published", Label).update(str(self.article.published))
            self.query_one(Markdown).update(convert(self.article.summary.content))

    def focus(self, scroll_visible: bool = True) -> Self:
        self.query_one(VerticalScroll).focus(scroll_visible)
        return self

    def action_close_article(self) -> None:
        """Close the current article."""
        self.post_message(self.Close())


### article_content.py ends here
