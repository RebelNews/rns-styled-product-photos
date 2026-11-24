"""Defund the ABC: put a dark-lettered design on the light colours, then restyle those colours' photos.

Job 014's first draft turned the white DEFUND lettering black but left its black drop shadow, so the letters ran
together. This version (art_light.make_light, checked on a preview by eye):
  * DEFUND lettering and the white Southern Cross stars become near-black (#040707),
  * the lettering's black drop shadow and outline are removed, so the letters read cleanly,
  * the TV, its screen, the antennas, the red "THE ABC" and the transparency are left exactly as they are.

Steps:
  1. build the new art from the dark-blank original (Printful file 1117450807) and save it plus a review sheet,
  2. stop here, changing nothing, unless the draft passes size checks (lettering band, stars and shadow found),
  3. upload it to Shopify Files to get a public address, then add it to the Printful file library,
  4. on every Defund the ABC sync variant whose print file is the old light file (1119089622), swap in the new file,
     keeping the same placement and position, and leave every other variant alone,
  5. restyle the photos of those colours only.
Old light file id for undoing: 1119089622.
"""
import io, os, json, time, requests
import numpy as np
from PIL import Image
import shop, flatstyle
from art_light import make_light

OUT = 'results/015'; os.makedirs(OUT, exist_ok=True)
DARK, OLD_LIGHT = 1117450807, 1119089622
PIDS = ['15493775229062', '15493775458438', '15493775622278', '15493775753350', '15504608919686']


def on(bg, im, w=600):
    im = im.copy(); im.thumbnail((w, w))
    b = Image.new('RGBA', (w, w), bg + (255,)); b.alpha_composite(im, ((w - im.width) // 2, (w - im.height) // 2))
    return b.convert('RGB')


# 1. build
c, j = shop.pf(f'/files/{DARK}'); src = j['result']['url']
orig = Image.open(io.BytesIO(requests.get(src, timeout=180).content)).convert('RGBA')
new, stats = make_light(orig)
print('art', orig.size, json.dumps(stats), flush=True)
path = f'{OUT}/defund-the-abc-light-v2.png'; new.save(path, optimize=True)
cols = [('White', (255, 255, 255)), ('Athletic Heather', (196, 196, 194)), ('Sport Grey', (170, 170, 168)), ('original on Black', (20, 20, 20))]
sheet = Image.new('RGB', (600 * 4, 600), 'white')
for i, (_, cc) in enumerate(cols): sheet.paste(on(cc, new if i < 3 else orig), (600 * i, 0))
sheet.save(f'{OUT}/review_sheet.jpg', quality=88)

# 2. checks
H = orig.height; vis = int((np.array(orig)[..., 3] > 0).sum())
ok = 0.15 * H < stats['band_end'] < 0.40 * H and stats['stars'] > 0 and stats['shadow'] > 0 and stats['letters'] > 0.03 * vis
if not ok: raise SystemExit('draft failed the checks; nothing changed')

# 3. upload: Shopify Files for a public address, then Printful
t = shop.gql('mutation($i:[StagedUploadInput!]!){stagedUploadsCreate(input:$i){stagedTargets{url resourceUrl parameters{name value}} userErrors{message}}}',
             {'i': [{'resource': 'IMAGE', 'filename': 'defund-the-abc-light-v2.png', 'mimeType': 'image/png', 'httpMethod': 'POST'}]})['stagedUploadsCreate']['stagedTargets'][0]
r = requests.post(t['url'], data={p['name']: p['value'] for p in t['parameters']}, files={'file': ('defund-the-abc-light-v2.png', open(path, 'rb'), 'image/png')}, timeout=300)
print('staged upload', r.status_code, flush=True)
fc = shop.gql('mutation($f:[FileCreateInput!]!){fileCreate(files:$f){files{id} userErrors{message}}}', {'f': [{'originalSource': t['resourceUrl'], 'contentType': 'IMAGE', 'alt': 'Defund the ABC art for light garments'}]})['fileCreate']
if fc['userErrors']: raise SystemExit('fileCreate: %s' % fc['userErrors'])
fid = fc['files'][0]['id']; url = None
for _ in range(40):
    time.sleep(6)
    n = shop.gql('query($id:ID!){node(id:$id){... on MediaImage{fileStatus image{url}}}}', {'id': fid})['node']
    if n.get('fileStatus') == 'READY' and n.get('image'): url = n['image']['url']; break
if not url: raise SystemExit('Shopify file not ready; nothing changed in Printful')
c, j = shop.pf('/files', 'POST', json={'url': url, 'filename': 'defund-the-abc-light-v2.png'})
if c != 200: raise SystemExit('Printful upload failed %s %s' % (c, str(j)[:200]))
NEW = j['result']['id']
for _ in range(40):
    c, j = shop.pf(f'/files/{NEW}')
    if (j.get('result') or {}).get('status') == 'ok': break
    time.sleep(6)
print('new Printful file', NEW, j['result'].get('status'), j['result'].get('width'), j['result'].get('height'), flush=True)
if j['result'].get('status') != 'ok': raise SystemExit('Printful file not processed; no variants changed')

# 4. swap the file on the light variants
done = {}
for pid in PIDS:
    c, sp = shop.pf(f'/sync/products/@{pid}')
    if c != 200: print(pid, 'no sync product', c, flush=True); continue
    n_ok = 0
    for sv in sp['result']['sync_variants']:
        fs = [f for f in sv['files'] if f['type'] != 'preview']
        if not any(f['id'] == OLD_LIGHT for f in fs): continue
        files = []
        for f in fs:
            e = {'type': f['type'], 'id': NEW if f['id'] == OLD_LIGHT else f['id']}
            if f.get('position'): e['position'] = f['position']
            files.append(e)
        body = {'variant_id': sv['variant_id'], 'files': files}
        c2, r2 = shop.pf('/sync/variant/%s' % sv['id'], 'PUT', json=body)
        if c2 != 200 and any('position' in e for e in files):
            for e in files: e.pop('position', None)
            c2, r2 = shop.pf('/sync/variant/%s' % sv['id'], 'PUT', json=body)
        print(pid, sv['name'], 'swapped' if c2 == 200 else 'FAILED %s %s' % (c2, str(r2)[:160]), flush=True)
        n_ok += c2 == 200
        time.sleep(1)
    done[pid] = n_ok
print('variants swapped', json.dumps(done), flush=True)

# 5. restyle those colours' photos (colour names read back from Shopify to match exactly)
time.sleep(20)
for pid in PIDS:
    p = shop.gql('query($id:ID!){product(id:$id){variants(first:100){nodes{id selectedOptions{name value}}}}}', {'id': f'gid://shopify/Product/{pid}'})['product']
    c, sp = shop.pf(f'/sync/products/@{pid}')
    ext = {str(sv['external_id']) for sv in sp['result']['sync_variants'] if any(f['id'] == NEW for f in sv['files'])}
    light_cols = sorted({o['value'] for v in p['variants']['nodes'] if v['id'].split('/')[-1] in ext for o in v['selectedOptions'] if o['name'].lower() in ('color', 'colour')})
    if not light_cols: print(pid, 'no colours to restyle'); continue
    try: print(pid, 'restyled', flatstyle.one(pid, set(light_cols), True, False), light_cols, flush=True)
    except Exception as e: print(pid, 'restyle ERROR', type(e).__name__, str(e)[:200], flush=True)
    time.sleep(5)
print('DONE. To undo, put Printful file %d back on these variants.' % OLD_LIGHT)
