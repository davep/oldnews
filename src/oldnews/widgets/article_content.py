"""Provides a widget that shows an article's content."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from typing import Self

##############################################################################
# html-to-markdown imports.
from html_to_markdown import ConversionOptions, convert

##############################################################################
# httpx imports.
from httpx import AsyncClient, HTTPStatusError, RequestError

##############################################################################
# OldAS imports.
from oldas import Article

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.getters import query_one
from textual.message import Message
from textual.reactive import var
from textual.widgets import Label, Markdown
from textual_enhanced.binding import HelpfulBinding

##############################################################################
# Local imports.
from .. import __user_agent__


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
            padding: 1 2;
            background: $secondary;

            Horizontal {
                height: auto;
            }

            #title {
                color: $text-accent;
                width: 1fr;
                padding-right: 2;
            }
            #published, #link {
                color: $text-muted;
            }
        }

        Markdown {
            padding: 0 1 0 1;
        }

        &.--compact #header {
            padding: 0 2;
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
            "g",
            "grab_full_content",
            "Grab Full",
            tooltip="Grab the page of the article and render it as text",
        )
    ]

    article: var[Article | None] = var(None)
    """The article being viewed."""
    compact_ui: var[bool] = var(False, toggle_class="--compact")
    """Should we try and make the UI as compact as possible?"""

    title = query_one("#title", Label)
    """The title label."""
    published = query_one("#published", Label)
    """The published date label."""
    link = query_one("#link", Label)
    """The link label."""
    markdown = query_one(Markdown)
    """The markdown display for the article."""
    content = query_one(VerticalScroll)
    """The article content."""

    @dataclass
    class Displayed(Message):
        """Message sent once an article is displayed."""

        article: Article
        """The article that has been displayed."""

    def compose(self) -> ComposeResult:
        """Compose the content of the widget."""
        with Vertical(id="header"):
            with Horizontal():
                yield Label(id="title", markup=False)
                yield Label(id="published")
            yield Label(id="link", markup=False)
        with VerticalScroll(classes="panel"):
            yield Markdown()

    async def _watch_article(self) -> None:
        """React to the article being updated."""
        if self.article is not None:
            self.title.update(self.article.title)
            self.published.update(
                self.article.published.astimezone().strftime("%Y-%m-%d %H:%M:%S")
            )
            if self.article.html_url is None:
                self.link.visible = False
            else:
                self.link.visible = True
                self.link.update(self.article.html_url)
            await self.markdown.update(convert(self.article.summary.content))
            self.content.scroll_home(animate=False)
            self.post_message(self.Displayed(self.article))
        self.set_class(self.article is not None, "--has-article")

    def focus(self, scroll_visible: bool = True) -> Self:
        self.content.focus(scroll_visible)
        return self

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action is possible to perform right now.

        Args:
            action: The action to perform.
            parameters: The parameters of the action.

        Returns:
            `True` if it can perform, `False` or `None` if not.
        """
        if self.is_mounted and action == "action_grab_full_content":
            return bool(self.article and self.article.html_url)
        return True

    async def action_grab_full_content(self) -> None:
        """Attempt to grab and show the full content of the article."""
        if not self.article or not self.article.html_url:
            return
        self.content.loading = True
        try:
            async with AsyncClient() as client:
                response = await client.get(
                    self.article.html_url,
                    follow_redirects=True,
                    headers={"user-agent": __user_agent__},
                )
        except RequestError as error:
            self.notify(str(error), title="Request error", severity="error", timeout=8)
            return
        finally:
            self.content.loading = False
        try:
            response.raise_for_status()
        except HTTPStatusError as error:
            self.notify(str(error), title="Response error", severity="error", timeout=8)
            return
        await self.markdown.update(
            convert(
                response.text,
                ConversionOptions(extract_metadata=False, skip_images=True),
            )
        )


### article_content.py ends here
