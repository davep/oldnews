"""Code relating to persisting the state of navigation."""

##############################################################################
# TypeDAL imports.
from typedal import TypedTable


##############################################################################
class NavigationState(TypedTable):
    """Table that holds state of the navigation table."""

    expanded_folder_id: str
    """The ID of a folder that is in the expanded state."""


##############################################################################
def get_navigation_state() -> set[str]:
    """Get the navigation state.

    Returns:
        The saved navigation state.
    """
    return set(
        row.expanded_folder_id
        for row in NavigationState.select(NavigationState.expanded_folder_id)
    )


##############################################################################
def save_navigation_state(state: set[str]) -> None:
    """Save the navigation state.

    Args:
        state: The state to save.
    """
    assert NavigationState._db is not None
    NavigationState.truncate()
    NavigationState.bulk_insert([{"expanded_folder_id": folder} for folder in state])
    NavigationState._db.commit()


### navigation_state.py ends here
