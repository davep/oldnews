"""Provides a class to sync data from TheOldReader."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncIterator, Callable, Iterable

##############################################################################
# OldAS imports.
from oldas import (
    Article,
    ArticleIDs,
    Articles,
    Folders,
    Session,
    Subscription,
    Subscriptions,
)

##############################################################################
from .data import (
    LocalUnread,
    get_local_subscriptions,
    get_local_unread,
    get_unread_article_ids,
    last_grabbed_data_at,
    load_configuration,
    locally_mark_article_ids_read,
    remember_we_last_grabbed_at,
    remove_subscription_articles,
    save_local_articles,
    save_local_folders,
    save_local_subscriptions,
)

##############################################################################
type Callback = Callable[[], Any] | None
"""Type of a callback with no arguments."""
type CallbackWith[T] = Callable[[T], Any] | None
"""Type of callback with a single argument."""


##############################################################################
@dataclass
class ToRSync:
    """Class that handles syncing data from TheOldReader."""

    session: Session
    """The TheOldReader API session object."""
    on_new_step: CallbackWith[str] = None
    """Function to call when a new step starts."""
    on_new_result: CallbackWith[str] = None
    """Function to call when a result should be communicated."""
    on_new_folders: CallbackWith[Folders] = None
    """Function to call when new folders are acquired."""
    on_new_subscriptions: CallbackWith[Subscriptions] = None
    """Function to call when new subscriptions are acquired."""
    on_new_unread: CallbackWith[LocalUnread] = None
    """Function to call when new unread counts are calculated."""
    on_sync_finished: Callback = None
    """Function to call when the sync has finished."""

    def __post_init__(self) -> None:
        """Initialise the sync object."""
        self._last_sync = last_grabbed_data_at()
        """The time at which we last did a sync."""
        self._first_sync = self._last_sync is None
        """Is this our first ever sync?"""

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

    async def _download(self, stream: AsyncIterator[Article], description: str) -> int:
        """Download and save articles from an article stream.

        Args:
            stream: The stream to download.
            description: The description of the download.

        Returns:
            The number of articles downloaded.
        """
        loaded = 0
        async for article in stream:
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
                self._step(f"{description}: {loaded}")
        return loaded

    async def _get_updated_read_status(self) -> None:
        """Refresh the read status from the server."""
        if self._first_sync:
            return
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

    async def _download_backlog(self, subscriptions: Iterable[Subscription]) -> None:
        """Download the backlog of articles for the given subscriptions.

        Args:
            subscriptions: The subscriptions to download the backlog for.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(
            days=load_configuration().local_history
        )
        for subscription in subscriptions:
            if loaded := await self._download(
                Articles.stream_new_since(self.session, cutoff, subscription, n=10),
                f"Downloading article backlog for {subscription.title}",
            ):
                self._result(
                    f"Downloaded article backlog for {subscription.title}: {loaded}"
                )

    async def _get_folders(self) -> Folders:
        """Get the list of folders from the server.

        Returns:
            The folders.
        """
        self._step("Getting folder list")
        folders = save_local_folders(await Folders.load(self.session))
        if self.on_new_folders:
            self.on_new_folders(folders)
        return folders

    async def _get_subscriptions(self) -> tuple[Subscriptions, Subscriptions]:
        """Get the list of subscriptions from the server.

        Returns:
            A tuple of the original subscription list before the sync, and
            after.
        """
        self._step("Getting subscriptions list")
        original_subscriptions = get_local_subscriptions()
        subscriptions = save_local_subscriptions(await Subscriptions.load(self.session))
        if self.on_new_subscriptions:
            self.on_new_subscriptions(subscriptions)
        return original_subscriptions, subscriptions

    async def _get_new_articles(self) -> None:
        """Download any new articles."""
        self._step(
            "Getting available articles"
            if self._first_sync
            else f"Getting new articles since {self._last_sync}"
        )
        new_grab = datetime.now(timezone.utc)
        last_grabbed = self._last_sync or (
            new_grab - timedelta(days=load_configuration().local_history)
        )
        if loaded := await self._download(
            Articles.stream_new_since(self.session, last_grabbed, n=10),
            "Downloading articles from TheOldReader",
        ):
            self._result(f"Articles downloaded: {loaded}")
        else:
            self._result("No new articles found on TheOldReader")
        remember_we_last_grabbed_at(new_grab)

    @staticmethod
    def _set_of_ids(subscriptions: Subscriptions) -> set[str]:
        """Get a set of the IDs of the given subscriptions.

        Args:
            subscriptions: The subscriptions to get the IDs of.

        Returns:
            A [set][`set`] of subscription IDs.
        """
        return {subscription.id for subscription in subscriptions}

    async def _get_historical_articles(
        self,
        original_subscriptions: Subscriptions,
        current_subscriptions: Subscriptions,
    ) -> None:
        """Download article histories for any new subscriptions.

        Args:
            original_subscriptions: The known subscriptions before the sync.
            current_subscriptions: The subscriptions we're now subscribed to.

        It's possible we have subscriptions we didn't know about before, so
        we want to go and backfill their content regardless of read or
        unread status. So, if it looks like we've grabbed data before but
        now we have subscriptions we didn't know about before... let's grab
        their history regardless.
        """
        if not self._first_sync and (
            new_subscriptions := self._set_of_ids(current_subscriptions)
            - self._set_of_ids(original_subscriptions)
        ):
            await self._download_backlog(
                subscription
                for subscription in current_subscriptions
                if subscription.id in new_subscriptions
            )

    def _clean_orphaned_articles(
        self,
        original_subscriptions: Subscriptions,
        current_subscriptions: Subscriptions,
    ) -> None:
        """Clean any articles left over from removed subscriptions.

        Args:
            original_subscriptions: The known subscriptions before the sync.
            current_subscriptions: The subscriptions we're now subscribed to.
        """
        if not self._first_sync and (
            removed_subscriptions := self._set_of_ids(original_subscriptions)
            - self._set_of_ids(current_subscriptions)
        ):
            for subscription in removed_subscriptions:
                remove_subscription_articles(subscription)

    async def _get_unread_counts(
        self, folders: Folders, subscriptions: Subscriptions
    ) -> None:
        """Get the updated unread counts."""
        self._step("Calculating unread counts")
        unread = get_local_unread(folders, subscriptions)
        if self.on_new_unread:
            self.on_new_unread(unread)

    async def refresh(self) -> None:
        """Refresh the data from TheOldReader.

        Args:
            session: The TheOldReader API session object.
        """
        folders = await self._get_folders()
        original_subscriptions, subscriptions = await self._get_subscriptions()
        await self._get_new_articles()
        await self._get_updated_read_status()
        await self._get_historical_articles(original_subscriptions, subscriptions)
        self._clean_orphaned_articles(original_subscriptions, subscriptions)
        await self._get_unread_counts(folders, subscriptions)
        if self.on_sync_finished:
            self.on_sync_finished()


### sync.py ends here
