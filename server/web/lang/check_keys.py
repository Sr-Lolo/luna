import re, json, os
os.chdir(r'C:\Users\Infinity Tech\Desktop\Mis Cosas\Proyecto Luna\LunaDeck v1.7.55\server\web')

keys = set()
for f in ['index.html','dashboard.html','ayuda.html']:
    txt = open(f,'r',encoding='utf-8').read()
    for m in re.finditer(r'data-i18n(?:-tooltip|-placeholder|-alt|-value)?="([^"]+)"', txt):
        keys.add(m.group(1))
    for m in re.finditer(r"__\('([^']+)'\)", txt):
        keys.add(m.group(1))

print(f'Found {len(keys)} unique data-i18n keys across all HTML')

jsons = {}
for lang in ['en','es','pt']:
    jsons[lang] = json.load(open(f'lang/{lang}.json','r',encoding='utf-8'))
    print(f'  {lang}.json: {len(jsons[lang])} keys')

for lang in ['en','es','pt']:
    missing = [k for k in sorted(keys) if k not in jsons[lang]]
    if missing:
        print(f'\n  MISSING in {lang}.json ({len(missing)}):')
        for k in missing:
            print(f'    {k}')
    else:
        print(f'\n  {lang}.json: ALL keys present')
