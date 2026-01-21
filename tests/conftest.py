"""Pytest configuration and fixtures for test suite."""

import os
import sys
from pathlib import Path

# Clean up cached tokens before any tests run
cache_file = Path(".askdelphi_tokens.json")
if cache_file.exists():
    cache_file.unlink()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Override USE_AUTH_CACHE to False for all tests
os.environ["ASKDELPHI_AUTH_MODE"] = "traditional"

import pytest


@pytest.fixture(autouse=True)
def cleanup_cache():
    """Clean up cache tokens before each test."""
    cache_file = Path(".askdelphi_tokens.json")
    if cache_file.exists():
        cache_file.unlink()
    yield
    # Clean up after test too
    if cache_file.exists():
        cache_file.unlink()
