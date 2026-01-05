"""Widget to show a list of articles."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from typing import Iterator, Literal, cast

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
class ArticleView(Option):
    """The view of an article in the article list."""

    def __init__(self, article: Article, showing_subscription: bool) -> None:
        """Initialise the article object.

        Args:
            article: The article to view.
            showing_subscription: Is the article list showing a subscription?
        """
        self._article = article
        """The article to view."""
        header = Table.grid(expand=True)
        header.add_column(width=2)
        header.add_column(ratio=1)
        if article.is_unread:
            header.add_row("[green]●[/]", escape(article.title))
        else:
            header.add_row("", f"[dim bold]{escape(article.title)}[/]")
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
        details.add_row(
            "",
            f"[dim italic]{escape(provenance)}[/]",
            f"[dim]{article.published.astimezone().strftime('%Y-%m-%d %H:%M:%S')}[/]",
        )
        super().__init__(Group(header, details), id=article.id)

    @property
    def article(self) -> Article:
        """The article being viewed."""
        return self._article


##############################################################################
UnreadSearchDirection = Literal["next", "previous"]
"""Type of a unread search direction."""


##############################################################################
class ArticleList(EnhancedOptionList):
    """Widget for showing a list of articles."""

    HELP = """
    ## The articles

    This panel shows the available articles for the folder or subscription
    that is highlighted in the navigation panel.
    """

    current_category: var[Folder | Subscription | None] = var(None)
    """The category of articles being shown."""
    articles: var[Articles] = var(Articles)
    """The list of articles to show."""

    @dataclass
    class ViewArticle(Message):
        """Message that requests that we view a specific article."""

        article: Article
        """The article to view."""

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
        showing_subscription = isinstance(self.current_category, Subscription)
        with self.preserved_highlight:
            self.set_options(
                [
                    ArticleView(article, showing_subscription)
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

    @on(EnhancedOptionList.OptionSelected)
    def _select_article(self, message: EnhancedOptionList.OptionSelected) -> None:
        """Select an article to view.

        Args:
            message: The message to handle.
        """
        assert isinstance(message.option, ArticleView)
        self.post_message(self.ViewArticle(message.option.article))

    def _unread_articles_after_highlight(
        self, direction: UnreadSearchDirection
    ) -> Iterator[ArticleView]:
        """Return a list of all articles after the highlight.

        Args:
            direction: The direction to search in.

        Returns:
            An iterator of `ArticleView` objects that show an unread article.

        Notes:
            If there is no highlight, we default at position 0.
        """
        highlight = self.highlighted or 0
        options = (
            list(reversed(self.options)) if direction == "previous" else self.options
        )
        highlight = (
            (len(options) - highlight - 1) if direction == "previous" else highlight
        )
        return (
            article_view
            for article_view in cast(
                list[ArticleView], [*options[highlight:], *options[0:highlight]]
            )[1:]
            if article_view.article.is_unread
        )

    def _highlight_unread(self, direction: UnreadSearchDirection) -> bool:
        """Highlight the next unread article, if there is one.

        Args:
            direction: The direction to search.

        Returns:
            `True` if an unread article was found and highlighted, `False`
            if not.
        """
        if next_hit := next(self._unread_articles_after_highlight(direction), None):
            if next_hit.id is not None:
                self.highlighted = self.get_option_index(next_hit.id)
                return True
        self.notify("No more unread articles")
        return False

    def highlight_next_unread(self) -> None:
        """Highlight the next unread article in the list."""
        self._highlight_unread("next")

    def highlight_previous_unread(self) -> None:
        """Highlight the previous unread article in the list."""
        self._highlight_unread("previous")

    def select_next_unread(self) -> None:
        """Select the next unread article in the list."""
        if self._highlight_unread("next"):
            self.call_later(self.run_action, "select")

    def select_previous_unread(self) -> None:
        """Select the next unread article in the list."""
        if self._highlight_unread("previous"):
            self.call_later(self.run_action, "select")


### article_list.py ends here
