# HTTP 401 Analysis: digitalecoach_client vs ask-delphi-api

## Problem
digitalecoach_client receives HTTP 401 (Unauthorized) when creating topics on production API.
ask-delphi-api works correctly with the same API.

## Key Differences Found

### 1. **Authentication Flow**

#### ask-delphi-api (WORKING)
```python
# Step 1: Exchange portal code for access tokens
url = f"{PORTAL_SERVER}/api/session/registration?sessionCode={code}"
response = session.get(url, headers=headers, timeout=30)
# Gets: accessToken, refreshToken, url (publication_url)

# Step 2: Get API token using access token
url = f"{publication_url}/api/token/EditingApiToken"
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(url, headers=headers, timeout=30)
# Gets: API token (JWT)

# Step 3: Use API token for all API calls
headers = {"Authorization": f"Bearer {api_token}"}
```

#### digitalecoach_client (BROKEN)
```python
# Uses AskDelphiAuth which should follow same flow
# BUT: May be using wrong token or missing publication_url extraction
```

### 2. **Critical Issue: Publication URL Extraction**

#### ask-delphi-api (CORRECT)
```python
# Line 365-368 in askdelphi_client.py
full_url = data.get("url", "")  # e.g., "https://company.askdelphi.com/nl-NL/Project/page/eyJ..."
if full_url:
    parsed = urlparse(full_url)
    self._publication_url = f"{parsed.scheme}://{parsed.netloc}"  # Extract ONLY base URL
    # Result: "https://company.askdelphi.com"
```

#### digitalecoach_client (CHECK)
```python
# In src/api_client/auth.py line 374-376
full_url = data.get("url", "")
if full_url:
    parsed = urlparse(full_url)
    self.cache.publication_url = f"{parsed.scheme}://{parsed.netloc}"
# LOOKS CORRECT - but verify it's being used
```

### 3. **API Token Retrieval**

#### ask-delphi-api (WORKING)
```python
# Line 464-474
url = f"{self._publication_url}/api/token/EditingApiToken"
headers = {
    "Authorization": f"Bearer {self._access_token}",
    "Accept": "application/json",
    "User-Agent": "AskDelphi-Python-Client/1.0"
}
response = requests.get(url, headers=headers, timeout=30)
```

#### digitalecoach_client (CHECK)
```python
# In src/api_client/auth.py line 509-519
url = f"{self.cache.publication_url}/api/token/EditingApiToken"
headers = {
    "Authorization": f"Bearer {self.cache.access_token}",
    "Accept": "application/json",
    "User-Agent": "AskDelphi-Python-Client/1.0"
}
response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
# LOOKS CORRECT
```

### 4. **API Request Headers**

#### ask-delphi-api (WORKING)
```python
# Line 636-641
headers = {
    "Authorization": f"Bearer {token}",  # API token (JWT)
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "AskDelphi-Python-Client/1.0"
}
```

#### digitalecoach_client (POTENTIAL ISSUE)
```python
# In src/api_client/session.py line 155-165
if self.auth_manager:
    token = self.auth_manager.get_api_token()
    headers = {
        "Authorization": f"Bearer {token}",
    }
else:
    headers = {
        "Authorization": f"Bearer {self.session_token}",
        "X-API-Key": self.api_key,
    }
# MISSING: Content-Type, Accept headers
```

### 5. **Request Headers Completeness**

#### ask-delphi-api
```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "AskDelphi-Python-Client/1.0"
}
```

#### digitalecoach_client
```python
headers = {
    "Authorization": f"Bearer {token}",
}
# MISSING: Content-Type, Accept, User-Agent
```

## Root Cause Analysis

### Most Likely Issues (in order of probability):

1. **Missing Content-Type Header** ⚠️ HIGH PRIORITY
   - ask-delphi-api always includes: `"Content-Type": "application/json"`
   - digitalecoach_client may not be sending this
   - API might reject requests without proper Content-Type

2. **Missing Accept Header** ⚠️ MEDIUM PRIORITY
   - ask-delphi-api includes: `"Accept": "application/json"`
   - digitalecoach_client missing this
   - Could cause response parsing issues

3. **Token Caching Issue** ⚠️ MEDIUM PRIORITY
   - Verify that `get_api_token()` is returning valid JWT token
   - Check if token is being cached correctly
   - Verify token hasn't expired

4. **Publication URL Issue** ⚠️ LOW PRIORITY
   - Verify publication_url is being extracted correctly
   - Check if it's being used for token endpoint

## Recommended Fixes

### Fix 1: Add Missing Headers
Update `src/api_client/session.py` line 155-165 to include all required headers:
```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "AskDelphi-Python-Client/1.0"
}
```

### Fix 2: Add Debug Logging
Add logging to verify:
- Token is valid JWT (starts with "eyJ")
- Publication URL is correct base URL
- Headers are complete before request

### Fix 3: Verify Token Expiry
Ensure token refresh logic is working:
- Check if cached token is expired
- Verify refresh token is being used correctly

## Testing Strategy

1. Enable DEBUG mode
2. Check logs for:
   - Authorization header value (first 30 chars)
   - Content-Type header
   - Accept header
   - Response status and body
3. Compare with ask-delphi-api working example
4. Verify token format (should start with "eyJ")
