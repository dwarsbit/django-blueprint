"""
Concrete models used to exercise blueprint's abstract bases.

The blueprint app itself defines no concrete models and has no migrations,
so these models are registered under its app label: Django creates their
tables with run_syncdb, just like it does for any migration-less app.
"""

from django.db import models

from blueprint.fields import TagField, URLPathField
from blueprint.models import (
    ContentModel,
    ManualOrderModel,
    SingletonModel,
    SoftDeletableContentModel,
)


class Article(ContentModel):
    class Meta(ContentModel.Meta):
        app_label = "blueprint"
        db_table = "test_article"

    title = models.CharField(max_length=100)


class Link(ContentModel):
    class Meta(ContentModel.Meta):
        app_label = "blueprint"
        db_table = "test_link"

    path = URLPathField()


class Tagged(ContentModel):
    class Meta(ContentModel.Meta):
        app_label = "blueprint"
        db_table = "test_tagged"

    tags = TagField()


class Section(ManualOrderModel):
    class Meta(ManualOrderModel.Meta):
        app_label = "blueprint"
        db_table = "test_section"

    name = models.CharField(max_length=100)


class Page(SoftDeletableContentModel):
    class Meta(SoftDeletableContentModel.Meta):
        app_label = "blueprint"
        db_table = "test_page"

    title = models.CharField(max_length=100)


class SiteSettings(SingletonModel):
    class Meta(SingletonModel.Meta):
        app_label = "blueprint"
        db_table = "test_site_settings"

    site_name = models.CharField(max_length=100, default="")
