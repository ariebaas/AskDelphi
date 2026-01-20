"""Entry point for the Digitalecoach reference importer.

This script:
- Loads configuration from .env
- Validates the input JSON against a schema
- Maps the process into a topic tree
- Uses AskDelphiSession to import everything into AskDelphi (or mock)
"""

import json
import argparse

from askdelphi.session import AskDelphiSession
from config import env
from importer.validator import ProcessValidator
from importer.mapper import DigitalCoachMapper
from importer.importer import DigitalCoachImporter


def run(input_file: str, schema_file: str) -> None:
    """Run the full import pipeline for a given process JSON file."""
    with open(input_file, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    validator = ProcessValidator(schema_file)
    validator.validate(data)

    mapper = DigitalCoachMapper()
    root_topics = mapper.map_process(data["process"])

    session = AskDelphiSession(
        base_url=env.ASKDELPHI_BASE_URL,
        api_key=env.ASKDELPHI_API_KEY,
        tenant=env.ASKDELPHI_TENANT,
        nt_account=env.ASKDELPHI_NT_ACCOUNT,
        acl=env.ASKDELPHI_ACL,
        project_id=env.ASKDELPHI_PROJECT_ID,
    )

    importer = DigitalCoachImporter(session)
    importer.import_topics(root_topics)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Digitalecoach reference importer")
    parser.add_argument("--input", required=True, help="Path to process JSON file")
    parser.add_argument("--schema", required=True, help="Path to JSON schema file")
    args = parser.parse_args()

    run(args.input, args.schema)
