"""Defines the models for the local article data."""

##############################################################################
# OldAS imports.
from oldas import State

##############################################################################
# Tortoise imports.
from tortoise import fields
from tortoise.models import Model


##############################################################################
class LocalArticle(Model):
    """A local copy of an article."""

    article_id = fields.CharField(max_length=255, pk=True)
    """The ID of the article."""
    title = fields.TextField()
    """The title of the article."""
    published = fields.DatetimeField()
    """The time when the article was published."""
    updated = fields.DatetimeField()
    """The time when the article was updated."""
    author = fields.CharField(max_length=255)
    """The author of the article."""
    summary_direction = fields.CharField(max_length=10)
    """The direction for the text in the summary."""
    summary_content = fields.TextField()
    """The content of the summary."""
    origin_stream_id = fields.TextField()
    """The stream ID for the article's origin."""
    origin_title = fields.TextField()
    """The title of the origin of the article."""
    origin_html_url = fields.TextField()
    """The URL of the HTML of the origin of the article."""

    async def add_category(self, category: str | State) -> None:
        """Add a given category to the local article.

        Args:
            category: The category to add.
        """
        await LocalArticleCategory.get_or_create(article=self, category=str(category))

    async def remove_category(self, category: str | State) -> None:
        """Remove a given category from the local article.

        Args:
            category: The category to add.
        """
        await LocalArticleCategory.filter(article=self, category=str(category)).delete()


##############################################################################
class LocalArticleCategory(Model):
    """A local copy of the categories associated with an article."""

    article: fields.ForeignKeyRelation[LocalArticle] = fields.ForeignKeyField(
        "models.LocalArticle", related_name="categories", on_delete=fields.CASCADE
    )
    """The article that this category belongs to."""
    category = fields.CharField(max_length=255)
    """The category."""


##############################################################################
class LocalArticleAlternate(Model):
    """A local copy of the alternate URLs associated with an article."""

    article: fields.ForeignKeyRelation[LocalArticle] = fields.ForeignKeyField(
        "models.LocalArticle", related_name="alternates", on_delete=fields.CASCADE
    )
    """The article that this alternate belongs to."""
    href = fields.TextField()
    """The URL of the alternate."""
    mime_type = fields.CharField(max_length=100)
    """The MIME type of the alternate."""


### local_article.py ends here
