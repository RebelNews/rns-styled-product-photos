"""Three small things.

A. A "Clothing" collection (tees, women's tees, long sleeves, hoodies, sweatshirts, hats) so the Clothing menu heading
   stops linking to every product in the store, mugs and books included.
B. Menu: Clothing points at that collection; the empty "Films" item becomes "Film Posters" and points at Posters.
C. Read-only probe for the mug, hat and sticker photo job: asks Printful what mock-up styles exist for one of each and
   saves a sample of each style to results/mockups/. Changes nothing on the store."""
import json, os, time, requests, shop
PUB = 'gid://shopify/Publication/2929601'; POSTERS = 'gid://shopify/Collection/262796279942'; MENU = 'gid://shopify/Menu/14851869'
TYPES = ['Unisex T-Shirt', "Women's T-Shirt", 'Long Sleeve T-Shirt', 'Unisex Hoodie', 'Unisex Sweatshirt', 'Hat']
# ---- A. Clothing collection
cid = None
try:
    c = shop.gql('query{collectionByIdentifier(identifier:{handle:"clothing"}){id}}')['collectionByIdentifier']
    if c: cid = c['id']; print('clothing collection exists', cid)
    else:
        i = {'title': 'Clothing', 'handle': 'clothing', 'sortOrder': 'BEST_SELLING', 'descriptionHtml': '<p>Rebel News T-shirts, hoodies, sweatshirts, long sleeves and hats, printed to order.</p>',
             'ruleSet': {'appliedDisjunctively': True, 'rules': [{'column': 'TYPE', 'relation': 'EQUALS', 'condition': t} for t in TYPES]}}
        try:
            d = shop.gql('mutation($i:CollectionInput!){collectionCreate(input:$i){collection{id handle} userErrors{field message}}}', {'i': i})['collectionCreate']
            if d['userErrors']: raise RuntimeError(str(d['userErrors'])[:200])
            cid = d['collection']['id']; print('clothing collection created (automatic, by product type)', cid, flush=True)
        except Exception as e:
            # Rule-based creation refused on this API version: make it a hand-filled collection and add every live garment and hat.
            print('automatic collection refused (%s); creating a manual one' % str(e)[:120], flush=True)
            i.pop('ruleSet'); d = shop.gql('mutation($c:CollectionCreateInput!){collectionCreate(collection:$c){collection{id} userErrors{field message}}}', {'c': i})['collectionCreate']
            if d['userErrors']: raise RuntimeError(str(d['userErrors'])[:200])
            cid = d['collection']['id']; ids, after = [], None
            while True:
                q = shop.gql('query($a:String){products(first:250,after:$a,query:"status:active"){pageInfo{hasNextPage endCursor} nodes{id productType}}}', {'a': after})['products']
                ids += [n['id'] for n in q['nodes'] if n['productType'] in TYPES]
                if not q['pageInfo']['hasNextPage']: break
                after = q['pageInfo']['endCursor']
            for k in range(0, len(ids), 20):
                shop.gql('mutation{' + ' '.join('m%d:productUpdate(product:{id:"%s",collectionsToJoin:["%s"]}){userErrors{message}}' % (n, x, cid) for n, x in enumerate(ids[k:k + 20])) + '}')
            print('clothing collection created (manual) with', len(ids), 'products', cid, flush=True)
        p = shop.gql('mutation($id:ID!,$in:[PublicationInput!]!){publishablePublish(id:$id,input:$in){userErrors{field message}}}', {'id': cid, 'in': [{'publicationId': PUB}]})['publishablePublish']
        print('published to Online Store' if not p['userErrors'] else 'publish userErrors %s' % p['userErrors'][:2])
except Exception as e: print('clothing collection ERROR', type(e).__name__, str(e)[:300])
# ---- B. Menu
try:
    m = shop.gql('query{menu(id:"%s"){id title handle items{id title type url resourceId tags items{id title type url resourceId tags items{id title type url resourceId tags}}}}}' % MENU)['menu']
    changed = []
    def fix(it, top):
        o = {'id': it['id'], 'title': it['title'], 'type': it['type'], 'url': it['url'], 'resourceId': it['resourceId'], 'tags': it.get('tags') or [], 'items': [fix(x, False) for x in it.get('items') or []]}
        if top and it['title'] == 'Clothing' and cid and it['resourceId'] != cid: o.update(resourceId=cid, url='/collections/clothing', type='COLLECTION'); changed.append('Clothing -> /collections/clothing')
        if not top and it['title'] == 'Films' and (it['url'] or '').endswith('/collections/films'): o.update(title='Film Posters', resourceId=POSTERS, url='/collections/art', type='COLLECTION'); changed.append('Films -> Film Posters (/collections/art)')
        if o['resourceId']: o.pop('url')
        return o
    items = [fix(x, True) for x in m['items']]
    if changed:
        d = shop.gql('mutation($id:ID!,$t:String!,$h:String!,$i:[MenuItemUpdateInput!]!){menuUpdate(id:$id,title:$t,handle:$h,items:$i){menu{id} userErrors{field message}}}', {'id': m['id'], 't': m['title'], 'h': m['handle'], 'i': items})['menuUpdate']
        print('menu', 'updated: ' + '; '.join(changed) if not d['userErrors'] else 'NOT updated %s' % d['userErrors'][:3], flush=True)
    else: print('menu: nothing to change')
except Exception as e: print('menu ERROR', type(e).__name__, str(e)[:300])
# ---- C. Mock-up probe (read-only)
os.makedirs('results/mockups', exist_ok=True)
for kind, pid in (('mug', '15499176083590'), ('hat', '6880348930182'), ('sticker', '15497901408390')):
    try:
        c, j = shop.pf('/sync/products/@' + pid)
        if c != 200: print(kind, pid, 'no sync product', c); continue
        sv = next((v for v in j['result']['sync_variants'] if v.get('synced')), None)
        if not sv: print(kind, pid, 'no synced variant'); continue
        prod = sv['product']['product_id']; files = [(f['type'], bool(f.get('url')), f.get('width'), f.get('height')) for f in sv['files']]
        c, pj = shop.pf('/mockup-generator/printfiles/%s' % prod); r = pj['result']; vp = next((x['placements'] for x in r['variant_printfiles'] if x['variant_id'] == sv['variant_id']), {})
        print(kind, pid, '| printful product', prod, sv['product'].get('name'), '| files', files, '| placements', vp, '| option groups', r.get('option_groups'), '| options', r.get('options'), flush=True)
        f = next((f for f in sv['files'] if f['type'] != 'preview' and (f.get('url') or f.get('preview_url'))), None)
        if not f: print(kind, 'no usable print file'); continue
        pl = f['type'] if f['type'] in vp else next(iter(vp), 'default'); area = next((x for x in r['printfiles'] if x['printfile_id'] == vp.get(pl)), None)
        if not area: print(kind, 'no print area for', pl); continue
        w = area['width']; h = round(f['height'] * w / f['width']) if f.get('width') else area['height']
        if h > area['height']: h = area['height']; w = round(f['width'] * h / f['height'])
        for grp in (r.get('option_groups') or [None])[:6]:
            body = {'variant_ids': [sv['variant_id']], 'format': 'png', 'files': [{'placement': pl, 'image_url': f.get('url') or f['preview_url'], 'position': {'area_width': area['width'], 'area_height': area['height'], 'width': w, 'height': h, 'top': (area['height'] - h) // 2, 'left': (area['width'] - w) // 2}}]}
            if grp: body['option_groups'] = [grp]
            time.sleep(14); c, t = shop.pf('/mockup-generator/create-task/%s' % prod, 'POST', json=body)
            if c != 200: print(kind, grp, 'task failed', c, str(t)[:140]); continue
            for _ in range(40):
                time.sleep(6); c, s = shop.pf('/mockup-generator/task?task_key=' + t['result']['task_key']); st = (s.get('result') or {}).get('status')
                if st != 'pending': break
            ms = (s.get('result') or {}).get('mockups') or []; urls = [m.get('mockup_url') for m in ms if m.get('mockup_url')] + [e.get('url') for m in ms for e in (m.get('extra') or []) if e.get('url')]
            print(kind, 'style', grp, '->', st, len(urls), 'images', flush=True)
            if urls:
                img = requests.get(urls[0], timeout=120).content; fn = 'results/mockups/probe_%s_%s.png' % (kind, ''.join(ch for ch in str(grp) if ch.isalnum()) or 'default'); open(fn, 'wb').write(img)
    except Exception as e: print(kind, 'ERROR', type(e).__name__, str(e)[:300], flush=True)
print('DONE')
