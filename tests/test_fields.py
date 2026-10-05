import types

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

from .models import HashTagged, Link, Post, Tagged
from .sanitizers import passthrough_sanitizer

pytestmark = pytest.mark.django_db


class TestHTMLField:
    def test_is_a_text_field(self):
        field = HTMLField()
        assert isinstance(field, models.TextField)

    def test_script_tags_and_content_are_removed(self):
        post = Post.objects.create(body="<p>Hi</p><script>alert(1)</script>")
        post.refresh_from_db()
        assert post.body == "<p>Hi</p>"

    def test_event_handlers_are_removed(self):
        post = Post.objects.create(body='<p onclick="x()">Hi</p>')
        post.refresh_from_db()
        assert post.body == "<p>Hi</p>"

    def test_javascript_urls_are_removed(self):
        post = Post.objects.create(body='<a href="javascript:alert(1)">x</a>')
        post.refresh_from_db()
        assert "javascript" not in post.body
        assert "<a" in post.body

    def test_safe_content_is_kept(self):
        html = (
            '<h2 class="title">Head</h2>'
            "<p>Some <em>text</em> with a "
            '<a href="https://example.com" title="Docs">link</a>.</p>'
        )
        post = Post.objects.create(body=html)
        post.refresh_from_db()
        assert '<h2 class="title">Head</h2>' in post.body
        assert "<em>text</em>" in post.body
        assert '<a href="https://example.com" title="Docs"' in post.body

    def test_comments_are_stripped(self):
        post = Post.objects.create(body="<p>Hi</p><!-- secret -->")
        post.refresh_from_db()
        assert post.body == "<p>Hi</p>"

    def test_empty_value_is_left_alone(self):
        post = Post.objects.create(body="")
        assert post.body == ""

    def test_non_string_values_are_passed_through(self):
        field = HTMLField(sanitizer=passthrough_sanitizer)
        field.set_attributes_from_name("body")

        instance = types.SimpleNamespace(body=42)
        assert field.pre_save(instance, True) == 42

    def test_field_sanitizer_overrides_the_default(self):
        field = HTMLField(sanitizer=passthrough_sanitizer)
        field.set_attributes_from_name("body")

        instance = types.SimpleNamespace(body='<p onclick="x()">Hi</p>')
        assert field.pre_save(instance, True) == '<p onclick="x()">Hi</p>'

    def test_field_sanitizer_accepts_a_dotted_path(self):
        field = HTMLField(sanitizer="tests.sanitizers.passthrough_sanitizer")
        field.set_attributes_from_name("body")

        instance = types.SimpleNamespace(body='<p onclick="x()">Hi</p>')
        assert field.pre_save(instance, True) == '<p onclick="x()">Hi</p>'

    def test_settings_sanitizer_is_used(self, settings):
        settings.BLUEPRINT = {"HTML_SANITIZER": "tests.sanitizers.upper_sanitizer"}

        field = HTMLField()
        field.set_attributes_from_name("body")

        instance = types.SimpleNamespace(body="<p>hi</p>")
        assert field.pre_save(instance, True) == "<P>HI</P>"

    def test_settings_sanitizer_can_be_a_callable(self, settings):
        settings.BLUEPRINT = {"HTML_SANITIZER": passthrough_sanitizer}

        field = HTMLField()
        field.set_attributes_from_name("body")

        instance = types.SimpleNamespace(body="<p onclick='x()'>Hi</p>")
        assert field.pre_save(instance, True) == "<p onclick='x()'>Hi</p>"

    def test_deconstruct_omits_the_default_sanitizer(self):
        _, _, _, kwargs = HTMLField().deconstruct()
        assert "sanitizer" not in kwargs

    def test_deconstruct_includes_a_custom_sanitizer(self):
        field = HTMLField(sanitizer=passthrough_sanitizer)
        _, _, _, kwargs = field.deconstruct()
        assert kwargs["sanitizer"] is passthrough_sanitizer


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

    def test_custom_validators_are_appended_to_the_schema_validator(self):
        def no_foo(value):
            if value and "foo" in value:
                raise ValidationError("no foo")

        field = FlexField({"type": "object"}, validators=[no_foo])

        from blueprint.validators import JSONSchemaValidator

        assert isinstance(field.validators[0], JSONSchemaValidator)
        assert field.validators[1] is no_foo


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

    def test_validator_messages_are_translated(self):
        from django.utils import translation

        field = URLPathField()

        with translation.override("nl"):
            messages = [str(v.message) for v in field.validators]

        assert messages[0] == (
            "Accepteert alleen letters, cijfers, liggende streepjes, "
            "streepjes en schuine streepjes."
        )
        assert messages[1] == "Opeenvolgende schuine streepjes zijn niet toegestaan."

    def test_root_path_is_kept(self):
        link = Link.objects.create(path="/")
        assert link.path == "/"

    def test_none_value_is_passed_through(self):
        field = URLPathField(null=True)
        field.set_attributes_from_name("path")

        instance = types.SimpleNamespace(path=None)
        assert field.pre_save(instance, True) is None


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

    def test_custom_validators_are_appended_to_the_options_validator(self):
        def always_ok(value):
            return None

        field = MultipleChoiceField(options=[("a", "Alpha")], validators=[always_ok])

        from blueprint.validators import ChoiceOptionsValidator

        assert isinstance(field.validators[0], ChoiceOptionsValidator)
        assert field.validators[1] is always_ok
        with pytest.raises(ValidationError):
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
        tagged = Tagged.objects.create(tags=["Hello", "hello", "#News"])
        tagged.refresh_from_db()
        assert tagged.tags == ["Hello", "hello", "#News"]

    def test_duplicates_are_dropped(self):
        tagged = Tagged.objects.create(tags=["Hello", "Hello ", "hello"])
        tagged.refresh_from_db()
        assert tagged.tags == ["Hello", "hello"]

    def test_empty_tags_are_dropped(self):
        tagged = Tagged.objects.create(tags=["", "   ", "World"])
        tagged.refresh_from_db()
        assert tagged.tags == ["World"]

    def test_non_list_values_are_passed_through(self):
        tagged = Tagged.objects.create(tags={"a": 1})
        tagged.refresh_from_db()
        assert tagged.tags == {"a": 1}


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

    def test_non_list_values_are_passed_through(self):
        tagged = HashTagged.objects.create(tags="Not a list")
        tagged.refresh_from_db()
        assert tagged.tags == "Not a list"
