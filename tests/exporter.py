"""Exporter CLI for AskDelphi Digital Coach.

This tool exports all content from AskDelphi (or the mock server) as JSON.
The output conforms to the AskDelphi export format.

Usage:
    python exporter.py --output path/to/export.json
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from askdelphi.session import AskDelphiSession
from config import env

# Configure logging with both file and console output
log_dir = os.path.dirname(__file__)
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
log_format = "[EXPORT] %(asctime)s %(levelname)s: %(message)s"

# File handler with flush
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


def export_content(output_path: str) -> None:
    """Export all content from AskDelphi as JSON.
    
    Args:
        output_path: Path where to save the export JSON file
    """
    logger.info("=" * 60)
    logger.info("EXPORTING CONTENT FROM ASKDELPHI")
    logger.info("=" * 60)
    
    # Create session
    logger.info("Creating AskDelphiSession...")
    session = AskDelphiSession(
        base_url=env.ASKDELPHI_BASE_URL,
        api_key=env.ASKDELPHI_API_KEY,
        tenant=env.ASKDELPHI_TENANT,
        nt_account=env.ASKDELPHI_NT_ACCOUNT,
        acl=env.ASKDELPHI_ACL,
        project_id=env.ASKDELPHI_PROJECT_ID,
    )
    logger.info("✓ AskDelphiSession created")
    
    # Call export endpoint
    logger.info("Fetching export from AskDelphi...")
    try:
        export_data = session.get("/export")
        logger.info("✓ Export fetched successfully")
    except Exception as e:
        logger.error(f"✗ Failed to fetch export: {e}")
        raise
    
    # Save to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving export to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Export saved to {output_file}")
    
    # Print summary
    if isinstance(export_data, dict):
        metadata = export_data.get("_metadata", {})
        topic_count = metadata.get("topic_count", 0)
        logger.info("=" * 60)
        logger.info(f"EXPORT SUMMARY:")
        logger.info(f"  Topics exported: {topic_count}")
        logger.info(f"  Exported at: {metadata.get('exported_at')}")
        logger.info(f"  Source: {metadata.get('source')}")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export content from AskDelphi as JSON"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        help="Output file path (default: export_YYYYMMDD_HHMMSS.json)"
    )
    
    args = parser.parse_args()
    
    try:
        export_content(args.output)
        logger.info("✓ Export completed successfully!")
    except Exception as e:
        logger.error(f"✗ Export failed: {e}")
        raise


if __name__ == "__main__":
    main()
