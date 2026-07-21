import json, os
for f in ['en.json','es.json','pt.json']:
    raw = open(f,'rb').read()
    has_bom = raw[:3] == b'\xef\xbb\xbf'
    if has_bom:
        raw = raw[3:]
        open(f,'wb').write(raw)
        print(f'{f}: BOM stripped')
    try:
        json.loads(raw.decode('utf-8'))
        print(f'{f}: VALID')
    except json.JSONDecodeError as e:
        print(f'{f}: INVALID - {e}')
