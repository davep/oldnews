"""Code relating to persisting articles."""

##############################################################################
# Python imports.
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from html import unescape
from typing import cast

##############################################################################
# OldAS imports.
from oldas import Article, Articles, Folder, Folders, State, Subscription
from oldas.articles import Alternate, Alternates, Direction, Origin, Summary

##############################################################################
# Tortoise imports.
from tortoise.transactions import in_transaction

##############################################################################
# Local imports.
from .log import Log
from .models import LocalArticle, LocalArticleAlternate, LocalArticleCategory


##############################################################################
async def save_local_articles(articles: Articles) -> Articles:
    """Locally save the given articles.

    Args:
        articles: The articles to save.

    Returns:
        The articles.
    """
    for article in articles:
        async with in_transaction():
            local_article, _ = await LocalArticle.update_or_create(
                article_id=article.id,
                defaults={
                    "title": article.title,
                    "published": article.published,
                    "updated": article.updated,
                    "author": article.author,
                    "summary_direction": article.summary.direction,
                    "summary_content": article.summary.content,
                    "origin_stream_id": article.origin.stream_id,
                    "origin_title": article.origin.title,
                    "origin_html_url": article.origin.html_url,
                },
            )
            await LocalArticleCategory.filter(article=local_article).delete()
            await LocalArticleCategory.bulk_create(
                LocalArticleCategory(article=local_article, category=str(category))
                for category in article.categories
            )
            await LocalArticleAlternate.filter(article=local_article).delete()
            await LocalArticleAlternate.bulk_create(
                LocalArticleAlternate(
                    article=local_article,
                    href=alternate.href,
                    mime_type=alternate.mime_type,
                )
                for alternate in article.alternate
            )
    return articles


##############################################################################
async def get_local_read_article_ids() -> set[str]:
    """Get the set of local articles that have been read.

    Returns:
        A `set` of IDs of articles that have been read.
    """
    return {
        category.article.article_id
        for category in await LocalArticleCategory.filter(
            category=str(State.READ)
        ).prefetch_related("article")
    }


##############################################################################
async def get_local_articles(
    related_to: Folder | Subscription, unread_only: bool
) -> Articles:
    """Get all available unread articles.

    Args:
        related_to: The folder or feed the articles should relate to.
        unread_only: Only load up the unread articles?

    Returns: The unread articles.
    """
    local_articles = (
        LocalArticle.filter(categories__category=related_to.id)
        if isinstance(related_to, Folder)
        else LocalArticle.filter(origin_stream_id=related_to.id)
    )
    if unread_only and (read := (await get_local_read_article_ids())):
        local_articles = local_articles.filter(article_id__not_in=read)

    articles: list[Article] = []
    for article in await local_articles.prefetch_related(
        "categories", "alternates"
    ).order_by("-published"):
        articles.append(
            Article(
                id=article.article_id,
                title=unescape(article.title),
                published=article.published,
                updated=article.updated,
                author=article.author,
                categories=Article.clean_categories(
                    category.category
                    for category in article.categories  # type: ignore
                ),
                alternate=Alternates(
                    Alternate(href=alternate.href, mime_type=alternate.mime_type)
                    for alternate in article.alternates  # type: ignore
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
async def locally_mark_read(article: Article) -> None:
    """Mark the given article as read.

    Args:
        article: The article to locally mark as read.
    """
    if local_article := await LocalArticle.filter(article_id=article.id).get_or_none():
        await local_article.add_category(str(State.READ))


##############################################################################
async def locally_mark_article_ids_read(articles: Iterable[str]) -> None:
    """Locally mark a collection of article IDs as being read.

    Args:
        articles: The article IDs to mark as read.
    """
    if article_ids := set(articles):
        Log().debug(f"Number of articles to mark as read: {len(article_ids)}")
        await LocalArticleCategory.bulk_create(
            [
                LocalArticleCategory(article=article, category=str(State.READ))
                for article in await LocalArticle.filter(article_id__in=article_ids)
            ],
            ignore_conflicts=True,
        )


##############################################################################
async def unread_count_in(
    category: Folder | Subscription, read: set[str] | None = None
) -> int:
    """Get the count of unread articles in a given category.

    Args:
        category: The category (Folder or Subscription) to get the unread count for.
        read: The set of IDs of read articles.

    Returns:
        The count of unread articles in that category.
    """
    query = (
        LocalArticle.filter(categories__category=category.id)
        if isinstance(category, Folder)
        else LocalArticle.filter(origin_stream_id=category.id)
    )
    if read := read if read is not None else await get_local_read_article_ids():
        query = query.filter(article_id__not_in=read)
    return await query.count()


##############################################################################
async def get_unread_article_ids() -> list[str]:
    """Get a list of all the unread article IDs.

    Returns:
        The list of IDs of unread articles.
    """
    read = await get_local_read_article_ids()
    return [
        article.article_id
        for article in await LocalArticle.filter(article_id__not_in=read)
    ]


##############################################################################
async def clean_old_read_articles(cutoff: timedelta) -> int:
    """Clean up articles that are older than the given cutoff time.

    Args:
        cutoff: The cutoff period after which articles will be removed.

    Returns:
        The number of removed articles.
    """
    read = await get_local_read_article_ids()
    retire_time = datetime.now(UTC) - cutoff
    Log().debug(f"Cleaning up read articles published before {retire_time}")
    cleaned = await LocalArticle.filter(
        published__lt=retire_time, article_id__in=read
    ).delete()
    Log().debug(f"Cleaned: {cleaned}")
    return cleaned


##############################################################################
async def rename_folder_for_articles(rename_from: str | Folder, rename_to: str) -> None:
    """Rename a folder for all articles that are in that folder.

    Args:
        rename_from: The folder name to rename from.
        rename_to: The folder name to rename to.
    """
    rename_from = Folders.full_id(rename_from)
    rename_to = Folders.full_id(rename_to)
    Log().debug(f"Renaming folder for local articles from {rename_from} to {rename_to}")
    await LocalArticleCategory.filter(category=rename_from).update(category=rename_to)


##############################################################################
async def remove_folder_from_articles(folder: str | Folder) -> None:
    """Remove a folder from being associated with all articles.

    Args:
        folder: The folder to remove from all articles.
    """
    folder = Folders.full_id(folder)
    Log().debug(f"Removing folder {folder} from all local articles")
    await LocalArticleCategory.filter(category=folder).delete()


##############################################################################
async def move_subscription_articles(
    subscription: Subscription,
    from_folder: str | Folder | None,
    to_folder: str | Folder | None,
) -> None:
    """Move the articles of a subscription from one folder to another.

    Args:
        subscription: The subscription whose articles we should move.
        from_folder: The folder to move from.
        to_folder: The folder to move to.
    """
    from_folder = (
        Folders.full_id(from_folder) if from_folder is not None else from_folder
    )
    to_folder = Folders.full_id(to_folder) if to_folder is not None else to_folder
    Log().debug(
        f"Moving all articles of {subscription.title} ({subscription.id}) from folder {from_folder} to {to_folder}"
    )
    for article in await LocalArticle.filter(
        origin_stream_id=subscription.id
    ).prefetch_related("categories"):
        if from_folder:
            await article.remove_category(from_folder)
        if to_folder:
            await article.add_category(to_folder)


##############################################################################
async def remove_subscription_articles(subscription: str | Subscription) -> None:
    """Remove all the articles associated with the given subscription.

    Args:
        subscription: The subscription to remove the articles for.
    """
    if isinstance(subscription, Subscription):
        subscription = subscription.id
    Log().debug(f"Removing all local articles for subscription {subscription}")
    deleted = await LocalArticle.filter(origin_stream_id=subscription).delete()
    Log().debug(f"Articles removed that belonged to {subscription}: {deleted}")


### local_articles.py ends here
