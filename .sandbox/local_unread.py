from oldas import Folder

from oldnews.data import initialise_database
from oldnews.data.local_articles import get_local_unread_articles


def main() -> None:
    initialise_database()
    for x in get_local_unread_articles(Folder("user/-/label/Python", "")):
        print(f"{x.categories} - {x.title}")


if __name__ == "__main__":
    main()
