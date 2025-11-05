"""Code relating to TOR auth."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Local imports.
from .locations import data_dir


##############################################################################
def auth_token_file() -> Path:
    """The location of the token file.

    Returns:
        The path to the token file.
    """
    return data_dir() / ".token"


##############################################################################
def get_auth_token() -> str | None:
    """Get the TOR auth token.

    Returns:
        The token, if there is one, otherwise `None`.
    """
    if not auth_token_file().is_file():
        return None
    return auth_token_file().read_text(encoding="utf-8")


##############################################################################
def set_auth_token(token: str) -> str:
    """Set the TOR auth token for later use.

    Args:
        token: The token to use.

    Returns:
        The token.
    """
    auth_token_file().write_text(token, encoding="utf-8")
    return token


### auth.py ends here
