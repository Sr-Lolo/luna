import json, sys
for f in ['en.json','es.json','pt.json']:
    raw = open(f,'rb').read()
    bom = raw[:3] == b'\xef\xbb\xbf'
    try:
        json.loads(raw.decode('utf-8'))
        print(f'{f}: VALID (BOM={bom})')
    except json.JSONDecodeError as e:
        print(f'{f}: INVALID - {e} (BOM={bom})')
