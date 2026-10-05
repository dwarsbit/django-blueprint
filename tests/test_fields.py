import pytest
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from blueprint.fields import (
    FlexField,
    HTMLField,
    HashTagField,
    MultipleChoiceField,
    TagField,
    URLPathField,
)

from .models import HashTagged, Link, Tagged

pytestmark = pytest.mark.django_db


class TestHTMLField:
    def test_is_a_text_field(self):
        field = HTMLField()
        assert isinstance(field, models.TextField)
        assert field.description == "A field for HTML content."


class TestFlexField:
    def test_is_a_json_field(self):
        field = FlexField({"type": "object"})
        assert isinstance(field, models.JSONField)

    def test_schema_is_required(self):
        with pytest.raises(ValueError, match="schema parameter is required"):
            FlexField(None)

    def test_invalid_schema_is_rejected(self):
        with pytest.raises(ValueError, match="Not a valid JSON schema"):
            FlexField({"type": "nonsense"})

    def test_deconstruct_includes_the_schema(self):
        field = FlexField({"type": "object"})
        _, _, _, kwargs = field.deconstruct()
        assert kwargs["schema"] == {"type": "object"}

    def test_valid_value_passes_validation(self):
        schema = {
            "type": "object",
            "properties": {"title": {"type": "string"}},
            "required": ["title"],
        }
        field = FlexField(schema)
        field.validators[0]({"title": "Hello"})

    def test_invalid_value_raises_validation_error(self):
        schema = {"type": "object", "required": ["title"]}
        field = FlexField(schema)
        with pytest.raises(ValidationError):
            field.validators[0]({})


class TestURLPathField:
    def test_defaults(self):
        field = URLPathField()
        assert field.unique is True
        assert field.max_length == 200

    def test_default_validators_are_always_present(self):
        field = URLPathField(validators=[])
        regex_validators = [
            v for v in field.validators if isinstance(v, RegexValidator)
        ]
        assert len(regex_validators) == 2

    def test_custom_validators_are_appended(self):
        extra = RegexValidator("^/custom", message="Must start with /custom.")
        field = URLPathField(validators=[extra])
        assert extra in field.validators
        regex_validators = [
            v for v in field.validators if isinstance(v, RegexValidator)
        ]
        assert len(regex_validators) == 3

    def test_value_without_slashes_is_normalized_on_save(self):
        link = Link.objects.create(path="foo/bar")
        assert link.path == "/foo/bar"

    def test_trailing_slash_is_stripped_on_save(self):
        link = Link.objects.create(path="/foo/bar/")
        assert link.path == "/foo/bar"

    def test_normalized_value_is_persisted(self):
        link = Link.objects.create(path="foo/bar")
        assert Link.objects.get(pk=link.pk).path == "/foo/bar"

    def test_invalid_characters_are_rejected(self):
        link = Link(path="foo bar")
        with pytest.raises(ValidationError):
            link.full_clean()

    def test_consecutive_slashes_are_rejected(self):
        link = Link(path="/foo//bar")
        with pytest.raises(ValidationError):
            link.full_clean()


class TestMultipleChoiceField:
    def test_defaults(self):
        field = MultipleChoiceField()
        assert field.default is list
        assert field.blank is True

    def test_dict_options_are_stored_as_pairs(self):
        field = MultipleChoiceField(options={"a": "Alpha", "b": "Beta"})
        assert field.options == [("a", "Alpha"), ("b", "Beta")]

    def test_list_options_are_kept_as_given(self):
        field = MultipleChoiceField(options=[("a", "Alpha"), ("b", "Beta")])
        assert field.options == [("a", "Alpha"), ("b", "Beta")]

    def test_deconstruct_includes_options(self):
        field = MultipleChoiceField(options=[("a", "Alpha")])
        _, _, _, kwargs = field.deconstruct()
        assert kwargs["options"] == [("a", "Alpha")]

    def test_values_outside_options_are_rejected(self):
        field = MultipleChoiceField(options=[("a", "Alpha"), ("b", "Beta")])
        with pytest.raises(ValidationError):
            field.clean(["a", "c"], None)

    def test_values_within_options_pass(self):
        field = MultipleChoiceField(options=[("a", "Alpha"), ("b", "Beta")])
        field.clean(["a", "b"], None)


class TestTagField:
    def test_defaults_to_an_empty_list(self):
        field = TagField()
        assert field.default is list
        assert field.blank is True

    def test_surrounding_whitespace_is_trimmed(self):
        tagged = Tagged.objects.create(tags=["  Hello  ", "World\t"])
        tagged.refresh_from_db()
        assert tagged.tags == ["Hello", "World"]

    def test_values_are_kept_as_given(self):
        tagged = Tagged.objects.create(tags=["Hello", "hello", "Hello", "#News"])
        tagged.refresh_from_db()
        assert tagged.tags == ["Hello", "hello", "Hello", "#News"]

    def test_empty_tags_are_dropped(self):
        tagged = Tagged.objects.create(tags=["", "   ", "World"])
        tagged.refresh_from_db()
        assert tagged.tags == ["World"]


class TestHashTagField:
    def test_defaults_to_an_empty_list(self):
        field = HashTagField()
        assert field.default is list
        assert field.blank is True

    def test_values_are_normalized(self):
        tagged = HashTagged.objects.create(
            tags=["#News", "  New York ", "news", "#Events"]
        )
        tagged.refresh_from_db()
        assert tagged.tags == ["news", "newyork", "events"]

    def test_duplicates_collapse(self):
        tagged = HashTagged.objects.create(tags=["#News", "news", " NEWS "])
        tagged.refresh_from_db()
        assert tagged.tags == ["news"]

    def test_whitespace_and_hash_only_values_are_dropped(self):
        tagged = HashTagged.objects.create(tags=["#", "   ", "#  #"])
        tagged.refresh_from_db()
        assert tagged.tags == []
