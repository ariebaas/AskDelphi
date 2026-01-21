"""Environment configuration loader for the Digitalecoach importer.

This module loads all relevant settings from a .env file using python-dotenv.
It centralizes configuration for AskDelphi connectivity and debug behavior."""

import os
from dotenv import load_dotenv

load_dotenv()


def get_env(name: str, default=None):
    """Return environment variable value or default if not set."""
    value = os.getenv(name)
    return value if value is not None else default


DEBUG = get_env("DEBUG", "false").lower() == "true"
SKIP_CHECKOUT_CHECKIN = get_env("SKIP_CHECKOUT_CHECKIN", "true").lower() == "true"

# Authentication Mode Selection
# "cache" = Use token caching with portal code (Daan's mechanism)
# "traditional" = Use API key with session tokens (default)
ASKDELPHI_AUTH_MODE = get_env("ASKDELPHI_AUTH_MODE", "traditional").lower()

# Token caching (only used when ASKDELPHI_AUTH_MODE="cache")
USE_AUTH_CACHE = ASKDELPHI_AUTH_MODE == "cache"

ASKDELPHI_BASE_URL = get_env("ASKDELPHI_BASE_URL")
ASKDELPHI_API_KEY = get_env("ASKDELPHI_API_KEY")

ASKDELPHI_TENANT = get_env("ASKDELPHI_TENANT")
ASKDELPHI_NT_ACCOUNT = get_env("ASKDELPHI_NT_ACCOUNT")
ASKDELPHI_ACL = [x.strip() for x in get_env("ASKDELPHI_ACL", "").split(",") if x.strip()]
ASKDELPHI_PROJECT_ID = get_env("ASKDELPHI_PROJECT_ID")

# CMS URL Configuration (for token caching mode)
ASKDELPHI_CMS_URL = get_env("ASKDELPHI_CMS_URL")
ASKDELPHI_PORTAL_CODE = get_env("ASKDELPHI_PORTAL_CODE")
