#!/usr/bin/env python3
"""Debug script om API connectivity en endpoints te testen."""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

import requests

load_dotenv()

def print_section(title):
    """Print een sectie header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def check_token_cache():
    """Check wat in .askdelphi_tokens.json staat."""
    print_section("1. TOKEN CACHE CONTROLE")
    
    cache_file = Path(".askdelphi_tokens.json")
    if not cache_file.exists():
        print("❌ .askdelphi_tokens.json bestaat niet")
        print("   Voer eerst authenticatie uit met USE_AUTH_CACHE=true")
        return None
    
    try:
        data = json.loads(cache_file.read_text())
        print("✅ .askdelphi_tokens.json gevonden")
        print(f"\n  Publication URL: {data.get('publication_url')}")
        print(f"  Access Token: {data.get('access_token', 'GEEN')[:30]}...")
        print(f"  Refresh Token: {data.get('refresh_token', 'GEEN')[:30]}...")
        return data
    except Exception as e:
        print(f"❌ Kon .askdelphi_tokens.json niet lezen: {e}")
        return None

def check_env_vars():
    """Check environment variabelen."""
    print_section("2. ENVIRONMENT VARIABELEN")
    
    vars_to_check = [
        'ASKDELPHI_BASE_URL',
        'ASKDELPHI_API_KEY',
        'ASKDELPHI_TENANT',
        'ASKDELPHI_NT_ACCOUNT',
        'ASKDELPHI_ACL',
        'ASKDELPHI_PROJECT_ID',
        'USE_AUTH_CACHE',
        'DEBUG'
    ]
    
    for var in vars_to_check:
        value = os.getenv(var, 'NIET INGESTELD')
        if var in ['ASKDELPHI_API_KEY', 'ASKDELPHI_NT_ACCOUNT']:
            display = f"{value[:10]}..." if len(value) > 10 else value
        else:
            display = value
        print(f"  {var}: {display}")

def test_api_endpoint(base_url, token, endpoint, method="GET"):
    """Test een API endpoint."""
    url = f"{base_url}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    
    print(f"\n  {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json={}, timeout=10)
        
        print(f"  Status: {response.status_code} {response.reason}")
        
        if response.status_code == 404:
            print(f"  ❌ ENDPOINT NIET GEVONDEN (404)")
            print(f"     Dit kan betekenen:")
            print(f"     - Base URL is incorrect")
            print(f"     - Endpoint path is incorrect")
            print(f"     - API versie is anders")
        elif response.status_code == 401:
            print(f"  ❌ UNAUTHORIZED (401)")
            print(f"     Token is ongeldig of verlopen")
        elif response.status_code == 200 or response.status_code == 201:
            print(f"  ✅ SUCCES")
        else:
            print(f"  ⚠️  Onverwachte status")
        
        if response.text:
            try:
                body = response.json()
                print(f"  Response: {json.dumps(body, indent=4)[:200]}...")
            except:
                print(f"  Response: {response.text[:200]}...")
        
        return response.status_code
    except requests.exceptions.Timeout:
        print(f"  ❌ TIMEOUT - Server antwoordt niet")
    except requests.exceptions.ConnectionError as e:
        print(f"  ❌ CONNECTION ERROR - Kan niet verbinden")
        print(f"     {str(e)[:100]}")
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)[:100]}")

def test_endpoints(base_url, token):
    """Test verschillende endpoints."""
    print_section("3. ENDPOINT TESTS")
    
    endpoints = [
        ("/topics", "GET"),
        ("/export", "GET"),
        ("/projects", "GET"),
    ]
    
    print(f"\nBase URL: {base_url}")
    
    for endpoint, method in endpoints:
        test_api_endpoint(base_url, token, endpoint, method)

def main():
    """Voer alle diagnostische checks uit."""
    print("\n" + "="*70)
    print("  DIGITALECOACH CLIENT - API DEBUG SCRIPT")
    print("="*70)
    
    # Check token cache
    cache_data = check_token_cache()
    if not cache_data:
        print("\n❌ Kan niet doorgaan zonder token cache")
        print("   Voer eerst uit met USE_AUTH_CACHE=true")
        sys.exit(1)
    
    # Check env vars
    check_env_vars()
    
    # Get base URL
    base_url = cache_data.get('publication_url')
    token = cache_data.get('access_token')
    
    if not base_url or not token:
        print("\n❌ Geen publication_url of access_token in cache")
        sys.exit(1)
    
    # Test endpoints
    test_endpoints(base_url, token)
    
    # Summary
    print_section("4. SAMENVATTING")
    print(f"\nBase URL die wordt gebruikt: {base_url}")
    print(f"\nAls endpoints 404 geven:")
    print(f"  1. Check of base URL correct is")
    print(f"  2. Controleer of endpoints /topics, /export, etc. bestaan")
    print(f"  3. Zet DEBUG=true voor meer details")
    print(f"\nAls endpoints 401 geven:")
    print(f"  1. Token is ongeldig of verlopen")
    print(f"  2. Verwijder .askdelphi_tokens.json en authenticeer opnieuw")

if __name__ == "__main__":
    main()
