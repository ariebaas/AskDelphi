# Vul je credentials in en voer dit script uit
$env:ASKDELPHI_BASE_URL='https://your-company.askdelphi.com/api'
$env:ASKDELPHI_API_KEY='your-api-key'
$env:ASKDELPHI_TENANT='your-tenant'
$env:ASKDELPHI_NT_ACCOUNT='your-username'
$env:ASKDELPHI_ACL='your-acl'
$env:ASKDELPHI_PROJECT_ID='your-project'
$env:USE_AUTH_CACHE='false'

python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
