"""For each product: get a flat front mock-up of every colour from Printful, place it on a Rebel News background,
and swap it in place for the image that colour's variants point at. Nothing is deleted."""
import io, re, time, requests, shop, styled
import numpy as np
from PIL import Image
def has_art(rgba):
    """False when the mock-up is a blank garment: almost no pixels differ from the garment's own colour."""
    a = np.asarray(rgba.resize((400, 400))); m = a[..., 3] > 200
    if m.sum() < 500: return False
    px = a[..., :3][m].astype(np.int32); q = px // 16; key = q[:, 0] * 256 + q[:, 1] * 16 + q[:, 2]
    vals, cnt = np.unique(key, return_counts=True); base = px[key == vals[cnt.argmax()]].mean(0)
    return float((np.abs(px - base).sum(1) > 150).mean()) >= 0.006
Q = '''query($id:ID!){product(id:$id){title productType collections(first:40){nodes{handle}}
 variants(first:100){nodes{id selectedOptions{name value} media(first:1){nodes{id}}}}}}'''
def staged(jpg):
    t = shop.gql('mutation($i:[StagedUploadInput!]!){stagedUploadsCreate(input:$i){stagedTargets{url resourceUrl parameters{name value}} userErrors{message}}}', {'i': [{'resource': 'IMAGE', 'filename': 'a.jpg', 'mimeType': 'image/jpeg', 'httpMethod': 'POST'}]})['stagedUploadsCreate']['stagedTargets'][0]
    r = requests.post(t['url'], data={p['name']: p['value'] for p in t['parameters']}, files={'file': ('a.jpg', jpg, 'image/jpeg')}, timeout=120)
    if r.status_code not in (200, 201, 204): raise RuntimeError(f'staged upload HTTP {r.status_code}')
    return t['resourceUrl']
def one(pid):
    p = shop.gql(Q, {'id': f'gid://shopify/Product/{pid}'})['product']
    cols = [c['handle'] for c in p['collections']['nodes']]
    colour_of, media_of, users = {}, {}, {}
    for v in p['variants']['nodes']:
        o = next((x['value'] for x in v['selectedOptions'] if x['name'].lower() in ('color', 'colour')), None)
        if o is None: continue
        n = v['id'].split('/')[-1]; colour_of[n] = o
        m = (v['media']['nodes'] or [{}])[0].get('id')
        if m: media_of.setdefault(o, set()).add(m); users.setdefault(m, set()).add(o)
    c, j = shop.pf(f'/sync/products/@{pid}')
    if c != 200: print(pid, 'no sync product', c); return 0
    reps = {}
    for sv in j['result']['sync_variants']:
        col = colour_of.get(str(sv.get('external_id')))
        if col and sv.get('synced') and col not in reps: reps[col] = sv
    if not reps: print(pid, 'no colours matched'); return 0
    missing = sorted(set(colour_of.values()) - set(reps))
    if missing:
        svs = j['result']['sync_variants']
        print(pid, 'colours with no synced Printful variant:', missing, '| sync variants', len(svs), '| synced', sum(1 for x in svs if x.get('synced')), '| shopify variants', len(colour_of), '| sample names', [x.get('name') for x in svs if not x.get('synced')][:3], flush=True)
    prod = next(iter(reps.values()))['product']['product_id']
    c, pj = shop.pf(f'/mockup-generator/printfiles/{prod}'); r = pj['result']
    sizes = {x['printfile_id']: x for x in r['printfiles']}; vp = {x['variant_id']: x['placements'] for x in r['variant_printfiles']}
    og = r.get('option_groups') or []; want = [g for g in og if g == 'Flat'] or [g for g in og if g == 'Ghost'] or og[:1]
    groups = {}
    for col, sv in reps.items():
        f = next((f for f in sv['files'] if f['type'] in ('default', 'front')), None) or next((f for f in sv['files'] if f['type'] != 'preview'), None)
        print(pid, col, 'print file', (f or {}).get('id'), (f or {}).get('type'), (f or {}).get('filename'), 'url' if (f or {}).get('url') else 'preview-only', '| all types', [x['type'] for x in sv['files']], flush=True)
        if f and (f.get('url') or f.get('preview_url')): groups.setdefault(f['id'], {'f': f, 'vars': {}})['vars'][sv['variant_id']] = col
    imgs = {}
    for g in groups.values():
        f = g['f']; area = sizes[vp[next(iter(g['vars']))]['front']]
        w = area['width']; h = round(f['height'] * w / f['width'])
        if h > area['height']: h = area['height']; w = round(f['width'] * h / f['height'])
        body = {'variant_ids': list(g['vars']), 'format': 'png', 'option_groups': want, 'files': [{'placement': 'front', 'image_url': f.get('url') or f['preview_url'], 'position': {'area_width': area['width'], 'area_height': area['height'], 'width': w, 'height': h, 'top': 0, 'left': (area['width'] - w) // 2}}]}
        c, t = shop.pf(f'/mockup-generator/create-task/{prod}', 'POST', json=body)
        if c != 200: print(pid, 'task failed', c, str(t)[:160], list(g['vars'].values())); continue
        for _ in range(45):
            time.sleep(8); c, s = shop.pf('/mockup-generator/task?task_key=' + t['result']['task_key']); st = (s.get('result') or {}).get('status')
            if st != 'pending': break
        if st != 'completed': print(pid, 'task', st, str((s.get('result') or {}).get('error'))[:160], list(g['vars'].values()), flush=True)
        for mk in (s.get('result') or {}).get('mockups') or []:
            if mk.get('placement') not in (None, 'front'): continue
            for vid in mk.get('variant_ids') or []:
                if vid in g['vars'] and mk.get('mockup_url'): imgs[g['vars'][vid]] = mk['mockup_url']
        time.sleep(12)
    used, files = {}, []
    if set(reps) - set(imgs): print(pid, 'no mock-up returned for', sorted(set(reps) - set(imgs)), flush=True)
    theme = styled.theme_for(cols, p['productType'], p['title'])
    for col, url in imgs.items():
        ms = media_of.get(col) or set()
        if len(ms) != 1 or len(users[next(iter(ms))]) != 1: print(pid, 'skip colour', col, 'media not one-to-one'); continue
        rgba = Image.open(io.BytesIO(requests.get(url, timeout=120).content)).convert('RGBA')
        if not has_art(rgba): print(pid, 'skip colour', col, 'mock-up came back blank'); continue
        bg = styled.pick_bg(styled.garment_lab(rgba), theme, used); used[bg] = used.get(bg, 0) + 1
        buf = io.BytesIO(); styled.compose(rgba, bg).save(buf, 'JPEG', quality=88, optimize=True)
        files.append({'id': next(iter(ms)), 'originalSource': staged(buf.getvalue()), 'alt': f"{p['title']} - {col}"})
        print(pid, col, '->', bg, flush=True)
    if not files: return 0
    d = shop.gql('mutation($f:[FileUpdateInput!]!){fileUpdate(files:$f){files{id} userErrors{field message code}}}', {'f': files})['fileUpdate']
    if d['userErrors']: print(pid, 'userErrors', d['userErrors'][:3])
    return len(d['files'] or [])
def run(pids, minutes=85):
    t0 = time.time(); total = 0; errs = 0
    for i, pid in enumerate(pids):
        if time.time() - t0 > minutes * 60: print('time budget reached; not done:', pids[i:]); break
        try: n = one(pid); total += n; print(pid, 'swapped', n, flush=True)
        except Exception as e:
            errs += 1; print(pid, 'ERROR', type(e).__name__, str(e)[:200], flush=True)
            if errs >= 3: print('stopping after 3 errors; not done:', pids[i + 1:]); break
    print('TOTAL swapped', total, 'errors', errs)
