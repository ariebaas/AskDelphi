"""Volledige workflow: Importeer proces en exporteer vervolgens alle content.

Dit script:
1. Importeert een proces uit JSON
2. Exporteert alle content naar een JSON bestand

Gebruik:
    python run_import_and_export.py --input ../procesbeschrijving/process_onboard_account.json --output export_with_content.json
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
import requests

cache_file = Path(".askdelphi_tokens.json")
if cache_file.exists():
    cache_file.unlink()

os.environ["ASKDELPHI_AUTH_MODE"] = "traditional"

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api_client.session import AskDelphiSession
from config import env
from importer.validator import ProcessValidator
from importer.mapper import DigitalCoachMapper
from importer.importer import DigitalCoachImporter

log_dir = os.path.dirname(__file__)
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"import_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
log_format = "[IMPORT_EXPORT] %(asctime)s %(levelname)s: %(message)s"


class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()


file_handler = FlushFileHandler(log_file, mode="w", encoding="utf-8")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
formatter.default_msec_format = "%s.%03d"
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S'))

# Root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def import_and_export(input_file: str, schema_file: str, output_file: str) -> None:
    """Import a process and then export all content.
    
    Args:
        input_file: Path to process JSON file
        schema_file: Path to JSON schema file
        output_file: Path where to save the export JSON file
    """
    logger.info("=" * 70)
    logger.info("IMPORT AND EXPORT WORKFLOW")
    logger.info("=" * 70)
    
    # Convert relative paths to absolute paths from project root
    project_root = os.path.dirname(os.path.dirname(__file__))
    input_file = os.path.normpath(os.path.join(project_root, input_file)) if not os.path.isabs(input_file) else input_file
    schema_file = os.path.normpath(os.path.join(project_root, schema_file)) if not os.path.isabs(schema_file) else schema_file
    output_file = os.path.normpath(os.path.join(log_dir, output_file)) if not os.path.isabs(output_file) else output_file
    
    # Reset mockserver state
    logger.info("\n[0/4] Resetting mockserver state...")
    try:
        requests.post(f"{env.ASKDELPHI_BASE_URL}/reset")
        logger.info("✓ Mockserver reset complete")
    except Exception as e:
        logger.warning(f"⚠ Could not reset mockserver (may not be running): {e}")
    
    # Step 1: Load and validate input
    logger.info("\n[1/4] Loading and validating input process...")
    with open(input_file, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    logger.info(f"✓ Loaded: {input_file}")
    
    if schema_file and os.path.exists(schema_file):
        validator = ProcessValidator(schema_file)
        validator.validate(data)
        logger.info(f"✓ Validated against schema: {schema_file}")
    else:
        logger.info(f"⚠ Schema file not found, skipping validation: {schema_file}")
    
    # Step 2: Map to topic tree
    logger.info("\n[2/4] Mapping process to topic tree...")
    mapper = DigitalCoachMapper()
    root_topics = mapper.map_process(data["process"])
    logger.info(f"✓ Mapped {len(root_topics)} root topic(s)")
    
    # Step 3: Import to AskDelphi
    logger.info("\n[3/4] Importing topics to AskDelphi...")
    session = AskDelphiSession(
        base_url=env.ASKDELPHI_BASE_URL,
        api_key=env.ASKDELPHI_API_KEY,
        tenant=env.ASKDELPHI_TENANT,
        nt_account=env.ASKDELPHI_NT_ACCOUNT,
        acl=env.ASKDELPHI_ACL,
        project_id=env.ASKDELPHI_PROJECT_ID,
        use_auth_cache=env.USE_AUTH_CACHE,
    )
    
    importer = DigitalCoachImporter(session)
    importer.import_topics(root_topics)
    logger.info("✓ Import completed successfully")
    
    # Step 4: Export all content
    logger.info("\n[4/4] Exporting all content...")
    try:
        export_data = session.get("/export")
        logger.info("✓ Export fetched from AskDelphi")
    except Exception as e:
        logger.error(f"✗ Failed to fetch export: {e}")
        raise
    
    # Save export to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Export saved to: {output_path}")
    
    # Print summary
    if isinstance(export_data, dict):
        metadata = export_data.get("_metadata", {})
        topics = export_data.get("topics", {})
        topic_count = metadata.get("topic_count", 0)
        
        logger.info("\n" + "=" * 70)
        logger.info("WORKFLOW COMPLETED SUCCESSFULLY!")
        logger.info("=" * 70)
        logger.info(f"Input process: {input_file}")
        logger.info(f"Topics imported: {len(root_topics)}")
        logger.info(f"Topics in export: {topic_count}")
        logger.info(f"Export file: {output_path}")
        logger.info("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import a process and export all content"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to process JSON file"
    )
    parser.add_argument(
        "--schema",
        type=str,
        required=True,
        help="Path to JSON schema file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=f"export_with_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        help="Output file path (default: export_with_content_YYYYMMDD_HHMMSS.json)"
    )
    
    args = parser.parse_args()
    
    try:
        import_and_export(args.input, args.schema, args.output)
    except Exception as e:
        logger.error(f"✗ Workflow failed: {e}")
        raise


if __name__ == "__main__":
    main()
