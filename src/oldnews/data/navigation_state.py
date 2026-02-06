"""Code relating to persisting the state of navigation."""

##############################################################################
# Tortoise imports.
from tortoise.transactions import in_transaction

##############################################################################
# Local imports.
from .models import NavigationState


##############################################################################
async def get_navigation_state() -> set[str]:
    """Get the navigation state.

    Returns:
        The saved navigation state.
    """
    return {state.expanded_folder_id for state in await NavigationState.all()}


##############################################################################
async def save_navigation_state(state: set[str]) -> None:
    """Save the navigation state.

    Args:
        state: The state to save.
    """
    async with in_transaction():
        await NavigationState.all().delete()
        await NavigationState.bulk_create(
            NavigationState(expanded_folder_id=folder) for folder in state
        )


### navigation_state.py ends here
