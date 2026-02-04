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
from .dump import data_dump
from .last_grab import last_grabbed_data_at, remember_we_last_grabbed_at
from .local_articles import (
    clean_old_read_articles,
    get_local_articles,
    get_unread_article_ids,
    locally_mark_article_ids_read,
    locally_mark_read,
    move_subscription_articles,
    remove_folder_from_articles,
    remove_subscription_articles,
    rename_folder_for_articles,
    save_local_articles,
)
from .local_data import initialise_local_data, shutdown_local_data
from .local_folders import get_local_folders, save_local_folders
from .local_subscriptions import get_local_subscriptions, save_local_subscriptions
from .local_unread import LocalUnread, get_local_unread, total_unread
from .log import Log
from .navigation_state import get_navigation_state, save_navigation_state
from .reset import reset_data

##############################################################################
# Exports.
__all__ = [
    "Configuration",
    "Log",
    "clean_old_read_articles",
    "data_dump",
    "get_auth_token",
    "get_local_articles",
    "get_local_folders",
    "get_local_subscriptions",
    "get_local_unread",
    "get_navigation_state",
    "get_unread_article_ids",
    "initialise_database",
    "initialise_local_data",
    "last_grabbed_data_at",
    "load_configuration",
    "locally_mark_read",
    "locally_mark_article_ids_read",
    "LocalUnread",
    "move_subscription_articles",
    "remember_we_last_grabbed_at",
    "remove_folder_from_articles",
    "remove_subscription_articles",
    "rename_folder_for_articles",
    "reset_data",
    "save_configuration",
    "save_local_articles",
    "save_local_folders",
    "save_local_subscriptions",
    "save_navigation_state",
    "shutdown_local_data",
    "set_auth_token",
    "total_unread",
    "update_configuration",
]

### __init__.py ends here
