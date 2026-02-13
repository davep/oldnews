"""Provides code for getting and tidying the content of an article."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# BeautifulSoup imports.
from bs4 import BeautifulSoup

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
# Local imports.
from . import __user_agent__
from .data import Log, get_content_grab_filter_for


##############################################################################
@dataclass
class NoContent:
    """Type returned if no content could be found for the article."""

    reason: str
    """The reason given for failing to find the content."""


##############################################################################
async def _download_content_from(url: str) -> str:
    """Download the content of the given URL.

    Args:
        url: The URL to download from.

    Returns:
        The HTML downloaded from the URL.

    Raises:
        RequestError: If there was an error getting to the site.
        HTTPStatusError: If there was an error with the site.
    """
    async with AsyncClient() as client:
        (
            response := await client.get(
                url,
                follow_redirects=True,
                headers={"user-agent": __user_agent__},
            )
        ).raise_for_status()
    return response.text


##############################################################################
async def _filter_content(article: Article, content: str) -> str:
    """Filter the content based on any defined filter.

    Args:
        article: The article to get the filter for.
        content: The content to filter.
    """
    Log().debug(
        f"Looking for content filter for article {article.id} in subscription {article.origin.stream_id}"
    )
    if article.origin.stream_id and (
        content_filter := await get_content_grab_filter_for(article.origin.stream_id)
    ):
        Log().debug(f"Found selector '{content_filter}'")
        if target_content := BeautifulSoup(content, "html.parser").select_one(
            content_filter
        ):
            content = str(target_content)
        else:
            Log().warning(
                f"The selector '{content_filter}' matched nothing; falling back to downloaded content"
            )
    else:
        Log().debug(f"No selector found for subscription {article.origin.stream_id}")
    return content


##############################################################################
async def download_content_of(article: Article) -> str | NoContent:
    """Download the content of the given article.

    Args:
        article: The article to download the content of.

    Returns:
        Either the content of the article as a string, or an instance of
        `NoContent`.
    """

    # Be sure that we've got somewhere to go to.
    if not article.html_url:
        return NoContent("There is no URL for the article")

    try:
        article_content = await _download_content_from(article.html_url)
    except (RequestError, HTTPStatusError) as error:
        return NoContent(str(error))

    return convert(
        await _filter_content(article, article_content),
        ConversionOptions(extract_metadata=False, skip_images=True),
    )


### content.py ends here
