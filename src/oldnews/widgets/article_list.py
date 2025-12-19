"""Widget to show a list of articles."""

##############################################################################
# OldAs imports.
from oldas import Articles

##############################################################################
# Textual imports.
from textual.reactive import var

##############################################################################
# Textual enhanced imports.
from textual_enhanced.widgets import EnhancedOptionList


##############################################################################
class ArticleList(EnhancedOptionList):
    """Widget for showing a list of articles."""

    articles: var[Articles] = var(Articles)
    """The list of articles to show."""

    def _watch_articles(self) -> None:
        """React to the article list being changed."""
        self.clear_options().add_options([article.title for article in self.articles])
        if self.option_count:
            self.highlighted = 0


### article_list.py ends here
