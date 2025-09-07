from tortoise import fields
from tortoise.models import Model

class Website(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    url = fields.CharField(max_length=100)

    def __str__(self):
        return self.name

class Article(Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255, null=True)
    lastmod = fields.DatetimeField(null=True)
    changefreq = fields.CharField(max_length=50, null=True)
    title = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    content = fields.TextField(null=True)
    headline = fields.CharField(max_length=255, null=True)
    author = fields.CharField(max_length=100, null=True)
    datePublished = fields.DateField(null=True)
    dateModified = fields.DateField(null=True)
    h1 = fields.CharField(max_length=255, null=True)
    h2 = fields.JSONField(null=True)
    word_count = fields.IntField(null=True)
    image = fields.CharField(max_length=255, null=True)
    keywords = fields.JSONField(null=True)
    additional_attributes = fields.JSONField(null=True)

    website: fields.ForeignKeyRelation[Website] = fields.ForeignKeyField(
        "models.Website", related_name="articles", on_delete=fields.CASCADE
    )

    def __str__(self):
        return f"{self.title or self.url}"
