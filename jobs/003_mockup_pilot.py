"""Pilot, one product: ask Printful for flat front mock-ups of every colour of one tee and save them under results/mockups/.
Changes nothing in Shopify or Printful's product data. The saved images are for checking quality before a full run."""
import os, re, json, time, requests, shop
PID = '15491039887494'  # Silent Night? Not on Our Watch. Unisex T-Shirt
c, j = shop.pf(f'/sync/products/@{PID}')
if c != 200: raise SystemExit(f'sync product lookup failed {c} {str(j)[:200]}')
svs = j['result']['sync_variants']
reps = {}
for v in svs:
    m = re.search(r'\(([^()]*?)\s*/\s*[^()/]+\)\s*$', v['product']['name']) or re.search(r'-\s*([^/]+?)\s*/', v.get('name') or '')
    col = (m.group(1) if m else 'unknown').strip()
    reps.setdefault(col, v)
print('colours', list(reps), flush=True)
v0 = next(iter(reps.values())); prod = v0['product']['product_id']
f0 = next((f for f in v0['files'] if f['type'] in ('default', 'front')), v0['files'][0])
print('print file keys', sorted(f0), '| has url', bool(f0.get('url')), '| size', f0.get('width'), f0.get('height'), '| dpi', f0.get('dpi'), flush=True)
c, pfj = shop.pf(f'/mockup-generator/printfiles/{prod}'); r = pfj['result']
print('option_groups', r.get('option_groups'), '| options', r.get('options'), flush=True)
sizes = {p['printfile_id']: p for p in r['printfiles']}
vp = {x['variant_id']: x['placements'] for x in r['variant_printfiles']}
area = sizes[vp[v0['variant_id']]['front']]
# one colour can have its own art (light and dark versions), so group colours by print file
groups = {}
for col, v in reps.items():
    f = next((f for f in v['files'] if f['type'] in ('default', 'front')), v['files'][0])
    groups.setdefault(f['id'], {'file': f, 'vars': {}})['vars'][v['variant_id']] = col
os.makedirs('results/mockups', exist_ok=True)
og = r.get('option_groups') or []
want = [g for g in og if g.lower() in ('flat', 'ghost')] or og[:1]
for fid, g in groups.items():
    f = g['file']; url = f.get('url') or f['preview_url']
    w = area['width']; h = round(f['height'] * w / f['width'])
    if h > area['height']: h = area['height']; w = round(f['width'] * h / f['height'])
    body = {'variant_ids': list(g['vars']), 'format': 'png', 'files': [{'placement': 'front', 'image_url': url, 'position': {'area_width': area['width'], 'area_height': area['height'], 'width': w, 'height': h, 'top': 0, 'left': (area['width'] - w) // 2}}]}
    if want: body['option_groups'] = want
    if r.get('options') and 'Front' in r['options']: body['options'] = ['Front']
    c, t = shop.pf(f'/mockup-generator/create-task/{prod}', 'POST', json=body)
    print('create task', c, str(t.get('result') or t)[:200], flush=True)
    if c != 200: continue
    key = t['result']['task_key']
    for _ in range(40):
        time.sleep(8); c, s = shop.pf(f'/mockup-generator/task?task_key={key}'); st = (s.get('result') or {}).get('status')
        if st != 'pending': break
    print('task', st, str((s.get('result') or {}).get('error') or '')[:200], flush=True)
    for mk in (s.get('result') or {}).get('mockups') or []:
        urls = [('main', mk.get('mockup_url'))] + [(e.get('title') or e.get('option') or 'extra', e.get('url')) for e in mk.get('extra') or []]
        for vid in mk.get('variant_ids') or []:
            col = g['vars'].get(vid)
            if not col: continue
            for title, u in urls[:3]:
                if not u: continue
                name = re.sub(r'[^a-z0-9]+', '-', f'{col}-{title}'.lower()).strip('-')
                img = requests.get(u, timeout=120).content
                open(f'results/mockups/{PID}_{name}.png', 'wb').write(img)
                print('saved', name, len(img), flush=True)
    time.sleep(30)
