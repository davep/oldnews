"""Code relating to persisting the known list of folders."""

##############################################################################
# OldAS imports.
from oldas import Folder, Folders

##############################################################################
# TypeDAL imports.
from typedal import TypedField, TypedTable


##############################################################################
class LocalFolders(TypedTable):
    """The local copy of the folders."""

    folder_id: TypedField[str]
    """The ID of the folder."""
    sort_id: TypedField[str]
    """The sort ID of the folder."""


##############################################################################
def get_local_folders() -> Folders:
    """Gets the local cache of known folders.

    Returns:
        The locally-known `Folders`.
    """
    return Folders(
        Folder({}, folder.folder_id, folder.sort_id)
        for folder in LocalFolders.select(LocalFolders.ALL)
    )


##############################################################################
def save_local_folders(folders: Folders) -> Folders:
    """Save the local copy of the known folders.

    Args:
        folders: The known folders.

    Returns:
        The folders.
    """
    assert LocalFolders._db is not None
    LocalFolders.truncate()
    LocalFolders.bulk_insert(
        [{"folder_id": folder.id, "sort_id": folder.sort_id} for folder in folders]
    )
    LocalFolders._db.commit()
    return folders


### local_folders.py ends here
