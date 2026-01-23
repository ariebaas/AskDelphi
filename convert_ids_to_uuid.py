#!/usr/bin/env python3
"""Convert string IDs in process JSON files to UUID format.

This script converts non-UUID string IDs to valid UUIDs using a deterministic
mapping (same input always produces same UUID). This ensures consistency across
multiple runs.

Usage:
    python convert_ids_to_uuid.py [input_file] [output_file]
    
Example:
    python convert_ids_to_uuid.py procesbeschrijving/process_onboard_account.json procesbeschrijving/process_onboard_account_converted.json
"""

import json
import uuid
import sys
import io
from pathlib import Path
from typing import Any, Dict

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Deterministic UUID namespace for converting strings to UUIDs
UUID_NAMESPACE = uuid.NAMESPACE_DNS

def string_to_uuid(string_id: str) -> str:
    """Convert a string ID to a deterministic UUID format.
    
    Uses UUID v5 (SHA-1 based) to ensure the same input always produces
    the same UUID. This is deterministic and reversible.
    """
    # Check if already a valid UUID
    try:
        uuid.UUID(string_id)
        return string_id  # Already a UUID
    except ValueError:
        pass
    
    # Convert string to UUID v5
    generated_uuid = uuid.uuid5(UUID_NAMESPACE, string_id)
    return str(generated_uuid)

def convert_ids_in_dict(obj: Any, id_mapping: Dict[str, str]) -> Any:
    """Recursively convert IDs in a dictionary/list structure."""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # Convert all ID-related fields to UUID
            if key in ("id", "topicId", "parentId", "parent", "parentTopicId") and isinstance(value, str):
                # Convert ID to UUID
                if value not in id_mapping:
                    id_mapping[value] = string_to_uuid(value)
                result[key] = id_mapping[value]
            elif isinstance(value, (dict, list)):
                result[key] = convert_ids_in_dict(value, id_mapping)
            else:
                result[key] = value
        return result
    elif isinstance(obj, list):
        return [convert_ids_in_dict(item, id_mapping) for item in obj]
    else:
        return obj

def convert_process_file(input_file: str, output_file: str) -> None:
    """Convert IDs in a process JSON file to UUID format."""
    print(f"Reading: {input_file}")
    
    # Try utf-8-sig first (handles BOM), then fall back to utf-8
    try:
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except (UnicodeDecodeError, json.JSONDecodeError):
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    print("Converting IDs to UUID format...")
    id_mapping = {}
    converted_data = convert_ids_in_dict(data, id_mapping)
    
    print(f"Converted {len(id_mapping)} IDs:")
    for original, converted in sorted(id_mapping.items()):
        if original != converted:
            print(f"  {original} → {converted}")
    
    print(f"Writing: {output_file}")
    with open(output_file, 'w', encoding='utf-8-sig') as f:
        json.dump(converted_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Conversion complete")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('--help', '-h', '?'):
        print(__doc__)
        sys.exit(0 if len(sys.argv) > 1 else 1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_converted.json')
    
    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    try:
        convert_process_file(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
