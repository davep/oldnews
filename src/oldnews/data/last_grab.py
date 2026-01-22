"""Code relating to remembering when we last grabbed data."""

##############################################################################
# Python imports.
from datetime import datetime, timezone

##############################################################################
# TypeDAL imports.
from typedal import TypedTable

##############################################################################
# Local imports.
from .tools import commit


##############################################################################
class LastGrabbed(TypedTable):
    """Table that holds details of when data was last grabbed."""

    at_time: datetime
    """The time at which data was last grabbed."""


##############################################################################
def last_grabbed_data_at() -> datetime | None:
    """The time at which data was last grabbed.

    Returns:
        The time at which we last grabbed data, or `None` if we never have.
    """
    if (row := LastGrabbed.select(LastGrabbed.ALL).first()) is not None:
        return row.at_time
    return None


##############################################################################
def remember_we_last_grabbed_at(grab_time: datetime | None = None) -> None:
    """Remember the time we last grabbed data.

    Args:
        grab_time: The time the grab was done.

    Note:
        If `grab_time` isn't supplied then it is recorded as now.
    """
    LastGrabbed.truncate()
    LastGrabbed.insert(at_time=grab_time or datetime.now(timezone.utc))
    commit(LastGrabbed)


### last_grab.py ends here
