import jsonschema
from django.core.validators import RegexValidator
from django.db import models

from .validators import ChoiceOptionsValidator, JSONSchemaValidator


class HTMLField(models.TextField):
    description = "A field for HTML content."


class FlexField(models.JSONField):
    description = "A JSON field with automatic validation against a schema."

    json_schema = None

    def __init__(self, schema, *args, **kwargs):
        if not schema:
            raise ValueError("The schema parameter is required.")

        try:
            jsonschema.validators.validator_for(schema).check_schema(schema)
        except jsonschema.SchemaError:
            raise ValueError("Not a valid JSON schema.")

        self.json_schema = schema

        kwargs["validators"] = [JSONSchemaValidator(json_schema=self.json_schema)]
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["schema"] = self.json_schema
        return name, path, args, kwargs


class URLPathField(models.CharField):
    description = "A field for a unique URL path. Only accepts letters, numbers, underscores, hyphens and slashes."

    default_validators = [
        RegexValidator(
            "^[a-zA-Z0-9_/-]+$",
            message="Only accepts letters, numbers, underscores, hyphens and slashes.",
        ),
        RegexValidator(
            "//",
            inverse_match=True,
            message="Consecutive slashes are not allowed.",
        ),
    ]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("unique", True)
        kwargs.setdefault("max_length", 200)

        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """
        Make sure paths start with a slash and do not end with one.
        """
        value: str = getattr(model_instance, self.attname, "")

        if not value.startswith("/"):
            value = f"/{value}"

        if value.endswith("/"):
            value = value[:-1]

        setattr(model_instance, self.attname, value)

        return value


class MultipleChoiceField(models.JSONField):
    description = "A field for storing multiple choices as a JSON array."

    def __init__(self, *args, options=None, **kwargs):
        kwargs.setdefault("default", list)
        kwargs.setdefault("blank", True)

        if not options:
            options = []

        self.options = (
            list(options.items()) if isinstance(options, dict) else list(options)
        )

        kwargs.setdefault("validators", [ChoiceOptionsValidator(options=self.options)])

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["options"] = self.options
        return name, path, args, kwargs


class TagField(models.JSONField):
    description = "A field for storing tags as a JSON array."

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", list)
        kwargs.setdefault("blank", True)

        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """
        Normalizes tags: trims surrounding whitespace, strips leading hash
        signs, lowercases, drops empties and removes duplicates.
        """
        value = super().pre_save(model_instance, add)

        if value is None:
            return value

        normalized = []
        for tag in value:
            tag = str(tag).strip().lstrip("#").strip().lower()
            if tag and tag not in normalized:
                normalized.append(tag)

        setattr(model_instance, self.attname, normalized)
        return normalized
