# Vul je credentials in en voer dit script uit
$env:ASKDELPHI_BASE_URL='https://your-company.askdelphi.com/api'
$env:ASKDELPHI_CMS_URL='https://company.askdelphi.com/cms/tenant/xxx/project/yyy/acl/zzz/page'
$env:ASKDELPHI_PORTAL_CODE='ABC123-XYZ789'
$env:ASKDELPHI_NT_ACCOUNT='your-username'
$env:USE_AUTH_CACHE='true'

python main.py --input procesbeschrijving/process_sanering.json --schema procesbeschrijving/process_schema.json
