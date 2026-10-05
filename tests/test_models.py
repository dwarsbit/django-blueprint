import uuid

import pytest
from django.contrib.auth import get_user_model

from .models import Article, Page, Section, SiteSettings

pytestmark = pytest.mark.django_db


class TestContentModel:
    def test_uuid_primary_key(self):
        article = Article.objects.create(title="Hello")
        assert isinstance(article.pk, uuid.UUID)

    def test_new_uuid_per_instance(self):
        first = Article.objects.create(title="First")
        second = Article.objects.create(title="Second")
        assert first.pk != second.pk

    def test_timestamps_are_set_on_create(self):
        article = Article.objects.create(title="Hello")
        assert article.created_at is not None
        assert article.modified_at is not None

    def test_modified_at_changes_on_save(self):
        article = Article.objects.create(title="Hello")
        before = article.modified_at
        article.save()
        article.refresh_from_db()
        assert article.modified_at > before

    def test_latest_by_created_at(self):
        Article.objects.create(title="First")
        latest = Article.objects.create(title="Second")
        assert Article.objects.latest() == latest

    def test_edited_by_is_null_by_default(self):
        article = Article.objects.create(title="Hello")
        assert article.edited_by is None

    def test_edited_by_related_name(self):
        user = get_user_model().objects.create(username="editor")
        article = Article.objects.create(title="Hello", edited_by=user)
        assert list(user.blueprint_article_edited.all()) == [article]


class TestManualOrderModel:
    def test_default_order_key(self):
        section = Section.objects.create(name="One")
        assert section.order_key == 0

    def test_ordering_by_order_key(self):
        Section.objects.create(name="One", order_key=2)
        Section.objects.create(name="Two", order_key=1)
        assert list(Section.objects.values_list("name", flat=True)) == ["Two", "One"]


class TestSoftDeletableModel:
    def test_soft_delete_sets_removed_at(self):
        page = Page.objects.create(title="Hello")
        page.delete()
        page.refresh_from_db()
        assert page.removed_at is not None

    def test_soft_delete_keeps_the_row(self):
        page = Page.objects.create(title="Hello")
        page.delete()
        assert Page.objects.filter(pk=page.pk).exists()

    def test_is_removed_property(self):
        page = Page.objects.create(title="Hello")
        assert page.is_removed is False
        page.delete()
        assert page.is_removed is True

    def test_hard_delete(self):
        page = Page.objects.create(title="Hello")
        page.delete(soft=False)
        assert not Page.objects.filter(pk=page.pk).exists()

    def test_available_objects_excludes_removed(self):
        kept = Page.objects.create(title="Kept")
        removed = Page.objects.create(title="Removed")
        removed.delete()
        assert list(Page.available_objects.all()) == [kept]

    def test_objects_includes_removed(self):
        kept = Page.objects.create(title="Kept")
        removed = Page.objects.create(title="Removed")
        removed.delete()
        assert set(Page.objects.all()) == {kept, removed}


class TestSingletonModel:
    def test_get_returns_none_when_table_is_empty(self):
        assert SiteSettings.objects.get() is None

    def test_get_returns_the_single_instance(self):
        settings = SiteSettings.objects.create(site_name="My site")
        assert SiteSettings.objects.get() == settings

    def test_create_creates_first_instance(self):
        SiteSettings.objects.create(site_name="My site")
        assert SiteSettings.objects.count() == 1

    def test_create_updates_existing_instance(self):
        SiteSettings.objects.create(site_name="First")
        settings = SiteSettings.objects.create(site_name="Second")
        assert SiteSettings.objects.count() == 1
        assert settings.site_name == "Second"

    def test_database_allows_only_one_row(self):
        from django.db import IntegrityError

        SiteSettings.objects.create(site_name="First")
        with pytest.raises(IntegrityError):
            SiteSettings(site_name="Second").save()


@pytest.mark.django_db
def test_reorder_normalizes_order_keys():
    Section.objects.create(name="One", order_key=7)
    Section.objects.create(name="Two", order_key=3)
    Section.objects.create(name="Three", order_key=5)

    section = Section.objects.first()
    section.reorder()

    assert list(
        Section.objects.order_by("order_key").values_list("name", "order_key")
    ) == [
        ("Two", 1),
        ("Three", 2),
        ("One", 3),
    ]


@pytest.mark.xfail(reason="Phase 0: queryset deletes bypass soft deletion")
@pytest.mark.django_db
def test_queryset_delete_is_soft():
    page = Page.objects.create(title="Hello")
    Page.objects.all().delete()
    assert Page.objects.filter(pk=page.pk).exists()
