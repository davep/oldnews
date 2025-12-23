"""Code relating to persisting the known list of folders."""

##############################################################################
# OldAS imports.
from oldas import Folder, Folders

##############################################################################
# TypeDAL imports.
from typedal import TypedTable


##############################################################################
class LocalFolder(TypedTable):
    """A local copy of a folder."""

    folder_id: str
    """The ID of the folder."""
    sort_id: str
    """The sort ID of the folder."""


##############################################################################
def get_local_folders() -> Folders:
    """Gets the local cache of known folders.

    Returns:
        The locally-known `Folders`.
    """
    return Folders(
        Folder(id=folder.folder_id, sort_id=folder.sort_id)
        for folder in LocalFolder.select(LocalFolder.ALL)
    )


##############################################################################
def save_local_folders(folders: Folders) -> Folders:
    """Save the local copy of the known folders.

    Args:
        folders: The known folders.

    Returns:
        The folders.
    """
    assert LocalFolder._db is not None
    LocalFolder.truncate()
    LocalFolder.bulk_insert(
        [{"folder_id": folder.id, "sort_id": folder.sort_id} for folder in folders]
    )
    LocalFolder._db.commit()
    return folders


### local_folders.py ends here
