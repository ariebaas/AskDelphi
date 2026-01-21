"""AskDelphiSession with debug-mode and .env configuration.

This module defines the central AskDelphiSession client that:
- Manages authentication and session tokens
- Automatically refreshes tokens when expired
- Injects tenant, NT-account, ACL and project context
- Provides debug logging controlled via the DEBUG environment variable
"""

import time
from typing import Optional

import requests

from config.env import DEBUG
from askdelphi.exceptions import AskDelphiAuthError


class AskDelphiSession:
    """Central client for all AskDelphi API calls.

    This client abstracts away:
    - Session token retrieval and refresh
    - Context injection (tenant, NT-account, ACL, project)
    - Basic error handling and debug logging
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        tenant: str,
        nt_account: str,
        acl: list,
        project_id: str,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.tenant = tenant
        self.nt_account = nt_account
        self.acl = acl
        self.project_id = project_id

        self.session_token: Optional[str] = None
        self.token_expiry: float = 0

        if DEBUG:
            print(" [DEBUG] AskDelphiSession initialized")
            print(f"  Base URL: {self.base_url}")
            print(f"  Tenant: {self.tenant}")
            print(f"  NT Account: {self.nt_account}")
            print(f"  ACL: {self.acl}")
            print(f"  Project: {self.project_id}")

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
