"""Pytest configuratie en fixtures voor test suite."""

import os
import sys
from pathlib import Path

cache_file = Path(".askdelphi_tokens.json")
if cache_file.exists():
    cache_file.unlink()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

os.environ["ASKDELPHI_AUTH_MODE"] = "traditional"

import pytest


@pytest.fixture(autouse=True)
def cleanup_cache():
    """Schoon cache tokens op voor elke test."""
    cache_file = Path(".askdelphi_tokens.json")
    if cache_file.exists():
        cache_file.unlink()
    yield
    if cache_file.exists():
        cache_file.unlink()
