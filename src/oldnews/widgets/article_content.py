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
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import var
from textual.widgets import Label, Markdown, Rule


##############################################################################
class ArticleContent(Vertical):
    """Shows the content of an article."""

    DEFAULT_CSS = """
    ArticleContent {
        display: none;

        &.--has-article {
            display: block;
        }

        Rule.-horizontal {
            margin: 0;
        }

        #header {
            height: auto;
            padding: 0 1 0 1;

            Horizontal {
                height: auto;
            }

            #title {
                color: $text-accent;
                width: 1fr;
            }
            #published, #link {
                color: $text-muted;
            }
        }

        &:focus-within {
            #header, Rule {
                background: $boost;
            }
            Rule {
                color: $border;
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

    article: var[Article | None] = var(None)
    """The article being viewed."""

    def compose(self) -> ComposeResult:
        """Compose the content of the widget."""
        yield Rule()
        with Vertical(id="header"):
            with Horizontal():
                yield Label(id="title", markup=False)
                yield Label(id="published")
            yield Label(id="link", markup=False)
        yield Rule()
        with VerticalScroll():
            yield Markdown()

    async def _watch_article(self) -> None:
        """React to the article being updated."""
        if self.article is not None:
            self.query_one("#title", Label).update(self.article.title)
            self.query_one("#published", Label).update(str(self.article.published))
            link = self.query_one("#link", Label)
            if self.article.html_url is None:
                link.visible = False
            else:
                link.visible = True
                link.update(self.article.html_url)
            await self.query_one(Markdown).update(convert(self.article.summary.content))
            self.query_one(VerticalScroll).scroll_home(animate=False)
        self.set_class(self.article is not None, "--has-article")

    def focus(self, scroll_visible: bool = True) -> Self:
        self.query_one(VerticalScroll).focus(scroll_visible)
        return self


### article_content.py ends here
