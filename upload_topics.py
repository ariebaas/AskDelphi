#!/usr/bin/env python3
"""
Digital Coach Topic Upload Script

Uploads topics from a JSON file to AskDelphi API, following the working
ask-delphi-api pattern.

Usage:
    python upload_topics.py uploadtest.json --original testempty.json
    python upload_topics.py uploadtest.json --dry-run
"""

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.api_client.session import AskDelphiSession
from src.config.env import DEBUG


def load_json(file_path: str) -> Dict[str, Any]:
    """Load and validate a JSON file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Basic validation
    if "topics" not in data:
        raise ValueError(f"Invalid format: missing 'topics' in {file_path}")

    return data


def detect_new_topics(original: Dict[str, Any], modified: Dict[str, Any]) -> List[str]:
    """Detect new topics in modified version."""
    original_topics = original.get("topics", {})
    modified_topics = modified.get("topics", {})
    
    new_topics = []
    for topic_id in modified_topics:
        if topic_id not in original_topics:
            new_topics.append(topic_id)
    
    return new_topics


def upload_topics(
    input_file: str,
    original_file: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
    rate_limit_ms: int = 100,
    verbose: bool = False
) -> None:
    """
    Upload topics from a JSON file to AskDelphi API.

    Args:
        input_file: JSON file with topics to upload
        original_file: Original JSON file for comparison
        dry_run: Only show what would change, don't upload
        force: Skip confirmation prompt
        rate_limit_ms: Delay between API calls
        verbose: Enable verbose logging
    """
    print("\n" + "=" * 60)
    print("DIGITAL COACH TOPIC UPLOAD")
    print("=" * 60 + "\n")

    # Load modified file
    print(f"Loading modified file: {input_file}")
    modified_data = load_json(input_file)
    print(f"  Topics in file: {len(modified_data.get('topics', {}))}")

    # Initialize client
    print("\nInitializing client...")
    session = AskDelphiSession()
    print("Client initialized!")

    # Load or use empty original
    if original_file:
        print(f"\nLoading original file: {original_file}")
        original_data = load_json(original_file)
    else:
        print("\nNo original file provided. Using empty topics.")
        original_data = {"topics": {}}

    print(f"  Topics in original: {len(original_data.get('topics', {}))}")

    # Detect new topics
    print("\nDetecting new topics...")
    new_topics = detect_new_topics(original_data, modified_data)
    print(f"  New topics: {len(new_topics)}")

    if not new_topics:
        print("\nNo new topics to upload.")
        return

    # Print summary
    print("\n" + "-" * 60)
    print(f"SUMMARY: {len(new_topics)} new topic(s) to create")
    print("=" * 60 + "\n")

    # Dry run mode
    if dry_run:
        print("DRY RUN MODE - No changes will be made.\n")
        topics = modified_data.get("topics", {})
        for topic_id in new_topics:
            topic_data = topics[topic_id]
            print(f"  + {topic_data.get('title', 'Untitled')}")
            print(f"    ID: {topic_id}")
            print(f"    Type ID: {topic_data.get('topic_type_id', 'N/A')}")
        return

    # Confirmation
    if not force:
        response = input(f"Create {len(new_topics)} topic(s)? [y/N]: ").strip().lower()
        if response != 'y':
            print("Upload cancelled.")
            return

    # Process new topics
    print(f"\nCreating {len(new_topics)} new topic(s)...\n")
    topics = modified_data.get("topics", {})
    created_count = 0
    error_count = 0

    for topic_id in new_topics:
        topic_data = topics[topic_id]
        title = topic_data.get("title", "Untitled")
        topic_type_id = topic_data.get("topic_type_id")

        if not topic_type_id:
            print(f"  ! Skipping '{title}': missing topic_type_id")
            error_count += 1
            continue

        try:
            # Create topic using minimal payload (matching working ask-delphi-api)
            payload = {
                "topicId": str(uuid.uuid4()),
                "topicTitle": title,
                "topicTypeId": topic_type_id,
                "copyParentTags": False,
            }

            if DEBUG:
                print(f"  [DEBUG] Creating topic with payload: {json.dumps(payload, indent=2)}")

            result = session.post(
                "v4/tenant/{tenantId}/project/{projectId}/acl/{aclEntryId}/topic",
                json=payload
            )

            created_count += 1
            print(f"  ✓ Created: {title}")
            if DEBUG:
                print(f"    Response: {json.dumps(result, indent=2)}")

        except Exception as e:
            error_count += 1
            print(f"  ✗ Error creating '{title}': {str(e)}")
            if DEBUG:
                import traceback
                print(f"    Traceback: {traceback.format_exc()}")

        time.sleep(rate_limit_ms / 1000)

    # Print final report
    print("\n" + "=" * 60)
    print("UPLOAD COMPLETE")
    print("=" * 60)
    print(f"  Created: {created_count}")
    print(f"  Errors: {error_count}")
    print("=" * 60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Upload topics from JSON file to AskDelphi API"
    )
    parser.add_argument(
        "input_file",
        help="JSON file with topics to upload"
    )
    parser.add_argument(
        "--original",
        help="Original JSON file for comparison (default: empty)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would change, don't upload"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt"
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=100,
        help="Delay between API calls in milliseconds (default: 100)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    try:
        upload_topics(
            input_file=args.input_file,
            original_file=args.original,
            dry_run=args.dry_run,
            force=args.force,
            rate_limit_ms=args.rate_limit,
            verbose=args.verbose
        )
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
