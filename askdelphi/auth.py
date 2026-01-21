"""Authentication module with URL parsing and token caching.

This module provides:
- CMS URL parsing to extract tenant, project, and ACL IDs
- Token caching and persistence
- Automatic token refresh before expiry
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


def log_request(method: str, url: str, headers: dict) -> None:
    """Log HTTP request details."""
    logger.debug(f"Request: {method} {url}")
    logger.debug(f"Headers: {headers}")


def log_response(response: requests.Response) -> None:
    """Log HTTP response details."""
    try:
        logger.debug(f"Response Status: {response.status_code}")
        logger.debug(f"Response Headers: {dict(response.headers)}")
        logger.debug(f"Response Body (first 500 chars): {response.text[:500]}")
    except Exception as e:
        logger.debug(f"Could not log response details: {e}")


def parse_cms_url(url: str) -> Tuple[str, str, str]:
    """
    Parse an Ask Delphi CMS URL and extract tenant_id, project_id, acl_entry_id.

    URL format:
    https://xxx.askdelphi.com/cms/tenant/{TENANT_ID}/project/{PROJECT_ID}/acl/{ACL_ENTRY_ID}/...

    Args:
        url: The CMS URL from the browser

    Returns:
        Tuple of (tenant_id, project_id, acl_entry_id)

    Raises:
        ValueError: If URL cannot be parsed
    """
    pattern = r'/tenant/([^/]+)/project/([^/]+)/acl/([^/]+)'
    match = re.search(pattern, url, re.IGNORECASE)

    if not match:
        raise ValueError(
            f"Could not parse CMS URL: {url}\n"
            "Expected format: https://xxx.askdelphi.com/cms/tenant/{TENANT_ID}/project/{PROJECT_ID}/acl/{ACL_ENTRY_ID}/..."
        )

    return match.group(1), match.group(2), match.group(3)


class TokenCache:
    """Manages token caching and persistence."""

    def __init__(self, cache_file: str = ".askdelphi_tokens.json"):
        """
        Initialize token cache.

        Args:
            cache_file: Path to cache file for storing tokens
        """
        self.cache_file = cache_file
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.publication_url: Optional[str] = None
        self.api_token: Optional[str] = None
        self.api_token_expiry: float = 0

    def load(self) -> bool:
        """
        Load tokens from cache file.

        Returns:
            True if tokens were loaded, False otherwise
        """
        try:
            path = Path(self.cache_file)
            if path.exists():
                data = json.loads(path.read_text())
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.publication_url = data.get("publication_url")
                logger.info(f"Loaded cached tokens from {self.cache_file}")
                return True
        except Exception as e:
            logger.debug(f"No cached tokens loaded: {e}")
        return False

    def save(self) -> None:
        """Save tokens to cache file."""
        data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "publication_url": self.publication_url,
            "saved_at": datetime.now().isoformat()
        }
        try:
            Path(self.cache_file).write_text(json.dumps(data, indent=2))
            logger.debug(f"Tokens saved to {self.cache_file}")
        except Exception as e:
            logger.warning(f"Could not save tokens: {e}")

    def is_api_token_valid(self) -> bool:
        """Check if API token is still valid (with 300 sec buffer)."""
        return self.api_token and time.time() < self.api_token_expiry - 300

    def set_api_token(self, token: str) -> None:
        """
        Set API token and parse its expiry time.

        Args:
            token: JWT token string
        """
        self.api_token = token

        # Parse JWT expiry
        try:
            payload = token.split(".")[1]
            # Add padding if needed
            payload += "=" * (4 - len(payload) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            self.api_token_expiry = decoded.get("exp", time.time() + 3600)
            logger.debug(f"Token expires at: {datetime.fromtimestamp(self.api_token_expiry)}")
        except Exception as e:
            logger.warning(f"Could not parse JWT expiry: {e}")
            self.api_token_expiry = time.time() + 3600  # Default 1 hour


class AskDelphiAuth:
    """Manages authentication with automatic token refresh and caching."""

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
        """
        Initialize authentication manager.

        Args:
            cms_url: Full CMS URL containing tenant/project/acl IDs (easiest option)
            tenant_id: Tenant ID (fallback if cms_url not provided)
            project_id: Project ID (fallback if cms_url not provided)
            acl_entry_id: ACL entry ID (fallback if cms_url not provided)
            token_cache_file: File to cache tokens in
        """
        # Try to get IDs from CMS URL first (easiest option)
        cms_url = cms_url or os.getenv("ASKDELPHI_CMS_URL")

        if cms_url:
            try:
                parsed_tenant, parsed_project, parsed_acl = parse_cms_url(cms_url)
                logger.info("Parsed IDs from CMS URL")
                self.tenant_id = tenant_id or parsed_tenant
                self.project_id = project_id or parsed_project
                self.acl_entry_id = acl_entry_id or parsed_acl
            except ValueError as e:
                logger.warning(f"Could not parse CMS URL: {e}")
                # Fall back to individual variables
                self.tenant_id = tenant_id or os.getenv("ASKDELPHI_TENANT_ID")
                self.project_id = project_id or os.getenv("ASKDELPHI_PROJECT_ID")
                self.acl_entry_id = acl_entry_id or os.getenv("ASKDELPHI_ACL_ENTRY_ID")
        else:
            # Use individual variables
            self.tenant_id = tenant_id or os.getenv("ASKDELPHI_TENANT_ID")
            self.project_id = project_id or os.getenv("ASKDELPHI_PROJECT_ID")
            self.acl_entry_id = acl_entry_id or os.getenv("ASKDELPHI_ACL_ENTRY_ID")

        # Validate required fields
        missing = []
        if not self.tenant_id:
            missing.append("ASKDELPHI_TENANT_ID (or ASKDELPHI_CMS_URL)")
        if not self.project_id:
            missing.append("ASKDELPHI_PROJECT_ID (or ASKDELPHI_CMS_URL)")
        if not self.acl_entry_id:
            missing.append("ASKDELPHI_ACL_ENTRY_ID (or ASKDELPHI_CMS_URL)")

        if missing:
            error_msg = f"Missing required credentials: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        self.portal_code = os.getenv("ASKDELPHI_PORTAL_CODE")
        self.cache = TokenCache(token_cache_file)

        # Try to load cached tokens
        self.cache.load()

    def authenticate(self, portal_code: Optional[str] = None) -> bool:
        """
        Authenticate with the API.

        First tries to use cached tokens. If not available or expired,
        uses the portal code to get new tokens.

        Args:
            portal_code: Optional portal code to use (overrides stored code)

        Returns:
            True if authentication successful
        """
        logger.info("="*60)
        logger.info("AUTHENTICATION STARTED")
        logger.info("="*60)

        # Try to get API token with existing tokens
        if self.cache.access_token and self.cache.publication_url:
            logger.info("Found cached tokens, trying to use them...")
            try:
                self._get_api_token()
                logger.info("SUCCESS: Authenticated using cached tokens")
                return True
            except Exception as e:
                logger.warning(f"Cached tokens failed: {e}")
                logger.info("Will try portal code authentication...")

        # Use portal code
        code = portal_code or self.portal_code
        if not code:
            error_msg = (
                "No portal code available. Provide one via:\n"
                " - argument to authenticate()\n"
                " - constructor parameter\n"
                " - ASKDELPHI_PORTAL_CODE in .env file"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Step 1: Exchange portal code for tokens
        logger.info("Step 1: Exchanging portal code for tokens...")
        url = f"{self.PORTAL_SERVER}/api/session/registration?sessionCode={code}"
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "AskDelphi-Python-Client/1.0"
        }

        log_request("GET", url, headers)

        try:
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=30)
        except requests.exceptions.Timeout:
            error_msg = "Request timed out after 30 seconds"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)

        log_response(response)

        # Log raw response info for debugging
        logger.debug(f"Response encoding: {response.encoding}")
        logger.debug(f"Response apparent_encoding: {response.apparent_encoding}")
        logger.debug(f"Content-Encoding header: {response.headers.get('Content-Encoding', 'none')}")
        logger.debug(f"Raw content first 100 bytes: {response.content[:100]}")

        if not response.ok:
            error_msg = self._format_error_response(response, "Portal code exchange")
            logger.error(error_msg)
            raise Exception(error_msg)

        # Parse response - handle potential encoding issues
        try:
            # First try the standard way
            data = response.json()
            logger.debug(f"Parsed JSON response: {json.dumps(data, indent=2)}")
        except (ValueError, UnicodeDecodeError) as e:
            logger.warning(f"Standard JSON parsing failed: {e}")

            # Try to decode manually with different approaches
            try:
                # Try decoding as utf-8 from raw content
                text = response.content.decode('utf-8')
                data = json.loads(text)
                logger.debug(f"Parsed JSON via manual utf-8 decode: {json.dumps(data, indent=2)}")
            except (UnicodeDecodeError, json.JSONDecodeError) as e2:
                logger.warning(f"Manual utf-8 decode failed: {e2}")

                # Try latin-1 (accepts any byte)
                try:
                    text = response.content.decode('latin-1')
                    data = json.loads(text)
                    logger.debug(f"Parsed JSON via latin-1 decode: {json.dumps(data, indent=2)}")
                except json.JSONDecodeError as e3:
                    # Log extensive debug info
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

        # Extract tokens
        self.cache.access_token = data.get("accessToken")
        self.cache.refresh_token = data.get("refreshToken")

        # IMPORTANT: Extract only the base URL (scheme + host) from the returned URL.
        # The portal returns a full URL with path like:
        # https://company.askdelphi.com/nl-NL/Project/page/eyJMMSI6...
        # But we only need the base URL for API calls:
        # https://company.askdelphi.com
        full_url = data.get("url", "")
        if full_url:
            parsed = urlparse(full_url)
            self.cache.publication_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            self.cache.publication_url = ""

        logger.info(f"Received access token: {self.cache.access_token[:20] if self.cache.access_token else 'None'}...")
        logger.info(f"Received refresh token: {self.cache.refresh_token[:20] if self.cache.refresh_token else 'None'}...")
        logger.info(f"Full URL from portal: {full_url}")
        logger.info(f"Extracted base URL: {self.cache.publication_url}")

        if not self.cache.access_token:
            error_msg = f"No accessToken in portal response. Response was: {data}"
            logger.error(error_msg)
            raise Exception(error_msg)

        if not self.cache.publication_url:
            error_msg = f"No url in portal response. Response was: {data}"
            logger.error(error_msg)
            raise Exception(error_msg)

        # Save tokens
        self.cache.save()
        logger.info("Tokens saved to cache file")

        # Step 2: Get API token
        logger.info(f"Step 2: Getting editing API token...")
        self._get_api_token()

        logger.info("="*60)
        logger.info("AUTHENTICATION SUCCESSFUL")
        logger.info("="*60)
        return True

    def _format_error_response(self, response: requests.Response, context: str) -> str:
        """Format a detailed error message from a failed response."""
        lines = [
            f"{context} failed!",
            f"",
            f" Status Code: {response.status_code} {response.reason}",
            f" URL: {response.url}",
            f" Content-Type: {response.headers.get('Content-Type', 'unknown')}",
        ]

        # Try to get response body
        try:
            content_type = response.headers.get('Content-Type', '')
            if 'json' in content_type:
                try:
                    body = response.json()
                    lines.append(f" Response (JSON): {json.dumps(body, indent=4)}")
                except:
                    lines.append(f" Response (text): {response.text[:1000]}")
            else:
                lines.append(f" Response (text): {response.text[:1000]}")
        except:
            lines.append(f" Response: (could not decode)")

        # Add troubleshooting hints based on status code
        lines.append("")
        lines.append("Troubleshooting:")

        if response.status_code == 401:
            lines.append(" - 401 Unauthorized: The portal code may be invalid, expired, or already used.")
            lines.append(" - Portal codes are ONE-TIME USE. Get a fresh code from the Mobile tab.")
            lines.append(" - Make sure you're copying the full code (format: ABC123-XYZ789)")
        elif response.status_code == 404:
            lines.append(" - 404 Not Found: The endpoint doesn't exist at this URL.")
            lines.append(" - This might mean the portal server URL is wrong.")
            lines.append(" - The correct portal is always: https://portal.askdelphi.com")
        elif response.status_code == 403:
            lines.append(" - 403 Forbidden: Access denied. Check your permissions.")
        elif response.status_code >= 500:
            lines.append(" - 5xx Server Error: The server is having issues. Try again later.")

        return "\n".join(lines)

    def get_api_token(self) -> str:
        """
        Get API token, refreshing if necessary.

        Returns:
        """
        if self.cache.is_api_token_valid():
            logger.debug("Using cached API token (still valid)")
            return self.cache.api_token

        # Try to refresh if token is expired
        if self.cache.refresh_token and not self.cache.is_api_token_valid():
            logger.debug("API token expired or expiring soon, trying refresh...")
            try:
                self._refresh_tokens()
            except Exception as e:
                logger.warning(f"Token refresh failed: {e}")

        # Get new API token
        self._get_api_token()
        return self.cache.api_token

    def _get_api_token(self) -> None:
        """Get a new API token using access token."""
        logger.debug("Getting API token...")

        if not self.cache.access_token or not self.cache.publication_url:
            raise Exception("No access token available. Call authenticate() first.")

        url = f"{self.cache.publication_url}/api/token/EditingApiToken"
        headers = {
            "Authorization": f"Bearer {self.cache.access_token}",
            "Accept": "application/json",
            "User-Agent": "AskDelphi-Python-Client/1.0"
        }

        log_request("GET", url, headers)

        try:
            response = requests.get(url, headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get editing API token: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)

        log_response(response)

        if not response.ok:
            error_msg = self._format_error_response(response, "Get editing API token")
            logger.error(error_msg)
            raise Exception(error_msg)

        # Check if we got HTML instead of JSON (indicates wrong URL)
        content_type = response.headers.get('Content-Type', '')
        if 'html' in content_type.lower():
            error_msg = (
                "Received HTML instead of JSON from EditingApiToken endpoint.\n"
                f" URL: {url}\n"
                f" Content-Type: {content_type}\n"
                f" This usually means the publication URL is incorrect.\n"
                f" The URL should be just the base domain (e.g., https://company.askdelphi.com)\n"
                f" Current publication URL: {self.cache.publication_url}\n"
                " Try deleting .askdelphi_tokens.json and authenticating with a fresh portal code."
            )
            logger.error(error_msg)
            raise Exception(error_msg)

        # Parse token (might be a JSON string or plain text)
        try:
            token = response.json()
            if isinstance(token, str):
                pass  # Already a string
            elif isinstance(token, dict):
                token = token.get("token") or token.get("accessToken") or str(token)
        except:
            token = response.text.strip().strip('"')

        logger.info(f" Received editing API token: {token[:30] if len(token) > 30 else token}...")

        # Validate that the token looks like a JWT
        if not token.startswith("eyJ"):
            error_msg = (
                f"Invalid API token received - does not look like a JWT.\n"
                f" Token starts with: {token[:50]}...\n"
                f" Expected: eyJ... (base64 encoded JSON)\n"
                f" This might indicate the server returned an error page instead of a token.\n"
                f" Check askdelphi_debug.log for details."
            )
            logger.error(error_msg)
            raise Exception(error_msg)

        self.cache.set_api_token(token)

    def _refresh_tokens(self) -> None:
        """Refresh the access token using refresh token."""
        logger.debug("Refreshing tokens...")

        if not self.cache.refresh_token or not self.cache.publication_url:
            raise Exception("No refresh token available")

        url = (
            f"{self.cache.publication_url}/api/token/refresh"
            f"?token={self.cache.access_token}&refreshToken={self.cache.refresh_token}"
        )
        headers = {
            "Authorization": f"Bearer {self.cache.access_token}",
            "Accept": "application/json",
            "User-Agent": "AskDelphi-Python-Client/1.0"
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            error_msg = f"Token refresh failed: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)

        if not response.ok:
            raise Exception(f"Failed to refresh token: {response.status_code}")

        data = response.json()
        self.cache.access_token = data.get("token") or data.get("accessToken", self.cache.access_token)
        self.cache.refresh_token = data.get("refresh") or data.get("refreshToken", self.cache.refresh_token)

        self.cache.save()
        logger.info("Tokens refreshed successfully")
