"""Widget to show a list of articles."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from operator import attrgetter
from typing import cast

##############################################################################
# OldAs imports.
from oldas import Article, Articles, Folder, Subscription

##############################################################################
# Rich imports.
from rich.console import Group
from rich.markup import escape
from rich.table import Table

##############################################################################
# Textual imports.
from textual import on
from textual.message import Message
from textual.reactive import var
from textual.widgets.option_list import Option

##############################################################################
# Textual enhanced imports.
from textual_enhanced.widgets import EnhancedOptionList

##############################################################################
# Local imports.
from ._next_matching_option import Direction, next_matching_option


##############################################################################
class ArticleView(Option):
    """The view of an article in the article list."""

    def __init__(
        self, article: Article, showing_subscription: bool, compact: bool
    ) -> None:
        """Initialise the article object.

        Args:
            article: The article to view.
            showing_subscription: Is the article list showing a subscription?
            compact: Should we show a compact version?
        """
        self._article = article
        """The article to view."""
        status = "[green]●[/]" if article.is_unread else ""
        title = escape(article.title)
        published = f"[dim]{escape(article.published.astimezone().strftime('%Y-%m-%d %H:%M:%S'))}[/]"
        header = Table.grid(expand=True)
        header.add_column(width=2)
        header.add_column(ratio=1, no_wrap=compact)
        content: Table | Group
        if compact:
            header.add_column(width=20, justify="right")
            header.add_row(status, title, published)
            content = header
        else:
            header.add_row(status, title)
            provenance = escape(
                (
                    article.author
                    if showing_subscription
                    else f"{article.origin.title}, {article.author}"
                )
                if article.author and article.author != article.origin.title
                else article.origin.title
            )
            details = Table.grid(expand=True)
            details.add_column(width=2)
            details.add_column(ratio=1)
            details.add_column(width=20, justify="right")
            details.add_row("", f"[dim italic]{provenance}[/]", published)
            content = Group(header, details)
        super().__init__(content, id=article.id)

    @property
    def article(self) -> Article:
        """The article being viewed."""
        return self._article


##############################################################################
class ArticleList(EnhancedOptionList):
    """Widget for showing a list of articles."""

    HELP = """
    ## The articles

    This panel shows the available articles for the folder or subscription
    that is highlighted in the navigation panel.
    """

    selected_category: var[Folder | Subscription | None] = var(None)
    """The category of articles being shown."""
    articles: var[Articles] = var(Articles)
    """The list of articles to show."""
    compact_ui: var[bool] = var(False)
    """Should we try and make the UI as compact as possible?"""

    @dataclass
    class ViewArticle(Message):
        """Message that requests that we view a specific article."""

        article: Article
        """The article to view."""

    @property
    def highlighted_article(self) -> Article | None:
        """The currently-highlighted article, or `None` if there isn't one."""
        if self.highlighted is not None:
            return cast(ArticleView, self.get_option_at_index(self.highlighted)).article
        return None

    def _watch_articles(self) -> None:
        """React to the article list being changed."""
        # Normally preserved_highlight is good enough; but here I want to
        # preserve the highlight but only if the article we end up on was
        # the one we started on; so this time we do a little bit of extra
        # work to undo preserved_highlight being helpful.
        current_id = (
            self.get_option_at_index(self.highlighted).id
            if self.highlighted is not None
            else None
        )
        showing_subscription = isinstance(self.selected_category, Subscription)
        with self.preserved_highlight:
            self.set_options(
                [
                    ArticleView(article, showing_subscription, self.compact_ui)
                    for article in self.articles
                ]
            )
        new_id = (
            self.get_option_at_index(self.highlighted).id
            if self.highlighted is not None
            else None
        )
        if current_id is not None and current_id != new_id:
            self.highlighted = 0
        self.can_focus = bool(self.option_count)

    def _watch_compact_ui(self) -> None:
        """React to the compact setting being toggled."""
        self.mutate_reactive(ArticleList.articles)

    @on(EnhancedOptionList.OptionSelected)
    def _select_article(self, message: EnhancedOptionList.OptionSelected) -> None:
        """Select an article to view.

        Args:
            message: The message to handle.
        """
        assert isinstance(message.option, ArticleView)
        self.post_message(self.ViewArticle(message.option.article))

    def _highlight_unread(self, direction: Direction) -> bool:
        """Highlight the next unread article, if there is one.

        Args:
            direction: The direction to search.

        Returns:
            `True` if an unread article was found and highlighted, `False`
            if not.
        """
        if (
            next_hit := next_matching_option(
                cast(list[ArticleView], self.options),
                self.highlighted,
                direction,
                attrgetter("article.is_unread"),
            )
        ) and next_hit.id is not None:
            self.highlighted = self.get_option_index(next_hit.id)
            return True
        self.notify("No more unread articles")
        return False

    def highlight_next_article(self) -> None:
        """Highlight the next article in the list."""
        self.call_later(self.run_action, "cursor_down")

    def highlight_previous_article(self) -> None:
        """Highlight the previous article in the list."""
        self.call_later(self.run_action, "cursor_up")

    def highlight_next_unread_article(self) -> None:
        """Highlight the next unread article in the list."""
        self._highlight_unread("forward")

    def highlight_previous_unread_article(self) -> None:
        """Highlight the previous unread article in the list."""
        self._highlight_unread("backward")

    def select_next_article(self) -> None:
        """Select the next article in the list."""
        self.call_later(self.run_action, "cursor_down")
        self.call_later(self.run_action, "select")

    def select_previous_article(self) -> None:
        """Select the previous article in the list."""
        self.call_later(self.run_action, "cursor_up")
        self.call_later(self.run_action, "select")

    def select_next_unread_article(self) -> None:
        """Select the next unread article in the list."""
        if self._highlight_unread("forward"):
            self.call_later(self.run_action, "select")

    def select_previous_unread_article(self) -> None:
        """Select the next unread article in the list."""
        if self._highlight_unread("backward"):
            self.call_later(self.run_action, "select")


### article_list.py ends here
