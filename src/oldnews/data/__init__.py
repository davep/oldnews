"""Provides functions and classes for managing the app's data."""

##############################################################################
# Local imports.
from .auth import get_auth_token, set_auth_token
from .config import (
    Configuration,
    load_configuration,
    save_configuration,
    update_configuration,
)
from .db import initialise_database
from .local_articles import save_local_articles
from .local_folders import get_local_folders, save_local_folders
from .local_subscriptions import get_local_subscriptions, save_local_subscriptions
from .navigation_state import get_navigation_state, save_navigation_state

##############################################################################
# Exports.
__all__ = [
    "Configuration",
    "get_auth_token",
    "initialise_database",
    "get_navigation_state",
    "load_configuration",
    "save_configuration",
    "save_navigation_state",
    "set_auth_token",
    "update_configuration",
    "save_local_folders",
    "get_local_folders",
    "save_local_articles",
    "save_local_subscriptions",
    "get_local_subscriptions",
]

### __init__.py ends here
