"""Code relating to persisting articles."""

##############################################################################
# Python imports.
from datetime import datetime

##############################################################################
# OldAS imports.
from oldas import Article, Articles

##############################################################################
# TypeDAL imports.
from typedal import TypedField, TypedTable


##############################################################################
class LocalArticle(TypedTable):
    """A local copy of an article."""

    article_id: str
    """The ID of the article."""
    title: str
    """The title of the article."""
    published: datetime
    """The time when the article was published."""
    updated: datetime
    """The time when the article was updated."""
    author: str
    """The author of the article."""
    summary_direction: str
    """The direction for the text in the summary."""
    summary_content: TypedField[str] = TypedField(str, type="text")
    """The content of the summary."""
    origin_stream_id: str
    """The stream ID for the article's origin."""
    origin_title: str
    """The title of the origin of the article."""
    origin_html_url: str
    """The URL of the HTML of the origin of the article."""


##############################################################################
class LocalArticleCategory(TypedTable):
    """A local copy of the categories associated with an article."""

    article: str
    """The article that this category belongs to."""
    category: str
    """The category."""


##############################################################################
def save_local_articles(articles: Articles) -> Articles:
    """Locally save the given articles.

    Args:
        articles: The articles to save.

    Returns:
        The articles.
    """
    assert LocalArticle._db is not None
    for article in articles:
        LocalArticleCategory.select(article=article.id).delete()
        LocalArticleCategory.bulk_insert(
            [
                {"article": article.id, "category": str(category)}
                for category in article.categories
            ]
        )
        LocalArticle.update_or_insert(
            LocalArticle.article_id == article.id,
            article_id=article.id,
            title=article.title,
            published=article.published,
            updated=article.updated,
            author=article.author,
            summary_direction=article.summary.direction,
            summary_content=article.summary.content,
            origin_stream_id=article.origin.stream_id,
            origin_title=article.origin.title,
            origin_html_url=article.origin.html_url,
        )
    LocalArticle._db.commit()
    return articles


### local_articles.py ends here
