"""Database tool functions."""

##############################################################################
# Python imports.
from typing import Any

##############################################################################
# TypeDAL imports.
from typedal import TypedField, TypedTable
from typedal.helpers import get_db, get_field
from typedal.types import Field


##############################################################################
def safely_index(
    table: type[TypedTable], name: str, field: str | Field | TypedField[Any]
) -> None:
    """Create an index on a type, but handle errors.

    Args:
        table: The table to create the index against.
        name: The name of the index.
        field: The field to index.

    Notes:
        From what I can gather TypeDAL *should* only create the index if it
        doesn't exist. Instead it throws an error if it exists. So here I
        swallow the `RuntimeError`. Hopefully there is a better way and I've
        just missed it.
    """
    try:
        table.create_index(
            name, get_field(field) if isinstance(field, TypedField) else field
        )
    except RuntimeError:
        pass


##############################################################################
def commit(table: type[TypedTable]) -> None:
    """Commit changes."""
    get_db(table()).commit()


### tools.py ends here
