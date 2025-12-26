"""Code relating to persisting unread counts."""

##############################################################################
# OldAS imports.
from oldas import Count, Counts, Prefix, Unread, id_is_a_feed, id_is_a_folder

##############################################################################
# TypeDAL imports.
from typedal import TypedTable


##############################################################################
class LocalUnread(TypedTable):
    """A local copy of the unread counts."""

    unread_id: str
    """The ID of the unread count."""
    count: int
    """The unread count."""


##############################################################################
def get_local_unread() -> Unread:
    """Get the local copy of the unread counts.

    Returns:
        The local unread counts.
    """
    local_unread = LocalUnread.select(LocalUnread.ALL).collect()
    total = sum(unread.count for unread in local_unread)
    return Unread(
        total,
        folders=Counts(
            Count.from_json(
                {
                    "id": count.unread_id,
                    "count": count.count,
                    "newestItemTimestampUsec": "0",
                },
                Prefix.FOLDER,
            )
            for count in local_unread
            if id_is_a_folder(count.unread_id)
        ),
        feeds=Counts(
            Count.from_json(
                {
                    "id": count.unread_id,
                    "count": count.count,
                    "newestItemTimestampUsec": "0",
                },
                Prefix.FEED,
            )
            for count in local_unread
            if id_is_a_feed(count.unread_id)
        ),
    )


##############################################################################
def save_local_unread(unread: Unread) -> Unread:
    """Locally save the given unread counts.

    Args:
        unread: The unread counts to save.

    Returns:
        The unread counts.
    """
    assert LocalUnread._db is not None
    LocalUnread.truncate()
    LocalUnread.bulk_insert(
        [
            {
                "unread_id": count.id,
                "count": count.unread,
            }
            for count in (*unread.folders, *unread.feeds)
        ]
    )
    LocalUnread._db.commit()
    return unread


### local_unread.py ends here
