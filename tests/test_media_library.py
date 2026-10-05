import pytest
from django.core.files.base import ContentFile
from django.db import IntegrityError, models

from blueprint.media_library.fields import (
    CropField,
    ManyMediaField,
    MediaField,
)
from blueprint.media_library.models import Folder, Media

pytestmark = pytest.mark.django_db


def make_media(filename="photo.jpg", content=b"image-bytes", **kwargs):
    media = Media(file=ContentFile(content, name=filename), **kwargs)
    media.save()
    return media


class TestFolder:
    def test_str(self):
        folder = Folder.objects.create(name="Holiday")
        assert str(folder) == "Holiday"

    def test_name_must_not_be_empty(self):
        from django.core.exceptions import ValidationError

        folder = Folder(name="")
        with pytest.raises(ValidationError):
            folder.full_clean()

    def test_unique_together_name_parent(self):
        parent = Folder.objects.create(name="Parent")
        Folder.objects.create(name="Child", parent=parent)
        with pytest.raises(IntegrityError):
            Folder.objects.create(name="Child", parent=parent)

    def test_same_name_in_different_parents(self):
        first = Folder.objects.create(name="Parent 1")
        second = Folder.objects.create(name="Parent 2")
        Folder.objects.create(name="Child", parent=first)
        Folder.objects.create(name="Child", parent=second)
        assert Folder.objects.count() == 4


class TestMedia:
    def test_name_is_derived_from_filename(self):
        media = make_media(filename="photo.jpg")
        assert media.name == "photo"

    def test_extension_with_multiple_dots(self):
        media = make_media(filename="archive.tar.gz")
        assert media.name == "archive.tar"

    def test_filename_without_extension(self):
        media = make_media(filename="README")
        assert media.name == "README"

    def test_explicit_name_is_kept(self):
        media = make_media(name="Custom name")
        assert media.name == "Custom name"

    def test_size_is_stored_in_bytes(self):
        media = make_media(content=b"x" * 2500)
        assert media.size == 2500

    def test_defaults(self):
        media = make_media()
        assert media.tags == []
        assert media.crop == []
        assert media.type == "file"
        assert media.folder is None

    def test_type_choices(self):
        media = make_media(type="image")
        assert media.type == "image"

    def test_save_without_file(self):
        media = Media(name="No file")
        media.save()
        media.refresh_from_db()
        assert media.size is None


class TestMediaFields:
    def test_media_field_defaults(self):
        field = MediaField(to=Media)
        assert isinstance(field, models.ForeignKey)
        assert field.blank is True
        assert field.null is True
        assert field.remote_field.related_name == "+"
        assert field.remote_field.on_delete is models.SET_NULL

    def test_media_field_file_type(self):
        assert MediaField(to=Media).file_type is None
        assert MediaField(to=Media, file_type="image").file_type == "image"
        assert MediaField(to=Media, file_type=["image", "video"]).file_type == [
            "image",
            "video",
        ]

    def test_many_media_field_defaults(self):
        field = ManyMediaField(to=Media)
        assert isinstance(field, models.ManyToManyField)
        assert field.blank is True
        assert field.remote_field.related_name == "+"
        assert field.file_type is None

    def test_many_media_field_file_type(self):
        assert ManyMediaField(to=Media, file_type="video").file_type == "video"

    def test_crop_field_defaults(self):
        field = CropField()
        assert field.default is list
        assert field.blank is True
