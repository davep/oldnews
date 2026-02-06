"""Code relating to persisting the known list of folders."""

##############################################################################
# OldAS imports.
from oldas import Folder, Folders

##############################################################################
# Tortoise imports.
from tortoise.transactions import in_transaction

##############################################################################
# Local imports.
from .models import LocalFolder


##############################################################################
async def get_local_folders() -> Folders:
    """Gets the local cache of known folders.

    Returns:
        The locally-known `Folders`.
    """
    return Folders(
        Folder(id=folder.folder_id, sort_id=folder.sort_id)
        for folder in await LocalFolder.all()
    )


##############################################################################
async def save_local_folders(folders: Folders) -> Folders:
    """Save the local copy of the known folders.

    Args:
        folders: The known folders.

    Returns:
        The folders.
    """
    async with in_transaction():
        await LocalFolder.all().delete()
        await LocalFolder.bulk_create(
            LocalFolder(folder_id=folder.id, sort_id=folder.sort_id)
            for folder in folders
        )
    return folders


### local_folders.py ends here
