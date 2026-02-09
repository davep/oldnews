"""Provides tools to dump data into an easy-to-browse format."""

##############################################################################
# Python imports.
from functools import singledispatch
from typing import Any

##############################################################################
# OldAS imports.
from oldas import Article, Folder, Subscription, User

##############################################################################
type DataDump = tuple[tuple[str, str], ...]
"""Type of a data dump."""


##############################################################################
@singledispatch
def data_dump(data: Any) -> DataDump:
    """Dump the given data into an easy-to-browse format.

    Args:
        data: The data to dump.

    Returns:
        A `DataDump` of the data.
    """
    return (("Data", str(data)),)


##############################################################################
@data_dump.register
def _(data: Folder) -> DataDump:
    return (("ID", data.id), ("Sort ID", data.sort_id))


##############################################################################
@data_dump.register
def _(data: Subscription) -> DataDump:
    return (
        ("ID", data.id),
        ("Title", data.title),
        ("Sort ID", data.sort_id),
        ("First Item Time", f"{data.first_item_time}"),
        ("URL", data.url),
        ("HTML URL", data.html_url),
        *(
            (
                f"Category[{n}]",
                f"{category.id}, {category.label}",
            )
            for n, category in enumerate(data.categories)
        ),
    )


##############################################################################
@data_dump.register
def _(data: Article) -> DataDump:
    # TODO: The article has pretty rich data, so in here I'm not showing
    # it all, just enough to be useful. In the future perhaps make it a
    # lot richer.
    return (
        ("ID", data.id),
        ("Title", data.title),
        ("Published", f"{data.published}"),
        ("Updated", f"{data.updated}"),
        *(
            (f"Category[{n}]", f"{category}")
            for n, category in enumerate(data.categories)
        ),
    )


@data_dump.register
def _(data: User) -> DataDump:
    return (
        ("User ID", data.user_id),
        ("Name", data.name),
        ("Profile ID", data.profile_id),
        ("Email", data.email),
        ("Is Blogger User", f"{data.is_blogger_user}"),
        ("Signup Time", f"{data.signup_time}"),
        ("Is Multi-Login Enabled", f"{data.is_multi_login_enabled}"),
        ("Is Premium", f"{data.is_premium}"),
    )


### dump.py ends here
