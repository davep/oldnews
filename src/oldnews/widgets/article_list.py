"""Widget to show a list of articles."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# OldAs imports.
from oldas import Article, Articles

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

    def __init__(self, article: Article) -> None:
        """Initialise the article object.

        Args:
            article: The article to view.
        """
        self._article = article
        """The article to view."""
        header = Table.grid(expand=True)
        header.add_column(width=2)
        header.add_column(ratio=1)
        header.add_row("!" if article.is_unread else "", escape(article.title))
        provenance = (
            f"{article.origin.title}, {article.author}"
            if article.author and article.author != article.origin.title
            else article.origin.title
        )
        details = Table.grid(expand=True)
        details.add_column(width=2)
        details.add_column(ratio=1)
        details.add_column(width=20, justify="right")
        details.add_row(
            "", f"[dim italic]{escape(provenance)}[/]", f"[dim]{article.published}[/]"
        )
        super().__init__(Group(header, details))

    @property
    def article(self) -> Article:
        """The article being viewed."""
        return self._article


##############################################################################
class ArticleList(EnhancedOptionList):
    """Widget for showing a list of articles."""

    articles: var[Articles] = var(Articles)
    """The list of articles to show."""

    @dataclass
    class ViewArticle(Message):
        article: Article
        """The article to view."""

    def _watch_articles(self) -> None:
        """React to the article list being changed."""
        self.clear_options().add_options(
            [ArticleView(article) for article in self.articles]
        )
        if self.option_count:
            self.highlighted = 0

    @on(EnhancedOptionList.OptionSelected)
    def _select_article(self, message: EnhancedOptionList.OptionSelected) -> None:
        """Select an article to view.

        Args:
            message: The message to handle.
        """
        assert isinstance(message.option, ArticleView)
        self.post_message(self.ViewArticle(message.option.article))


### article_list.py ends here
