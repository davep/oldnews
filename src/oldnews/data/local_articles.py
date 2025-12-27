"""Code relating to persisting articles."""

##############################################################################
# Python imports.
from datetime import datetime
from typing import Iterator, cast

##############################################################################
# OldAS imports.
from oldas import Article, Articles, Folder, State, Subscription
from oldas.articles import Direction, Origin, Summary

##############################################################################
# TypeDAL imports.
from typedal import TypedField, TypedTable, relationship


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
    categories = relationship(
        list["LocalArticleCategory"],
        condition=lambda article, category: cast(LocalArticle, article).id
        == cast(LocalArticleCategory, category).article,
        join="left",
    )


##############################################################################
class LocalArticleCategory(TypedTable):
    """A local copy of the categories associated with an article."""

    article: LocalArticle
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
        local_article = LocalArticle.update_or_insert(
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
        LocalArticleCategory.where(article=local_article.id).delete()
        LocalArticleCategory.bulk_insert(
            [
                {"article": local_article.id, "category": str(category)}
                for category in article.categories
            ]
        )
    LocalArticle._db.commit()
    return articles


##############################################################################
def _for_subscription(subscription: Subscription) -> Iterator[LocalArticle]:
    """Get all unread articles for a given subscription.

    Args:
        subscription: The subscription to get the articles for.

    Yields:
        The unread articles.
    """
    read = {
        category.article.id
        for category in LocalArticleCategory.where(
            LocalArticleCategory.category == State.READ
        ).collect()
    }
    for article in (
        LocalArticle.where(~LocalArticle.id.belongs(read))
        .where(origin_stream_id=subscription.id)
        .join()
    ):
        yield article


##############################################################################
def _for_folder(folder: Folder) -> Iterator[LocalArticle]:
    """Get all unread articles for a given folder.

    Args:
        folder: The folder to get the articles for.

    Yields:
        The unread articles.
    """
    in_folder = {
        category.article.id
        for category in LocalArticleCategory.where(
            LocalArticleCategory.category == folder.id
        ).collect()
    }
    read = {
        category.article.id
        for category in LocalArticleCategory.where(
            LocalArticleCategory.category == State.READ
        ).collect()
    }
    for article in (
        LocalArticle.where(LocalArticle.id.belongs(in_folder - read)).select().join()
    ):
        yield article


##############################################################################
def get_local_unread_articles(related_to: Folder | Subscription) -> Articles:
    """Get all available unread articles.

    Args:
        related_to: The folder or feed the articles should relate to.

    Returns:
        The unread articles.

    Notes:
        TODO: This isn't the final form of this function, this is just an
        experiment to get the loading of unread articles going. Eventually I
        will be narrowing things down.
    """
    articles: list[Article] = []
    for article in (
        _for_folder(related_to)
        if isinstance(related_to, Folder)
        else _for_subscription(related_to)
    ):
        articles.append(
            Article(
                id=article.article_id,
                title=article.title,
                published=article.published,
                updated=article.updated,
                author=article.author,
                categories=Article.clean_categories(
                    category.category for category in article.categories
                ),
                origin=Origin(
                    stream_id=article.origin_stream_id,
                    title=article.origin_title,
                    html_url=article.origin_html_url,
                ),
                summary=Summary(
                    direction=cast(Direction, article.summary_direction),
                    content=article.summary_content,
                ),
            )
        )
    return Articles(articles)


### local_articles.py ends here
