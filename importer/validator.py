"""JSON schema-based validator for Digital Coach process definitions.

This module validates the input JSON structure before it is mapped
and imported into AskDelphi."""

import json
from jsonschema import validate, ValidationError


class ProcessValidator:
    """Validate a process JSON file against a JSON schema."""

    def __init__(self, schema_path: str) -> None:
        self.schema_path = schema_path
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def validate(self, data: dict) -> None:
        """Validate the given data against the loaded schema.

        Raises:
            ValidationError: if the data does not conform to the schema.
        """
        try:
            validate(instance=data, schema=self.schema)
        except ValidationError as exc:
            raise ValidationError(f"Process JSON failed validation: {exc.message}") from exc
