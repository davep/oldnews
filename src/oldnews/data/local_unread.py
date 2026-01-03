"""Code relating to unread counts."""

##############################################################################
# OldAS imports.
from oldas import Folders, Subscriptions, id_is_a_folder

##############################################################################
# Local imports.
from .local_articles import get_local_read_article_ids, unread_count_in

##############################################################################
LocalUnread = dict[str, int]
"""Type of the local unread data."""


##############################################################################
def get_local_unread(folders: Folders, subscriptions: Subscriptions) -> LocalUnread:
    """Get the local unread counts.

    Args:
        folders: The folders we know about.
        subscriptions: The subscriptions we know about.

    Returns:
        The local unread counts.
    """
    read = get_local_read_article_ids()
    unread = LocalUnread()
    for category in [*folders, *subscriptions]:
        unread[category.id] = unread_count_in(category, read)
    return unread


##############################################################################
def total_unread(unread: LocalUnread) -> int:
    """Calculate the total unread.

    Args:
        unread: The unread counts.

    Returns:
        The total unread.
    """
    return sum(count for category, count in unread.items() if id_is_a_folder(category))


### local_unread.py ends here
