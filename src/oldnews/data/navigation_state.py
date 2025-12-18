"""Code relating to persisting the state of navigation."""

##############################################################################
# Python imports.
from json import JSONDecodeError, dumps, loads
from pathlib import Path

##############################################################################
# Local imports.
from .locations import data_dir


##############################################################################
def navigation_state_file() -> Path:
    """The location of the navigation state file.

    Returns:
        The path to the navigation state file.
    """
    return data_dir() / "navigation-state.json"


##############################################################################
def get_navigation_state() -> set[str]:
    """Get the navigation state.

    Returns:
        The saved navigation state.
    """
    try:
        return set(loads(navigation_state_file().read_text(encoding="utf-8")))
    except (JSONDecodeError, OSError):
        return set()


##############################################################################
def save_navigation_state(state: set[str]) -> None:
    """Save the navigation state.

    Args:
        state: The state to save.
    """
    try:
        navigation_state_file().write_text(
            dumps(list(state), indent=4), encoding="utf-8"
        )
    except OSError:
        pass


### navigation_state.py ends here
