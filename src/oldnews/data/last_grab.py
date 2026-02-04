"""Code relating to remembering when we last grabbed data."""

##############################################################################
# Python imports.
from datetime import UTC, datetime

##############################################################################
# Local imports.
from .models import LastGrabbed


##############################################################################
async def last_grabbed_data_at() -> datetime | None:
    """The time at which data was last grabbed.

    Returns:
        The time at which we last grabbed data, or `None` if we never have.
    """
    if (row := LastGrabbed.first()) and (last_grabbed := (await row)):
        return last_grabbed.at_time
    return None


##############################################################################
async def remember_we_last_grabbed_at(grab_time: datetime | None = None) -> None:
    """Remember the time we last grabbed data.

    Args:
        grab_time: The time the grab was done.

    Note:
        If `grab_time` isn't supplied then it is recorded as now.
    """
    await LastGrabbed.all().delete()
    await LastGrabbed.create(at_time=grab_time or datetime.now(UTC))


### last_grab.py ends here
