from oldas import State

from oldnews.data import initialise_database
from oldnews.data.local_articles import LocalArticleCategory


def main() -> None:
    initialise_database()
    for x in LocalArticleCategory.join().where(category=State.FRESH).collect():
        print(f"{x.category} - {x.article.title}")


if __name__ == "__main__":
    main()
