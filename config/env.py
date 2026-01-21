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

ASKDELPHI_BASE_URL = get_env("ASKDELPHI_BASE_URL")
ASKDELPHI_API_KEY = get_env("ASKDELPHI_API_KEY")

ASKDELPHI_TENANT = get_env("ASKDELPHI_TENANT")
ASKDELPHI_NT_ACCOUNT = get_env("ASKDELPHI_NT_ACCOUNT")
ASKDELPHI_ACL = [x.strip() for x in get_env("ASKDELPHI_ACL", "").split(",") if x.strip()]
ASKDELPHI_PROJECT_ID = get_env("ASKDELPHI_PROJECT_ID")
