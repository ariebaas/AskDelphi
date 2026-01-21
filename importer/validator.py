"""JSON schema-gebaseerde validator voor Digital Coach proces definities.

Deze module valideert de input JSON structuur voordat deze wordt gemapt
en geïmporteerd in AskDelphi."""

import json
from jsonschema import validate, ValidationError


class ProcessValidator:
    """Valideer een proces JSON bestand tegen een JSON schema."""

    def __init__(self, schema_path: str) -> None:
        self.schema_path = schema_path
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

    def validate(self, data: dict) -> None:
        """Valideer de gegeven data tegen het geladen schema.

        Raises:
            ValidationError: indien de data niet conform het schema is.
        """
        try:
            validate(instance=data, schema=self.schema)
        except ValidationError as exc:
            raise ValidationError(f"Proces JSON validatie mislukt: {exc.message}") from exc
