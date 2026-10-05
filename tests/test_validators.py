import pytest
from django.core.exceptions import ValidationError

from blueprint.validators import JSONSchemaValidator


class TestJSONSchemaValidator:
    def test_valid_value_passes(self):
        validator = JSONSchemaValidator(json_schema={"type": "integer"})
        validator(42)

    def test_invalid_value_raises_validation_error(self):
        validator = JSONSchemaValidator(json_schema={"type": "integer"})
        with pytest.raises(ValidationError) as excinfo:
            validator("not an integer")
        assert excinfo.value.code == "invalid"

    def test_message_and_code_overrides(self):
        validator = JSONSchemaValidator(
            json_schema={"type": "integer"},
            message="Nope",
            code="bad_int",
        )
        with pytest.raises(ValidationError) as excinfo:
            validator("x")
        assert excinfo.value.message == "Nope"
        assert excinfo.value.code == "bad_int"

    def test_equality_for_migration_serialization(self):
        schema = {"type": "integer"}
        assert JSONSchemaValidator(json_schema=schema) == JSONSchemaValidator(
            json_schema=schema
        )
        assert JSONSchemaValidator(json_schema=schema) != JSONSchemaValidator(
            json_schema={"type": "string"}
        )

    def test_is_deconstructible(self):
        validator = JSONSchemaValidator(json_schema={"type": "integer"})
        path, args, kwargs = validator.deconstruct()
        assert path == "blueprint.validators.JSONSchemaValidator"
        assert kwargs == {"json_schema": {"type": "integer"}}
