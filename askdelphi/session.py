"""AskDelphiSession with debug-mode and .env configuration.

This module defines the central AskDelphiSession client that:
- Manages authentication and session tokens
- Automatically refreshes tokens when expired
- Injects tenant, NT-account, ACL and project context
- Provides debug logging controlled via the DEBUG environment variable
- Supports CMS URL parsing and token caching
"""

import os
import time
from typing import Optional

import requests
from dotenv import load_dotenv

from config.env import DEBUG
from askdelphi.exceptions import AskDelphiAuthError
from askdelphi.auth import AskDelphiAuth, parse_cms_url


class AskDelphiSession:
    """Central client for all AskDelphi API calls.

    This client abstracts away:
    - Session token retrieval and refresh
    - Context injection (tenant, NT-account, ACL, project)
    - Basic error handling and debug logging
    - CMS URL parsing and token caching
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        tenant: Optional[str] = None,
        nt_account: Optional[str] = None,
        acl: Optional[list] = None,
        project_id: Optional[str] = None,
        cms_url: Optional[str] = None,
        use_auth_cache: bool = True,
    ) -> None:
        """
        Initialize AskDelphiSession.

        Can be initialized in two ways:
        1. CMS URL: cms_url (parsed to extract tenant, project, acl)
        2. Traditional: base_url, api_key, tenant, nt_account, acl, project_id

        Args:
            base_url: Base URL for API calls (or ASKDELPHI_BASE_URL from .env)
            api_key: API key for authentication (or ASKDELPHI_API_KEY from .env)
            tenant: Tenant ID (or ASKDELPHI_TENANT from .env)
            nt_account: NT account (or ASKDELPHI_NT_ACCOUNT from .env)
            acl: ACL list (or ASKDELPHI_ACL from .env)
            project_id: Project ID (or ASKDELPHI_PROJECT_ID from .env)
            cms_url: Full CMS URL (alternative to individual parameters)
            use_auth_cache: Whether to use token caching (from config)
        """
        load_dotenv()

        # Try to get CMS URL from .env if not provided
        cms_url = cms_url or os.getenv("ASKDELPHI_CMS_URL")

        # If CMS URL provided, parse it
        if cms_url:
            try:
                parsed_tenant, parsed_project, parsed_acl = parse_cms_url(cms_url)
                tenant = tenant or parsed_tenant
                project_id = project_id or parsed_project
                acl = acl or [parsed_acl]
                if DEBUG:
                    print(" [DEBUG] Parsed credentials from CMS URL")
            except ValueError as e:
                if DEBUG:
                    print(f" [DEBUG] Could not parse CMS URL: {e}")

        # Fallback to .env variables
        base_url = base_url or os.getenv("ASKDELPHI_BASE_URL")
        api_key = api_key or os.getenv("ASKDELPHI_API_KEY")
        tenant = tenant or os.getenv("ASKDELPHI_TENANT")
        nt_account = nt_account or os.getenv("ASKDELPHI_NT_ACCOUNT")
        project_id = project_id or os.getenv("ASKDELPHI_PROJECT_ID")

        if acl is None:
            acl_str = os.getenv("ASKDELPHI_ACL")
            acl = [acl_str] if acl_str else []

        self.base_url = base_url.rstrip("/") if base_url else None
        self.api_key = api_key
        self.tenant = tenant
        self.nt_account = nt_account
        self.acl = acl or []
        self.project_id = project_id

        self.session_token: Optional[str] = None
        self.token_expiry: float = 0

        # Initialize auth manager if using cache
        self.auth_manager: Optional[AskDelphiAuth] = None
        if use_auth_cache and tenant and project_id and acl:
            try:
                self.auth_manager = AskDelphiAuth(
                    cms_url=cms_url,
                    tenant_id=tenant,
                    project_id=project_id,
                    acl_entry_id=acl[0] if acl else None,
                )
                if DEBUG:
                    print(" [DEBUG] Auth manager initialized with caching")
            except Exception as e:
                if DEBUG:
                    print(f" [DEBUG] Could not initialize auth manager: {e}")

        if DEBUG:
            print(" [DEBUG] AskDelphiSession initialized")
            print(f"  Base URL: {self.base_url}")
            print(f"  Tenant: {self.tenant}")
            print(f"  NT Account: {self.nt_account}")
            print(f"  ACL: {self.acl}")
            print(f"  Project: {self.project_id}")
            print(f"  Using auth cache: {use_auth_cache and self.auth_manager is not None}")

    # -----------------------------
    # Public HTTP API
    # -----------------------------

    def get(self, path: str):
        """Perform a GET request against the AskDelphi API."""
        return self._request("GET", path)

    def post(self, path: str, json: dict):
        """Perform a POST request against the AskDelphi API."""
        return self._request("POST", path, json=json)

    def put(self, path: str, json: dict):
        """Perform a PUT request against the AskDelphi API."""
        return self._request("PUT", path, json=json)

    def delete(self, path: str):
        """Perform a DELETE request against the AskDelphi API."""
        return self._request("DELETE", path)

    # -----------------------------
    # Core request logic
    # -----------------------------

    def _request(self, method: str, path: str, json: dict = None):
        """Internal helper to send an HTTP request with context and token handling."""

        # Use auth manager if available, otherwise use session token
        if self.auth_manager:
            token = self.auth_manager.get_api_token()
            headers = {
                "Authorization": f"Bearer {token}",
            }
        else:
            if not self.session_token or time.time() >= self.token_expiry:
                self._refresh_token()

            headers = {
                "Authorization": f"Bearer {self.session_token}",
                "X-API-Key": self.api_key,
            }

        payload = json or {}
        payload["_context"] = {
            "tenant": self.tenant,
            "ntAccount": self.nt_account,
            "acl": self.acl,
            "projectId": self.project_id,
        }

        url = f"{self.base_url}{path}"

        if DEBUG:
            print(f"\n [DEBUG] {method} {url}")
            print(f"  Headers: {headers}")
            print(f"  Payload: {payload}")

        response = requests.request(method, url, json=payload, headers=headers)

        if DEBUG:
            print(f" [DEBUG] Response {response.status_code}")
            print(f"  Body: {response.text}")

        if response.status_code == 401:
            if DEBUG:
                print(" [DEBUG] Token expired, refreshing...")
            if self.auth_manager:
                self.auth_manager.authenticate()
                token = self.auth_manager.get_api_token()
                headers["Authorization"] = f"Bearer {token}"
            else:
                self._refresh_token()
                headers["Authorization"] = f"Bearer {self.session_token}"
            response = requests.request(method, url, json=payload, headers=headers)

        if not response.ok:
            raise AskDelphiAuthError(
                f"AskDelphi API error {response.status_code}: {response.text}"
            )

        return response.json()

    # -----------------------------
    # Token management
    # -----------------------------

    def _refresh_token(self) -> None:
        """Retrieve a new session token from the /auth/session endpoint."""

        auth_payload = {
            "apiKey": self.api_key,
            "tenant": self.tenant,
            "ntAccount": self.nt_account,
            "acl": self.acl,
            "projectId": self.project_id,
        }

        if DEBUG:
            print("\n[DEBUG] Requesting new session token...")

        response = requests.post(f"{self.base_url}/auth/session", json=auth_payload)

        if not response.ok:
            raise AskDelphiAuthError(
                f"Kon geen sessie-token ophalen: {response.status_code} {response.text}"
            )

        data = response.json()
        self.session_token = data["sessionToken"]
        self.token_expiry = time.time() + data.get("expiresIn", 3600)

        if DEBUG:
            print(f"[DEBUG] New session token: {self.session_token}")
            print(f"[DEBUG] Token expires in: {data.get('expiresIn', 3600)} sec")
