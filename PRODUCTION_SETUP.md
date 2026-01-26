# Production Setup Guide

## Overview

The `digitalecoach_client` is now configured for production use with full authentication support. This guide explains how to set up and use the client against the production AskDelphi API.

## Prerequisites

1. **Python 3.8+** installed
2. **Portal Code** from AskDelphi (one-time use code for authentication)
3. **CMS URL** or individual credentials (tenant, project, ACL IDs)
4. **.env file** configured with production credentials

## Configuration

### Step 1: Create .env File

Create a `.env` file in the project root with your production credentials:

```env
# Production API Configuration
ASKDELPHI_CMS_URL=https://xxx.askdelphi.com/cms/tenant/{TENANT_ID}/project/{PROJECT_ID}/acl/{ACL_ENTRY_ID}/...
# OR use individual parameters:
ASKDELPHI_TENANT_ID=your-tenant-id
ASKDELPHI_PROJECT_ID=your-project-id
ASKDELPHI_ACL_ENTRY_ID=your-acl-id

# Portal Authentication
ASKDELPHI_PORTAL_CODE=ABC123-XYZ789

# Optional
DEBUG=true
USE_AUTH_CACHE=true
```

### Step 2: Prepare Input JSON

Prepare your topics JSON file in one of two formats:

**Format 1: Process Structure** (recommended)
```json
{
  "process": {
    "id": "uuid",
    "title": "Process Title",
    "description": "Description",
    "topic_type_id": "uuid",
    "topic_type_title": "process",
    "tags": ["tag1", "tag2"],
    "tasks": [
      {
        "id": "uuid",
        "title": "Task Title",
        "topic_type_id": "uuid",
        "steps": [...]
      }
    ]
  }
}
```

**Format 2: Topics Dictionary**
```json
{
  "topics": {
    "topic-id-1": {
      "title": "Topic Title",
      "topic_type_id": "uuid",
      "tags": ["tag1"]
    }
  }
}
```

## Usage

### Upload to Production API

```bash
# Dry-run (show what would be uploaded)
python upload_topics.py procesbeschrijving/process_sanering_uuid.json --production --dry-run

# Upload with confirmation
python upload_topics.py procesbeschrijving/process_sanering_uuid.json --production

# Upload without confirmation
python upload_topics.py procesbeschrijving/process_sanering_uuid.json --production --force
```

### Upload to Mock Server (Testing)

```bash
# Dry-run against mock server
python upload_topics.py procesbeschrijving/process_sanering_uuid.json --mock-server --dry-run

# Upload to mock server
python upload_topics.py procesbeschrijving/process_sanering_uuid.json --mock-server --force
```

### Additional Options

```bash
# Compare with original file
python upload_topics.py input.json --original original.json --production

# Enable verbose logging
python upload_topics.py input.json --production -v

# Set rate limit between API calls (milliseconds)
python upload_topics.py input.json --production --rate-limit 500
```

## Authentication Flow

### First Run (Portal Code Required)

1. Script requests portal code from .env
2. Exchanges portal code for access tokens via portal
3. Extracts publication URL from portal response
4. Gets editing API token using access token
5. Caches tokens in `.askdelphi_tokens.json`
6. Uses cached tokens for subsequent requests

### Subsequent Runs (Cached Tokens)

1. Script loads cached tokens from `.askdelphi_tokens.json`
2. Validates token expiry
3. Refreshes token if needed
4. Uses valid token for API requests

### Token Refresh

Tokens are automatically refreshed when:
- Token expires (default 1 hour)
- Token is within 5 minutes of expiry
- Manual refresh can be triggered by deleting `.askdelphi_tokens.json`

## Topic Creation Payload

### Production API (v4)

Minimal payload for production API:

```json
{
  "topicId": "uuid",
  "topicTitle": "Topic Title",
  "topicTypeId": "uuid",
  "copyParentTags": false
}
```

Optional fields:
- `description`: Topic description
- `tags`: Array of tags
- `parentTopicId`: Parent topic ID
- `parentTopicRelationTypeId`: Relationship type to parent
- `parentTopicVersionId`: Parent topic version

### Mock Server

Extended payload for mock server testing:

```json
{
  "id": "uuid",
  "title": "Topic Title",
  "topicTypeKey": "uuid",
  "topicTypeNamespace": "AskDelphi.DigitalCoach",
  "metadata": {},
  "tags": []
}
```

## Troubleshooting

### Authentication Failures

**Error: "Portal code exchange failed"**
- Portal code may be invalid or already used
- Portal codes are one-time use only
- Get a fresh code from the Mobile tab in AskDelphi

**Error: "No access token available"**
- Delete `.askdelphi_tokens.json` and try again
- Ensure ASKDELPHI_PORTAL_CODE is set in .env

### Topic Creation Failures

**Error: "Invalid topic type"**
- Topic type ID not recognized by production API
- Verify topic_type_id is valid for your environment

**Error: "Validation failed (ERR20001)"**
- Check required fields in payload
- Ensure topicTypeId is valid
- Verify topicTypeNamespace is correct

### Connection Issues

**Error: "Failed to resolve"**
- Check internet connection
- Verify ASKDELPHI_BASE_URL is correct
- Check firewall/proxy settings

## Best Practices

1. **Always use dry-run first**: Test with `--dry-run` before uploading
2. **Enable verbose logging**: Use `-v` flag for debugging
3. **Cache tokens**: Use `USE_AUTH_CACHE=true` to avoid repeated authentication
4. **Rate limiting**: Use `--rate-limit` to avoid overwhelming the API
5. **Backup before upload**: Create backups of existing content before uploading changes

## Files

- `upload_topics.py` - Main upload script
- `.env` - Configuration file (not in git)
- `.askdelphi_tokens.json` - Token cache (auto-generated, not in git)
- `procesbeschrijving/process_sanering_uuid.json` - Example input file

## Support

For issues or questions:
1. Check debug logs: `cat askdelphi_debug.log`
2. Enable verbose mode: `python upload_topics.py ... -v`
3. Review this guide for troubleshooting
4. Check GitHub issues for similar problems
