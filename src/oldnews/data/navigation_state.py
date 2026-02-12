"""Code relating to persisting the state of navigation."""

##############################################################################
# OldAS imports.
from oldas import Folder, Folders

##############################################################################
# Tortoise imports.
from tortoise.transactions import in_transaction

##############################################################################
# Local imports.
from .log import Log
from .models import NavigationState


##############################################################################
async def get_navigation_state() -> set[str]:
    """Get the navigation state.

    Returns:
        The saved navigation state.
    """
    Log().debug("Loading navigation state")
    return {state.expanded_folder_id for state in await NavigationState.all()}


##############################################################################
async def save_navigation_state(state: set[str]) -> None:
    """Save the navigation state.

    Args:
        state: The state to save.
    """
    Log().debug("Saving navigation state")
    async with in_transaction():
        await NavigationState.all().delete()
        await NavigationState.bulk_create(
            NavigationState(expanded_folder_id=folder) for folder in state
        )


##############################################################################
async def rename_folder_in_navigation_state(
    folder: Folder | str, rename_to: Folder | str
) -> None:
    """Rename any mention of the given folder in the navigation state.

    Args:
        folder: The folder being renamed.
        rename_to: The new name for the folder.
    """
    rename_from = Folders.full_id(folder)
    rename_to = Folders.full_id(rename_to)
    Log().debug(f"Replacing {rename_from} with {rename_to} in navigation state")
    if is_expanded := await NavigationState.get_or_none(expanded_folder_id=rename_from):
        async with in_transaction():
            await is_expanded.delete()
            await NavigationState.create(expanded_folder_id=rename_to)


### navigation_state.py ends here
