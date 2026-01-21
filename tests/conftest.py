"""Pytest configuratie en fixtures voor test suite."""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

cache_file = Path(".askdelphi_tokens.json")
if cache_file.exists():
    cache_file.unlink()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ["ASKDELPHI_AUTH_MODE"] = "traditional"

import pytest

# Setup logging to file
log_dir = Path(__file__).parent.parent / "log" / "test"
log_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = log_dir / f"pytest_{timestamp}.log"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)


@pytest.fixture(autouse=True)
def cleanup_cache():
    """Schoon cache tokens op voor elke test."""
    cache_file = Path(".askdelphi_tokens.json")
    if cache_file.exists():
        cache_file.unlink()
    yield
    if cache_file.exists():
        cache_file.unlink()
