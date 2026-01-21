"""Authenticatie module met URL parsing en token caching.

Deze module biedt:
- CMS URL parsing om tenant, project en ACL IDs uit te halen
- Token caching en persistentie
- Automatische token vernieuwing voor expiry
- JWT expiry parsing
"""

import json
import os
import re
import time
import logging
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

# Constants
REQUEST_TIMEOUT = 30
TOKEN_EXPIRY_BUFFER = 300
DEFAULT_TOKEN_EXPIRY = 3600
JWT_PREFIX = "eyJ"
RESPONSE_TEXT_LIMIT = 1000
PORTAL_SERVER = "https://portal.askdelphi.com"
API_SERVER = "https://edit.api.askdelphi.com"


def log_request(method: str, url: str, headers: dict) -> None:
    """Log HTTP verzoek details."""
    logger.debug(f"Verzoek: {method} {url}")
    logger.debug(f"Headers: {headers}")


def log_response(response: requests.Response) -> None:
    """Log HTTP response details."""
    try:
        logger.debug(f"Response Status: {response.status_code}")
        logger.debug(f"Response Headers: {dict(response.headers)}")
        logger.debug(f"Response Body (eerste 500 chars): {response.text[:500]}")
    except Exception as e:
        logger.debug(f"Kon response details niet loggen: {e}")


def _parse_json_response(response: requests.Response) -> dict:
    """Parse JSON response with fallback encoding strategies.
    
    Tries multiple approaches to parse JSON:
    1. Standard response.json()
    2. Manual UTF-8 decode
    3. Latin-1 decode (accepts any byte)
    
    Args:
        response: HTTP response object
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        Exception: If all parsing attempts fail
    """
    try:
        data = response.json()
        logger.debug(f"Parsed JSON response: {json.dumps(data, indent=2)}")
        return data
    except (ValueError, UnicodeDecodeError) as e:
        logger.warning(f"Standard JSON parsing failed: {e}")

    try:
        text = response.content.decode('utf-8')
        data = json.loads(text)
        logger.debug(f"Parsed JSON via manual utf-8 decode: {json.dumps(data, indent=2)}")
        return data
    except (UnicodeDecodeError, json.JSONDecodeError) as e2:
        logger.warning(f"Manual utf-8 decode failed: {e2}")

    try:
        text = response.content.decode('latin-1')
        data = json.loads(text)
        logger.debug(f"Parsed JSON via latin-1 decode: {json.dumps(data, indent=2)}")
        return data
    except json.JSONDecodeError as e3:
        logger.error(f"All JSON parsing attempts failed!")
        logger.error(f" Original error: {e}")
        logger.error(f" UTF-8 error: {e2}")
        logger.error(f" Latin-1 error: {e3}")
        logger.error(f" Raw content (hex): {response.content[:200].hex()}")
        logger.error(f" Raw content (repr): {repr(response.content[:200])}")

        error_msg = (
            f"Failed to parse JSON response from portal.\n"
            f" Content-Type: {response.headers.get('Content-Type', 'unknown')}\n"
            f" Content-Encoding: {response.headers.get('Content-Encoding', 'none')}\n"
            f" Response encoding: {response.encoding}\n"
            f" Raw bytes (first 50): {response.content[:50].hex()}\n"
            f" This might indicate the response is compressed or corrupted.\n"
            f" Check askdelphi_debug.log for full details."
        )
        raise Exception(error_msg)


def _make_request(method: str, url: str, headers: dict, context: str) -> requests.Response:
    """Make HTTP request with common error handling.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        headers: Request headers
        context: Context string for error messages
        
    Returns:
        Response object if successful
        
    Raises:
        Exception: If request fails
    """
    log_request(method, url, headers)
    
    try:
        response = requests.request(method, url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        error_msg = f"{context} mislukt: {e}"
        if "Failed to resolve" in str(e) or "Connection" in str(e):
            logger.debug(error_msg)
        else:
            logger.error(error_msg)
        raise Exception(error_msg)
    
    log_response(response)
    return response


def parse_cms_url(url: str) -> Tuple[str, str, str]:
    """Parse een Ask Delphi CMS URL en haal tenant_id, project_id, acl_entry_id uit.

    URL format:
    https://xxx.askdelphi.com/cms/tenant/{TENANT_ID}/project/{PROJECT_ID}/acl/{ACL_ENTRY_ID}/...

    Args:
        url: De CMS URL uit de browser

    Returns:
        Tuple van (tenant_id, project_id, acl_entry_id)

    Raises:
        ValueError: Indien URL niet kan worden geparst
    """
    pattern = r'/tenant/([^/]+)/project/([^/]+)/acl/([^/]+)'
    match = re.search(pattern, url, re.IGNORECASE)

    if not match:
        raise ValueError(
            f"Kon CMS URL niet parsen: {url}\n"
            "Verwacht format: https://xxx.askdelphi.com/cms/tenant/{TENANT_ID}/project/{PROJECT_ID}/acl/{ACL_ENTRY_ID}/..."
        )

    return match.group(1), match.group(2), match.group(3)


class TokenCache:
    """Beheert token caching en persistentie."""

    def __init__(self, cache_file: str = ".askdelphi_tokens.json"):
        """Initialiseer token cache.

        Args:
            cache_file: Pad naar cache bestand voor token opslag
        """
        self.cache_file = cache_file
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.publication_url: Optional[str] = None
        self.api_token: Optional[str] = None
        self.api_token_expiry: float = 0

    def load(self) -> bool:
        """Laad tokens uit cache bestand.

        Returns:
            True indien tokens werden geladen, False anders
        """
        try:
            path = Path(self.cache_file)
            if path.exists():
                data = json.loads(path.read_text())
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.publication_url = data.get("publication_url")
                logger.info(f"Cached tokens geladen uit {self.cache_file}")
                return True
        except Exception as e:
            logger.debug(f"Geen cached tokens geladen: {e}")
        return False

    def save(self) -> None:
        """Sla tokens op in cache bestand."""
        data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "publication_url": self.publication_url,
            "saved_at": datetime.now().isoformat()
        }
        try:
            Path(self.cache_file).write_text(json.dumps(data, indent=2))
            logger.debug(f"Tokens opgeslagen in {self.cache_file}")
        except Exception as e:
            logger.warning(f"Kon tokens niet opslaan: {e}")

    def is_api_token_valid(self) -> bool:
        """Controleer of API token nog geldig is (met buffer)."""
        return self.api_token and time.time() < self.api_token_expiry - TOKEN_EXPIRY_BUFFER

    def set_api_token(self, token: str) -> None:
        """Stel API token in en parse zijn expiry tijd.

        Args:
            token: JWT token string
        """
        self.api_token = token

        try:
            payload = token.split(".")[1]
            payload += "=" * (4 - len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            self.api_token_expiry = decoded.get("exp", time.time() + DEFAULT_TOKEN_EXPIRY)
            logger.debug(f"Token verloopt op: {datetime.fromtimestamp(self.api_token_expiry)}")
        except Exception as e:
            logger.warning(f"Kon JWT expiry niet parsen: {e}")
            self.api_token_expiry = time.time() + DEFAULT_TOKEN_EXPIRY


class AskDelphiAuth:
    """Beheert authenticatie met automatische token vernieuwing en caching."""

    PORTAL_SERVER = "https://portal.askdelphi.com"
    API_SERVER = "https://edit.api.askdelphi.com"

    def __init__(
        self,
        cms_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        project_id: Optional[str] = None,
        acl_entry_id: Optional[str] = None,
        token_cache_file: str = ".askdelphi_tokens.json"
    ):
        """Initialiseer authenticatie manager.

        Args:
            cms_url: Volledige CMS URL met tenant/project/acl IDs (makkelijkste optie)
            tenant_id: Tenant ID (fallback indien cms_url niet gegeven)
            project_id: Project ID (fallback indien cms_url niet gegeven)
            acl_entry_id: ACL entry ID (fallback indien cms_url niet gegeven)
            token_cache_file: Bestand om tokens in op te slaan
        """
        cms_url = cms_url or os.getenv("ASKDELPHI_CMS_URL")

        if cms_url:
            try:
                parsed_tenant, parsed_project, parsed_acl = parse_cms_url(cms_url)
                logger.info("IDs geparst uit CMS URL")
                self.tenant_id = tenant_id or parsed_tenant
                self.project_id = project_id or parsed_project
                self.acl_entry_id = acl_entry_id or parsed_acl
            except ValueError as e:
                logger.warning(f"Kon CMS URL niet parsen: {e}")
                self.tenant_id = tenant_id or os.getenv("ASKDELPHI_TENANT_ID")
                self.project_id = project_id or os.getenv("ASKDELPHI_PROJECT_ID")
                self.acl_entry_id = acl_entry_id or os.getenv("ASKDELPHI_ACL_ENTRY_ID")
        else:
            self.tenant_id = tenant_id or os.getenv("ASKDELPHI_TENANT_ID")
            self.project_id = project_id or os.getenv("ASKDELPHI_PROJECT_ID")
            self.acl_entry_id = acl_entry_id or os.getenv("ASKDELPHI_ACL_ENTRY_ID")

        missing = []
        if not self.tenant_id:
            missing.append("ASKDELPHI_TENANT_ID (of ASKDELPHI_CMS_URL)")
        if not self.project_id:
            missing.append("ASKDELPHI_PROJECT_ID (of ASKDELPHI_CMS_URL)")
        if not self.acl_entry_id:
            missing.append("ASKDELPHI_ACL_ENTRY_ID (of ASKDELPHI_CMS_URL)")

        if missing:
            error_msg = f"Ontbrekende vereiste credentials: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        self.portal_code = os.getenv("ASKDELPHI_PORTAL_CODE")
        self.cache = TokenCache(token_cache_file)

        self.cache.load()

    def _try_cached_tokens(self) -> bool:
        """Try to authenticate using cached tokens.
        
        Returns:
            True if cached tokens are valid, False otherwise
        """
        if not (self.cache.access_token and self.cache.publication_url):
            return False
            
        logger.info("Cached tokens gevonden, proberen te gebruiken...")
        try:
            self._get_api_token()
            logger.info("SUCCES: Geverifieerd met cached tokens")
            return True
        except Exception as e:
            if "Failed to resolve" in str(e) or "Connection" in str(e):
                logger.debug(f"Cached tokens mislukt (verbindingsprobleem): {type(e).__name__}")
            else:
                logger.warning(f"Cached tokens mislukt: {e}")
            return False

    def _exchange_portal_code(self, code: str) -> dict:
        """Exchange portal code for access tokens.
        
        Args:
            code: Portal code from user
            
        Returns:
            Dictionary with accessToken, refreshToken, and url
        """
        logger.info("Stap 1: Portal code uitwisselen voor tokens...")
        url = f"{PORTAL_SERVER}/api/session/registration?sessionCode={code}"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "AskDelphi-Python-Client/1.0"
        }

        try:
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.Timeout:
            error_msg = f"Request timed out after {REQUEST_TIMEOUT} seconds"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)

        log_response(response)
        logger.debug(f"Response encoding: {response.encoding}")
        logger.debug(f"Content-Encoding header: {response.headers.get('Content-Encoding', 'none')}")

        if not response.ok:
            error_msg = self._format_error_response(response, "Portal code exchange")
            logger.error(error_msg)
            raise Exception(error_msg)

        return _parse_json_response(response)

    def _extract_and_save_tokens(self, data: dict) -> None:
        """Extract tokens from portal response and save to cache.
        
        Args:
            data: Response data from portal
            
        Raises:
            Exception: If required tokens are missing
        """
        self.cache.access_token = data.get("accessToken")
        self.cache.refresh_token = data.get("refreshToken")

        full_url = data.get("url", "")
        if full_url:
            parsed = urlparse(full_url)
            self.cache.publication_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            self.cache.publication_url = ""

        logger.info(f"Received access token: {self.cache.access_token[:20] if self.cache.access_token else 'None'}...")
        logger.info(f"Received refresh token: {self.cache.refresh_token[:20] if self.cache.refresh_token else 'None'}...")
        logger.info(f"Extracted base URL: {self.cache.publication_url}")

        if not self.cache.access_token:
            error_msg = f"No accessToken in portal response. Response was: {data}"
            logger.error(error_msg)
            raise Exception(error_msg)

        if not self.cache.publication_url:
            error_msg = f"No url in portal response. Response was: {data}"
            logger.error(error_msg)
            raise Exception(error_msg)

        self.cache.save()
        logger.info("Tokens saved to cache file")

    def authenticate(self, portal_code: Optional[str] = None) -> bool:
        """Authenticeer met de API.

        Probeert eerst cached tokens te gebruiken. Indien niet beschikbaar of verlopen,
        gebruikt de portal code om nieuwe tokens op te halen.

        Args:
            portal_code: Optionele portal code om te gebruiken (overschrijft opgeslagen code)

        Returns:
            True indien authenticatie succesvol
        """
        logger.info("="*60)
        logger.info("AUTHENTICATIE GESTART")
        logger.info("="*60)

        if self._try_cached_tokens():
            return True

        code = portal_code or self.portal_code
        if not code:
            error_msg = (
                "Geen portal code beschikbaar. Geef er een via:\n"
                " - argument naar authenticate()\n"
                " - constructor parameter\n"
                " - ASKDELPHI_PORTAL_CODE in .env bestand"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        data = self._exchange_portal_code(code)
        self._extract_and_save_tokens(data)

        logger.info("Stap 2: Getting editing API token...")
        self._get_api_token()

        logger.info("="*60)
        logger.info("AUTHENTICATION SUCCESSFUL")
        logger.info("="*60)
        return True

    def _format_error_response(self, response: requests.Response, context: str) -> str:
        """Formatteer een gedetailleerd foutbericht van een mislukte response."""
        lines = [
            f"{context} mislukt!",
            f"",
            f" Status Code: {response.status_code} {response.reason}",
            f" URL: {response.url}",
            f" Content-Type: {response.headers.get('Content-Type', 'onbekend')}",
        ]

        try:
            content_type = response.headers.get('Content-Type', '')
            if 'json' in content_type:
                try:
                    body = response.json()
                    lines.append(f" Response (JSON): {json.dumps(body, indent=4)}")
                except (ValueError, json.JSONDecodeError):
                    lines.append(f" Response (text): {response.text[:RESPONSE_TEXT_LIMIT]}")
            else:
                lines.append(f" Response (text): {response.text[:RESPONSE_TEXT_LIMIT]}")
        except Exception:
            lines.append(f" Response: (kon niet decoderen)")

        lines.append("")
        lines.append("Probleemoplossing:")

        if response.status_code == 401:
            lines.append(" - 401 Unauthorized: De portal code kan ongeldig, verlopen of al gebruikt zijn.")
            lines.append(" - Portal codes zijn EENMALIG GEBRUIK. Haal een verse code uit het Mobile tabblad.")
            lines.append(" - Zorg dat je de volledige code kopieert (format: ABC123-XYZ789)")
        elif response.status_code == 404:
            lines.append(" - 404 Not Found: Het endpoint bestaat niet op deze URL.")
            lines.append(" - Dit kan betekenen dat de portal server URL fout is.")
            lines.append(f" - De juiste portal is altijd: {PORTAL_SERVER}")
        elif response.status_code == 403:
            lines.append(" - 403 Forbidden: Toegang geweigerd. Controleer je machtigingen.")
        elif response.status_code >= 500:
            lines.append(" - 5xx Server Error: De server heeft problemen. Probeer later opnieuw.")

        return "\n".join(lines)

    def get_api_token(self) -> str:
        """Haal API token op, vernieuw indien nodig.

        Returns:
            Geldig API token
        """
        if self.cache.is_api_token_valid():
            logger.debug("Cached API token gebruiken (nog geldig)")
            return self.cache.api_token

        if self.cache.refresh_token and not self.cache.is_api_token_valid():
            logger.debug("API token verlopen of verloopt binnenkort, probeer vernieuwen...")
            try:
                self._refresh_tokens()
            except Exception as e:
                if "Failed to resolve" in str(e) or "Connection" in str(e):
                    logger.debug(f"Token vernieuwen mislukt (verbindingsprobleem): {type(e).__name__}")
                else:
                    logger.warning(f"Token vernieuwen mislukt: {e}")

        self._get_api_token()
        return self.cache.api_token

    def _get_api_token(self) -> None:
        """Haal een nieuw API token op met behulp van access token."""
        logger.debug("API token ophalen...")

        if not self.cache.access_token or not self.cache.publication_url:
            raise Exception("Geen access token beschikbaar. Roep authenticate() eerst aan.")

        url = f"{self.cache.publication_url}/api/token/EditingApiToken"
        headers = {
            "Authorization": f"Bearer {self.cache.access_token}",
            "Accept": "application/json",
            "User-Agent": "AskDelphi-Python-Client/1.0"
        }

        log_request("GET", url, headers)

        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as e:
            error_msg = f"Kon editing API token niet ophalen: {e}"
            if "Failed to resolve" in str(e) or "Connection" in str(e):
                logger.debug(error_msg)
            else:
                logger.error(error_msg)
            raise Exception(error_msg)

        log_response(response)

        if not response.ok:
            error_msg = self._format_error_response(response, "Editing API token ophalen")
            logger.error(error_msg)
            raise Exception(error_msg)

        content_type = response.headers.get('Content-Type', '')
        if 'html' in content_type.lower():
            error_msg = (
                "HTML ontvangen in plaats van JSON van EditingApiToken endpoint.\n"
                f" URL: {url}\n"
                f" Content-Type: {content_type}\n"
                f" Dit betekent meestal dat de publication URL incorrect is.\n"
                f" De URL moet alleen het base domein zijn (bijv. https://company.askdelphi.com)\n"
                f" Huidige publication URL: {self.cache.publication_url}\n"
                " Probeer .askdelphi_tokens.json te verwijderen en opnieuw te authenticeren met een verse portal code."
            )
            logger.error(error_msg)
            raise Exception(error_msg)

        try:
            token = response.json()
            if isinstance(token, str):
                pass
            elif isinstance(token, dict):
                token = token.get("token") or token.get("accessToken") or str(token)
        except (ValueError, json.JSONDecodeError):
            token = response.text.strip().strip('"')

        logger.info(f" Editing API token ontvangen: {token[:30] if len(token) > 30 else token}...")

        if not token.startswith(JWT_PREFIX):
            error_msg = (
                f"Ongeldig API token ontvangen - ziet er niet uit als JWT.\n"
                f" Token begint met: {token[:50]}...\n"
                f" Verwacht: {JWT_PREFIX}... (base64 gecodeerde JSON)\n"
                f" Dit kan betekenen dat de server een foutpagina retourneerde in plaats van een token.\n"
                f" Controleer askdelphi_debug.log voor details."
            )
            logger.error(error_msg)
            raise Exception(error_msg)

        self.cache.set_api_token(token)

    def _refresh_tokens(self) -> None:
        """Vernieuw de access token met behulp van refresh token."""
        logger.debug("Tokens vernieuwen...")

        if not self.cache.refresh_token or not self.cache.publication_url:
            raise Exception("Geen refresh token beschikbaar")

        url = (
            f"{self.cache.publication_url}/api/token/refresh"
            f"?token={self.cache.access_token}&refreshToken={self.cache.refresh_token}"
        )
        headers = {
            "Authorization": f"Bearer {self.cache.access_token}",
            "Accept": "application/json",
            "User-Agent": "AskDelphi-Python-Client/1.0"
        }

        response = _make_request("GET", url, headers, "Token vernieuwen")

        if not response.ok:
            raise Exception(f"Token vernieuwen mislukt: {response.status_code}")

        data = response.json()
        self.cache.access_token = data.get("token") or data.get("accessToken", self.cache.access_token)
        self.cache.refresh_token = data.get("refresh") or data.get("refreshToken", self.cache.refresh_token)

        self.cache.save()
        logger.info("Tokens succesvol vernieuwd")
