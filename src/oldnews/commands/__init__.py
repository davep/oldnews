"""Provides the command messages for the application."""

##############################################################################
# Local imports.
from .admin import (
    AddSubscription,
    MoveSubscription,
    Remove,
    Rename,
    SetSubscriptionContentFilter,
)
from .copying import (
    Copy,
    CopyArticleToClipboard,
    CopyFeedToClipboard,
    CopyHomePageToClipboard,
)
from .main import (
    Information,
    RefreshFromTheOldReader,
    UserInformation,
)
from .marking import (
    MarkAllRead,
    MarkRead,
    MarkUnread,
)
from .navigation import (
    Escape,
    Next,
    NextUnread,
    Previous,
    PreviousUnread,
)
from .opening import (
    OpenArticle,
    OpenHomePage,
)
from .ui import (
    ToggleCompact,
    ToggleShowAll,
)

##############################################################################
# Exports.
__all__ = [
    "AddSubscription",
    "Copy",
    "CopyArticleToClipboard",
    "CopyFeedToClipboard",
    "CopyHomePageToClipboard",
    "Escape",
    "Information",
    "MarkAllRead",
    "MarkRead",
    "MarkUnread",
    "Next",
    "NextUnread",
    "MoveSubscription",
    "OpenArticle",
    "OpenHomePage",
    "Previous",
    "PreviousUnread",
    "RefreshFromTheOldReader",
    "Rename",
    "Remove",
    "SetSubscriptionContentFilter",
    "ToggleCompact",
    "ToggleShowAll",
    "UserInformation",
]

### __init__.py ends here
