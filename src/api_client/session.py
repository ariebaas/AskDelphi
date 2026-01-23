"""AskDelphiSession met debug-mode en .env configuratie.

Deze module definieert de centrale AskDelphiSession client die:
- Authenticatie en sessie tokens beheert
- Tokens automatisch vernieuwt wanneer verlopen
- Tenant, NT-account, ACL en project context injecteert
- Debug logging biedt gecontroleerd via DEBUG omgevingsvariabele
- CMS URL parsing en token caching ondersteunt
"""

import os
import time
from typing import Optional

import requests
from dotenv import load_dotenv

from ..config.env import DEBUG
from .exceptions import AskDelphiAuthError
from .auth import AskDelphiAuth, parse_cms_url


def _get_config_value(param_value: Optional[str], env_var: str) -> Optional[str]:
    """Haal configuratie waarde op van parameter of omgevingsvariabele.
    
    Args:
        param_value: Waarde doorgegeven als parameter
        env_var: Naam van omgevingsvariabele
        
    Returns:
        Parameter waarde indien gegeven, anders omgevingsvariabele waarde
    """
    return param_value or os.getenv(env_var)


class AskDelphiSession:
    """Centrale client voor alle AskDelphi API aanroepen.

    Deze client abstraheerd:
    - Sessie token ophalen en vernieuwen
    - Context injectie (tenant, NT-account, ACL, project)
    - Basis foutafhandeling en debug logging
    - CMS URL parsing en token caching
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
        """Initialiseer AskDelphiSession.

        Kan op twee manieren worden geïnitialiseerd:
        1. CMS URL: cms_url (geparst om tenant, project, acl uit te halen)
        2. Traditioneel: base_url, api_key, tenant, nt_account, acl, project_id

        Args:
            base_url: Base URL voor API aanroepen (of ASKDELPHI_BASE_URL uit .env)
            api_key: API sleutel voor authenticatie (of ASKDELPHI_API_KEY uit .env)
            tenant: Tenant ID (of ASKDELPHI_TENANT uit .env)
            nt_account: NT account (of ASKDELPHI_NT_ACCOUNT uit .env)
            acl: ACL lijst (of ASKDELPHI_ACL uit .env)
            project_id: Project ID (of ASKDELPHI_PROJECT_ID uit .env)
            cms_url: Volledige CMS URL (alternatief voor individuele parameters)
            use_auth_cache: Of token caching moet worden gebruikt
        """
        load_dotenv()

        cms_url = _get_config_value(cms_url, "ASKDELPHI_CMS_URL")

        if cms_url:
            try:
                parsed_tenant, parsed_project, parsed_acl = parse_cms_url(cms_url)
                tenant = tenant or parsed_tenant
                project_id = project_id or parsed_project
                acl = acl or [parsed_acl]
                if DEBUG:
                    print(" [DEBUG] Credentials geparst uit CMS URL")
            except ValueError as e:
                if DEBUG:
                    print(f" [DEBUG] Kon CMS URL niet parsen: {e}")

        base_url = _get_config_value(base_url, "ASKDELPHI_BASE_URL")
        api_key = _get_config_value(api_key, "ASKDELPHI_API_KEY")
        tenant = _get_config_value(tenant, "ASKDELPHI_TENANT")
        nt_account = _get_config_value(nt_account, "ASKDELPHI_NT_ACCOUNT")
        project_id = _get_config_value(project_id, "ASKDELPHI_PROJECT_ID")

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
                    print(" [DEBUG] Auth manager geïnitialiseerd met caching")
            except Exception as e:
                if DEBUG:
                    print(f" [DEBUG] Kon auth manager niet initialiseren: {e}")

        if DEBUG:
            print(" [DEBUG] AskDelphiSession geïnitialiseerd")
            print(f"  Base URL: {self.base_url}")
            print(f"  Tenant: {self.tenant}")
            print(f"  NT Account: {self.nt_account}")
            print(f"  ACL: {self.acl}")
            print(f"  Project: {self.project_id}")
            print(f"  Auth cache gebruiken: {use_auth_cache and self.auth_manager is not None}")

    def get(self, path: str):
        """Voer een GET verzoek uit tegen de AskDelphi API."""
        return self._request("GET", path)

    def post(self, path: str, json: dict):
        """Voer een POST verzoek uit tegen de AskDelphi API."""
        return self._request("POST", path, json=json)

    def put(self, path: str, json: dict):
        """Voer een PUT verzoek uit tegen de AskDelphi API."""
        return self._request("PUT", path, json=json)

    def delete(self, path: str):
        """Voer een DELETE verzoek uit tegen de AskDelphi API."""
        return self._request("DELETE", path)

    def _request(self, method: str, path: str, json: dict = None):
        """Interne helper om een HTTP verzoek met context en token handling te verzenden."""

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

        # Don't add _context to payload - it's not part of the API contract
        # The context is already embedded in the URL path parameters
        payload = json or {}

        # Vervang template parameters in path
        url_path = path
        if self.tenant and self.project_id and self.acl:
            acl_str = self.acl[0] if isinstance(self.acl, list) else self.acl
            url_path = (
                path
                .replace("{tenantId}", self.tenant)
                .replace("{projectId}", self.project_id)
                .replace("{aclEntryId}", acl_str)
            )

        # Zorg dat base_url eindigt met / en path begint met /
        base = self.base_url.rstrip("/")
        if not url_path.startswith("/"):
            url_path = "/" + url_path
        url = f"{base}{url_path}"

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
                print(" [DEBUG] Token verlopen, vernieuwen...")
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
                f"AskDelphi API fout {response.status_code}: {response.text}"
            )

        return response.json()

    def _refresh_token(self) -> None:
        """Haal een nieuw sessie token op van het /auth/session endpoint."""

        auth_payload = {
            "apiKey": self.api_key,
            "tenant": self.tenant,
            "ntAccount": self.nt_account,
            "acl": self.acl,
            "projectId": self.project_id,
        }

        if DEBUG:
            print("\n[DEBUG] Nieuw sessie token aanvragen...")

        response = requests.post(f"{self.base_url}/auth/session", json=auth_payload)

        if not response.ok:
            raise AskDelphiAuthError(
                f"Kon geen sessie-token ophalen: {response.status_code} {response.text}"
            )

        data = response.json()
        self.session_token = data["sessionToken"]
        self.token_expiry = time.time() + data.get("expiresIn", 3600)

        if DEBUG:
            print(f"[DEBUG] Nieuw sessie token: {self.session_token}")
            print(f"[DEBUG] Token verloopt over: {data.get('expiresIn', 3600)} sec")
