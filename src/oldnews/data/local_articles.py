"""Code relating to persisting articles."""

##############################################################################
# Python imports.
from datetime import datetime
from html import unescape
from typing import Iterable, Iterator, cast

##############################################################################
# OldAS imports.
from oldas import Article, Articles, Folder, State, Subscription
from oldas.articles import Alternate, Alternates, Direction, Origin, Summary

##############################################################################
# TypeDAL imports.
from typedal import TypedField, TypedTable, relationship


##############################################################################
class LocalArticle(TypedTable):
    """A local copy of an article."""

    article_id: TypedField[str]
    """The ID of the article."""
    title: str
    """The title of the article."""
    published: TypedField[datetime] = TypedField(datetime)
    """The time when the article was published."""
    updated: TypedField[datetime] = TypedField(datetime)
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
    """The categories associated with this article."""
    alternate = relationship(
        list["LocalArticleAlternate"],
        condition=lambda article, alternate: cast(LocalArticle, article).id
        == cast(LocalArticleAlternate, alternate).article,
        join="left",
    )
    """The alternates for the article."""

    def add_category(self, category: str | State) -> None:
        """Add a given category to the local article.

        Args:
            category: The category to add.
        """
        if not str(category) in self.categories:
            assert LocalArticleCategory._db is not None
            LocalArticleCategory.insert(article=self.id, category=str(category))
            LocalArticleCategory._db.commit()

    def remove_category(self, category: str | State) -> None:
        """Remove a given category from the local article.

        Args:
            category: The category to add.
        """
        if str(category) in self.categories:
            assert LocalArticleCategory._db is not None
            LocalArticleCategory.where(
                (LocalArticleCategory.article == self.id)
                & (LocalArticleCategory.category == str(category))
            ).delete()
            LocalArticleCategory._db.commit()


##############################################################################
class LocalArticleCategory(TypedTable):
    """A local copy of the categories associated with an article."""

    article: LocalArticle
    """The article that this category belongs to."""
    category: str
    """The category."""


##############################################################################
class LocalArticleAlternate(TypedTable):
    """A local copy of the alternate URLs associated with an article."""

    article: LocalArticle
    """The article that this alternate belongs to."""
    href: str
    """The URL of the alternate."""
    mime_type: str
    """The MIME type of the alternate."""


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
        LocalArticleAlternate.where(article=local_article.id).delete()
        LocalArticleAlternate.bulk_insert(
            [
                {
                    "article": local_article.id,
                    "href": alternate.href,
                    "mime_type": alternate.mime_type,
                }
                for alternate in article.alternate
            ]
        )
    LocalArticle._db.commit()
    return articles


##############################################################################
def get_local_read_article_ids() -> set[int]:
    """Get the set of local articles that have been read.

    Returns:
        A `set` of IDs of articles that have been read.
    """
    return {
        category.article.id
        for category in LocalArticleCategory.where(
            LocalArticleCategory.category == State.READ
        ).collect()
    }


##############################################################################
def _for_subscription(
    subscription: Subscription, unread_only: bool
) -> Iterator[LocalArticle]:
    """Get all unread articles for a given subscription.

    Args:
        subscription: The subscription to get the articles for.
        unread_only: Only load up the unread articles?

    Yields:
        The articles.
    """
    read = get_local_read_article_ids() if unread_only else set()
    for article in (
        LocalArticle.where(~LocalArticle.id.belongs(read))
        .where(origin_stream_id=subscription.id)
        .join()
        .orderby(~LocalArticle.published)
    ):
        yield article


##############################################################################
def _for_folder(folder: Folder, unread_only: bool) -> Iterator[LocalArticle]:
    """Get all unread articles for a given folder.

    Args:
        folder: The folder to get the articles for.
        unread_only: Only load up the unread articles?

    Yields:
        The unread articles.
    """
    in_folder = {
        category.article.id
        for category in LocalArticleCategory.where(
            LocalArticleCategory.category == folder.id
        ).collect()
    }
    read = get_local_read_article_ids() if unread_only else set()
    for article in (
        LocalArticle.where(LocalArticle.id.belongs(in_folder - read))
        .select()
        .join()
        .orderby(~LocalArticle.published)
    ):
        yield article


##############################################################################
def get_local_articles(
    related_to: Folder | Subscription, unread_only: bool
) -> Articles:
    """Get all available unread articles.

    Args:
        related_to: The folder or feed the articles should relate to.
        unread_only: Only load up the unread articles?

    Returns: The unread articles.
    """
    articles: list[Article] = []
    for article in (
        _for_folder(related_to, unread_only)
        if isinstance(related_to, Folder)
        else _for_subscription(related_to, unread_only)
    ):
        articles.append(
            Article(
                id=article.article_id,
                title=unescape(article.title),
                published=article.published,
                updated=article.updated,
                author=article.author,
                categories=Article.clean_categories(
                    category.category for category in article.categories
                ),
                alternate=Alternates(
                    Alternate(href=alternate.href, mime_type=alternate.mime_type)
                    for alternate in article.alternate
                ),
                origin=Origin(
                    stream_id=article.origin_stream_id,
                    title=unescape(article.origin_title),
                    html_url=article.origin_html_url,
                ),
                summary=Summary(
                    direction=cast(Direction, article.summary_direction),
                    content=article.summary_content,
                ),
            )
        )
    return Articles(articles)


##############################################################################
def locally_mark_read(article: Article) -> None:
    """Mark the given article as read.

    Args:
        article: The article to locally mark as read.
    """
    if local_article := LocalArticle.where(
        LocalArticle.article_id == article.id
    ).first():
        local_article.add_category(State.READ)


##############################################################################
def locally_mark_article_ids_read(articles: Iterable[str]) -> None:
    """Locally mark a collection of article IDs as being read.

    Args:
        articles: The article IDs to mark as read.
    """
    for local_article in LocalArticle.where(LocalArticle.article_id.belongs(articles)):
        local_article.add_category(State.READ)


##############################################################################
def unread_count_in(
    category: Folder | Subscription, read: set[int] | None = None
) -> int:
    """Get the count of unread articles in a given category.

    Args:
        category: The category to get the unread count for.
        read: The set of IDs of read articles.

    Returns:
        The count of unread articles in that category.

    Notes:
        Note that `read` is optional and will be worked out of not passed,
        but if this function is being called in a tight loop it's more
        efficient to provide this externally.
    """
    read = get_local_read_article_ids() if read is None else read
    if isinstance(category, Folder):
        in_folder = {
            category.article.id
            for category in LocalArticleCategory.where(
                LocalArticleCategory.category == category.id
            ).collect()
        }
        return LocalArticle.where(LocalArticle.id.belongs(in_folder - read)).count()
    return (
        LocalArticle.where(~LocalArticle.id.belongs(read))
        .where(origin_stream_id=category.id)
        .count()
    )


##############################################################################
def get_unread_article_ids() -> list[str]:
    """Get a list of all the unread article IDs.

    Returns:
        The list of IDs of unread articles.
    """
    read = get_local_read_article_ids()
    return [
        article.article_id
        for article in LocalArticle.where(~LocalArticle.id.belongs(read)).select()
    ]


### local_articles.py ends here
