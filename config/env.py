"""Omgevingsconfiguratie loader voor de Digitalecoach importer.

Deze module laadt alle relevante instellingen uit een .env bestand met behulp van python-dotenv.
Het centraliseert de configuratie voor AskDelphi connectiviteit."""

import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def get_env(name: str, default=None):
    """Retourneer omgevingsvariabele waarde of standaard indien niet ingesteld."""
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
ASKDELPHI_AUTH_MODE = get_env("ASKDELPHI_AUTH_MODE", "traditional").lower()
USE_AUTH_CACHE = get_env("USE_AUTH_CACHE", "false").lower() == "true"
