# Vergelijking: Werkende ask-delphi-api Client vs digitalecoach_client

## Topic Creation Payload Vergelijking

### ask-delphi-api (WERKEND)
```python
# Line 759-764 in askdelphi_client.py
body = {
    "topicId": str(uuid.uuid4()),
    "topicTitle": title,
    "topicTypeId": topic_type_id,
    "copyParentTags": copy_parent_tags,
}

return self._request(
    "POST",
    "v4/tenant/{tenantId}/project/{projectId}/acl/{aclEntryId}/topic",
    json_data=body
)
```

### digitalecoach_client (HUIDIGE IMPLEMENTATIE)
```python
# Line 61-68 in src/importer/importer.py
payload = {
    "topicId": topic.id,
    "topicTitle": topic.title,
    "topicTypeId": topic_type_id,
    "topicTypeNamespace": topic_type_namespace,
    "copyParentTags": False,
    "language": "nl-NL",
}
```

## Geïdentificeerde Verschillen

### 1. **Minimale Payload (ask-delphi-api)**
De werkende client stuurt ALLEEN de essentiële velden:
- `topicId`
- `topicTitle`
- `topicTypeId`
- `copyParentTags`

### 2. **Uitgebreide Payload (digitalecoach_client)**
De digitalecoach_client voegt extra velden toe:
- `topicTypeNamespace` ← MOGELIJK PROBLEEM
- `language` ← MOGELIJK PROBLEEM
- `description` (optioneel)
- `tags` (optioneel)
- `parentTopicId` (optioneel)
- `parentTopicRelationTypeId` (optioneel)
- `parentTopicVersionId` (optioneel)

## Hypothese: Wat Gaat Mis

### Scenario 1: Extra Velden Worden Afgewezen
De production API v4 endpoint accepteert ALLEEN:
- topicId
- topicTitle
- topicTypeId
- copyParentTags

Alle andere velden (topicTypeNamespace, language, etc.) kunnen leiden tot validatiefouten.

### Scenario 2: topicTypeNamespace Veroorzaakt Conflict
- ask-delphi-api: Stuurt topicTypeNamespace NIET
- digitalecoach_client: Stuurt topicTypeNamespace WEL
- Production API: Kan dit veld afwijzen of vereisen dat het EXACT overeenkomt

### Scenario 3: Veldnamen Zijn Onjuist
Mogelijke naamverschillen:
- `topicTypeId` vs `topicTypeKey`
- `topicTitle` vs `title`
- `copyParentTags` vs `copyParentTags`

## Aanbevolen Fixes

### Fix 1: Minimale Payload Testen
Verwijder alle extra velden en test met ALLEEN:
```python
payload = {
    "topicId": topic.id,
    "topicTitle": topic.title,
    "topicTypeId": topic_type_id,
    "copyParentTags": False,
}
```

### Fix 2: Stap-voor-Stap Velden Toevoegen
1. Start met minimale payload
2. Voeg `description` toe
3. Voeg `tags` toe
4. Voeg `language` toe
5. Voeg `topicTypeNamespace` toe
6. Voeg parent-velden toe

### Fix 3: Payload Validatie
Voeg logging toe om te zien welke velden de API accepteert/afwijst:
```python
if env_config.DEBUG:
    logger.debug(f"Payload velden: {list(payload.keys())}")
    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
```

## Testing Strategie

1. **Test 1**: Minimale payload (alleen essentiële velden)
2. **Test 2**: Voeg description toe
3. **Test 3**: Voeg tags toe
4. **Test 4**: Voeg language toe
5. **Test 5**: Voeg topicTypeNamespace toe
6. **Test 6**: Voeg parent-velden toe

## Volgende Stap

Implementeer Fix 1 (minimale payload) en test tegen zandbak omgeving.
