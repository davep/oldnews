"""Code relating to persisting unread counts."""

##############################################################################
# OldAS imports.
from oldas import Folders, Subscriptions

##############################################################################
# Local imports.
from .local_articles import unread_count_in

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
    unread: LocalUnread = {}
    for category in [*folders, *subscriptions]:
        unread[category.id] = unread_count_in(category)
    return unread


### local_unread.py ends here
