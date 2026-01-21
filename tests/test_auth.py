"""Tests voor authenticatie module met URL parsing en token caching."""

import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from api_client.auth import parse_cms_url, TokenCache, AskDelphiAuth


class TestParseCmsUrl:
    """Test CMS URL parsing."""

    def test_parse_valid_cms_url(self):
        """Test het parsen van een geldige CMS URL."""
        url = "https://company.askdelphi.com/cms/tenant/abc-123/project/def-456/acl/ghi-789/page"
        tenant, project, acl = parse_cms_url(url)

        assert tenant == "abc-123"
        assert project == "def-456"
        assert acl == "ghi-789"

    def test_parse_cms_url_case_insensitive(self):
        """Test dat URL parsing case-insensitief is."""
        url = "https://company.askdelphi.com/cms/TENANT/ABC-123/PROJECT/DEF-456/ACL/GHI-789/page"
        tenant, project, acl = parse_cms_url(url)

        assert tenant == "ABC-123"
        assert project == "DEF-456"
        assert acl == "GHI-789"

    def test_parse_invalid_cms_url(self):
        """Test dat ongeldige URL ValueError genereert."""
        url = "https://company.askdelphi.com/invalid/url"

        with pytest.raises(ValueError):
            parse_cms_url(url)


class TestTokenCache:
    """Test token caching functionaliteit."""

    def test_token_cache_initialization(self):
        """Test token cache initialisatie."""
        cache = TokenCache()

        assert cache.access_token is None
        assert cache.refresh_token is None
        assert cache.publication_url is None
        assert cache.api_token is None
        assert cache.api_token_expiry == 0

    def test_token_cache_save_and_load(self, tmp_path):
        """Test tokens opslaan en laden uit cache."""
        cache_file = tmp_path / "tokens.json"
        cache = TokenCache(str(cache_file))

        cache.access_token = "access_123"
        cache.refresh_token = "refresh_456"
        cache.publication_url = "https://company.askdelphi.com"

        cache.save()
        assert cache_file.exists()

        cache2 = TokenCache(str(cache_file))
        assert cache2.load()

        assert cache2.access_token == "access_123"
        assert cache2.refresh_token == "refresh_456"
        assert cache2.publication_url == "https://company.askdelphi.com"

    def test_token_cache_load_nonexistent(self, tmp_path):
        """Test laden uit niet-bestaand cache bestand."""
        cache_file = tmp_path / "nonexistent.json"
        cache = TokenCache(str(cache_file))

        assert not cache.load()

    def test_api_token_validity_check(self):
        """Test API token geldigheid controle."""
        cache = TokenCache()

        assert not cache.is_api_token_valid()

        cache.api_token = "token_123"
        cache.api_token_expiry = time.time() + 3600
        assert cache.is_api_token_valid()

        cache.api_token_expiry = time.time() + 100
        assert not cache.is_api_token_valid()

    def test_set_api_token_with_jwt(self):
        """Test API token instellen en JWT expiry parsing."""
        cache = TokenCache()
        
        # Create a mock JWT token
        import base64
        payload = {
            "exp": int(time.time()) + 3600,
            "sub": "user123"
        }
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        token = f"eyJ.{payload_b64}.signature"
        
        cache.set_api_token(token)
        
        assert cache.api_token == token
        assert cache.api_token_expiry > time.time()


class TestAskDelphiAuth:
    """Test AskDelphi authentication manager."""

    def test_auth_initialization_with_individual_ids(self):
        """Test auth initialization with individual IDs."""
        auth = AskDelphiAuth(
            tenant_id="tenant-123",
            project_id="project-456",
            acl_entry_id="acl-789"
        )
        
        assert auth.tenant_id == "tenant-123"
        assert auth.project_id == "project-456"
        assert auth.acl_entry_id == "acl-789"

    def test_auth_initialization_with_cms_url(self):
        """Test auth initialization with CMS URL."""
        cms_url = "https://company.askdelphi.com/cms/tenant/abc-123/project/def-456/acl/ghi-789/page"
        auth = AskDelphiAuth(cms_url=cms_url)
        
        assert auth.tenant_id == "abc-123"
        assert auth.project_id == "def-456"
        assert auth.acl_entry_id == "ghi-789"

    def test_auth_initialization_missing_credentials(self):
        """Test that auth raises error when credentials are missing."""
        with pytest.raises(ValueError):
            AskDelphiAuth(tenant_id="tenant-123")

    @patch.dict('os.environ', {'ASKDELPHI_PORTAL_CODE': 'ABC123-XYZ789'})
    @patch('askdelphi.auth.requests.Session')
    def test_authenticate_with_portal_code(self, mock_session):
        """Test authentication with portal code."""
        auth = AskDelphiAuth(
            tenant_id="tenant-123",
            project_id="project-456",
            acl_entry_id="acl-789"
        )
        
        # Mock portal response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.headers = {}
        mock_response.encoding = "utf-8"
        mock_response.apparent_encoding = "utf-8"
        mock_response.content = b'{"accessToken": "access_token_123", "refreshToken": "refresh_token_456", "url": "https://company.askdelphi.com/project/page"}'
        mock_response.text = '{"accessToken": "access_token_123", "refreshToken": "refresh_token_456", "url": "https://company.askdelphi.com/project/page"}'
        mock_response.json.return_value = {
            "accessToken": "access_token_123",
            "refreshToken": "refresh_token_456",
            "url": "https://company.askdelphi.com/project/page"
        }
        mock_session.return_value.get.return_value = mock_response
        
        # Mock API token response
        with patch('askdelphi.auth.requests.get') as mock_get:
            import base64
            payload = {
                "exp": int(time.time()) + 3600,
                "sub": "user123"
            }
            payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
            api_token = f"eyJ.{payload_b64}.signature"
            
            mock_api_response = Mock()
            mock_api_response.ok = True
            mock_api_response.status_code = 200
            mock_api_response.headers = {"Content-Type": "application/json"}
            mock_api_response.json.return_value = api_token
            mock_get.return_value = mock_api_response
            
            result = auth.authenticate()
            
            assert result is True
            assert auth.cache.access_token == "access_token_123"
            assert auth.cache.refresh_token == "refresh_token_456"
            assert auth.cache.publication_url == "https://company.askdelphi.com"

    def test_get_api_token_uses_cache(self):
        """Test that get_api_token uses cached token if valid."""
        auth = AskDelphiAuth(
            tenant_id="tenant-123",
            project_id="project-456",
            acl_entry_id="acl-789"
        )
        
        # Set cached token
        auth.cache.api_token = "cached_token_123"
        auth.cache.api_token_expiry = time.time() + 3600
        
        token = auth.get_api_token()
        
        assert token == "cached_token_123"

    def test_token_refresh_on_expiry(self):
        """Test that token is refreshed when expired."""
        auth = AskDelphiAuth(
            tenant_id="tenant-123",
            project_id="project-456",
            acl_entry_id="acl-789"
        )
        
        # Set expired token
        auth.cache.api_token = "old_token"
        auth.cache.api_token_expiry = time.time() - 100
        auth.cache.access_token = "access_token"
        auth.cache.refresh_token = "refresh_token"
        auth.cache.publication_url = "https://company.askdelphi.com"
        
        with patch.object(auth, '_refresh_tokens'):
            with patch.object(auth, '_get_api_token'):
                auth.get_api_token()
                auth._refresh_tokens.assert_called_once()


class TestSessionIntegration:
    """Test integration with AskDelphiSession."""

    @patch('askdelphi.session.AskDelphiAuth')
    def test_session_with_cms_url(self, mock_auth_class):
        """Test session initialization with CMS URL."""
        from askdelphi.session import AskDelphiSession
        
        cms_url = "https://company.askdelphi.com/cms/tenant/abc-123/project/def-456/acl/ghi-789/page"
        
        session = AskDelphiSession(
            cms_url=cms_url,
            base_url="https://api.example.com"
        )
        
        assert session.tenant == "abc-123"
        assert session.project_id == "def-456"
        assert session.acl == ["ghi-789"]

    @patch('askdelphi.session.AskDelphiAuth')
    def test_session_uses_auth_manager(self, mock_auth_class):
        """Test that session uses auth manager when available."""
        from askdelphi.session import AskDelphiSession
        
        mock_auth = Mock()
        mock_auth.get_api_token.return_value = "api_token_123"
        mock_auth_class.return_value = mock_auth
        
        session = AskDelphiSession(
            tenant="tenant-123",
            project_id="project-456",
            acl=["acl-789"],
            base_url="https://api.example.com",
            use_auth_cache=True
        )
        
        assert session.auth_manager is not None
