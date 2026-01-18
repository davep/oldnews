"""Provides a class to sync data from TheOldReader."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

##############################################################################
# OldAS imports.
from oldas import ArticleIDs, Articles, Folders, Session, Subscriptions

##############################################################################
from ..data import (
    LocalUnread,
    get_local_unread,
    get_unread_article_ids,
    last_grabbed_data_at,
    load_configuration,
    locally_mark_article_ids_read,
    remember_we_last_grabbed_at,
    save_local_articles,
    save_local_folders,
    save_local_subscriptions,
)


##############################################################################
@dataclass
class ToRSync:
    """Class that handles syncing data from TheOldReader."""

    session: Session
    """The TheOldReader API session object."""
    on_new_step: Callable[[str], Any] | None = None
    """Function to call when a new step starts."""
    on_new_result: Callable[[str], Any] | None = None
    """Function to call when a result should be communicated."""
    on_new_folders: Callable[[Folders], Any] | None = None
    """Function to call when new folders are acquired."""
    on_new_subscriptions: Callable[[Subscriptions], Any] | None = None
    """Function to call when new subscriptions are acquired."""
    on_new_unread: Callable[[LocalUnread], Any] | None = None
    """Function to call when new unread counts are calculated."""
    on_sync_funished: Callable[[], Any] | None = None
    """Function to call when the sync has finished."""

    def _step(self, step: str) -> None:
        """Mark a new step.

        Args:
            step: The step that is happening.
        """
        if self.on_new_step:
            self.on_new_step(step)

    def _result(self, result: str) -> None:
        """Show a new result.

        Args:
            result: The result that should be shown.
        """
        if self.on_new_result:
            self.on_new_result(result)

    async def _download_newest_articles(self) -> None:
        """Download the latest articles available."""
        last_grabbed = last_grabbed_data_at() or (
            datetime.now() - timedelta(days=load_configuration().local_history)
        )
        new_grab = datetime.now(timezone.utc)
        loaded = 0
        async for article in Articles.stream_new_since(
            self.session, last_grabbed, n=10
        ):
            # I've encountered articles that don't have an origin stream ID,
            # which means that I can't relate them back to a stream, which
            # means I'll never see them anyway...
            if not article.origin.stream_id:
                continue
            # TODO: Right now I'm saving articles one at a time; perhaps I
            # should save them in small batches? This would be simple enough
            # -- perhaps same them in batches the same size as the buffer
            # window I'm using right now (currently 10 articles per trip to
            # ToR).
            save_local_articles(Articles([article]))
            loaded += 1
            if (loaded % 10) == 0:
                self._step(f"Downloading articles from TheOldReader: {loaded}")
        if loaded:
            self._result(f"Articles downloaded: {loaded}")
        else:
            self._result("No new articles found on TheOldReader")
        remember_we_last_grabbed_at(new_grab)

    async def _refresh_read_status(self) -> None:
        """Refresh the read status from the server."""
        self._step("Getting list of unread articles from TheOldReader")
        remote_unread_articles = set(
            article_id.full_id
            for article_id in await ArticleIDs.load_unread(self.session)
        )
        self._step("Comparing against locally-read articles")
        local_unread_articles = set(get_unread_article_ids())
        if mark_as_read := local_unread_articles - remote_unread_articles:
            locally_mark_article_ids_read(mark_as_read)
            self._result(
                f"Articles found read elsewhere on TheOldReader: {len(mark_as_read)}"
            )

    async def refresh(self) -> None:
        """Refresh the data from TheOldReader.

        Args:
            session: The TheOldReader API session object.
        """

        # Get the folder list.
        self._step("Getting folder list")
        folders = save_local_folders(await Folders.load(self.session))
        if self.on_new_folders:
            self.on_new_folders(folders)

        # Get the subscriptions list.
        self._step("Getting subscriptions list")
        subscriptions = save_local_subscriptions(await Subscriptions.load(self.session))
        if self.on_new_subscriptions:
            self.on_new_subscriptions(subscriptions)

        # Download the latest articles we don't know about.
        if never_grabbed_before := ((last_grab := last_grabbed_data_at()) is None):
            self._step("Getting available articles")
        else:
            self._step(f"Getting new articles since {last_grab}")
        await self._download_newest_articles()

        # If we have grabbed data before, let's try and sync up what's been read.
        if not never_grabbed_before:
            await self._refresh_read_status()

        # Recalculate the unread counts.
        self._step("Calculating unread counts")
        unread = get_local_unread(folders, subscriptions)
        if self.on_new_unread:
            self.on_new_unread(unread)

        # Finally we're all done.
        if self.on_sync_funished:
            self.on_sync_funished()


### sync.py ends here
