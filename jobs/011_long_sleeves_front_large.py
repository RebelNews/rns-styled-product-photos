"""Long sleeves for the 41 designs job 010 skipped because their tees print on both 'default' and 'front_large'
(listed in jobs/011_tees.json). Those are still one front print: some colours use the standard front file and others the
large front file, never both on one shirt. Job 010's rule treated the mix as a second placement; this job checks each
tee colour instead, and only skips a design if one colour prints in more than one place or anywhere other than the front.

Everything else is job 010 unchanged: each long-sleeve colour is linked with the same print file and placement as that
colour of the tee, the product is created hidden, and each colour gets a flat styled photo for review before publishing.
The job stops starting new designs after 5 hours 20 minutes."""
import json, os, re, time, shop, flatstyle
T_START = time.time(); BUDGET = 19200
PUB = 'gid://shopify/Publication/2929601'
PF_LOC = 'gid://shopify/Location/33058652205'                   # Printful fulfilment location
TEES = json.load(open(os.path.join(os.path.dirname(__file__), '011_tees.json')))
EXCLUDE = re.compile(r'tim horton|built not stolen|still no proof|pocket', re.I)
LS_EXAMPLE = '6947730915462'                                    # True Story Nativity Unisex Long Sleeve Shirt, for the Printful blank
SIZES = ['S', 'M', 'L', 'XL', '2XL']; PRICE = {'S': '45.00', 'M': '45.00', 'L': '45.00', 'XL': '45.00', '2XL': '48.00'}
SKIP_COLL = {'all', 'unisex', 'unisex-t-shirt', 'mens-all', 'mens-t-shirts', 'best-sellers', 'featured', 'hall-of-fame', 'gifts-under-40', 'add-ons',
             'womens-all', 'sheila-gunn-reids-picks', 'avi-yeminis-picks', 'drea-humphreys-picks', 'new-arrivals'}
SKIP_TAGS = {'light-colours-done', 'gift-under-40'}
SIMPLE = {'default', 'front', 'front_large'}
BLANK = '<p><strong>Bella+Canvas 3501 long-sleeve tee.</strong> 100% combed ring-spun cotton (heathers are a cotton-poly blend), 4.2 oz, retail fit. Unisex sizing.</p>'
MADE = '<p><em>Made to order: ships in 2-5 business days plus transit. Free shipping in Canada, the US, Australia and New Zealand on orders over $100.</em></p>'
QT = '''query($id:ID!){product(id:$id){title status descriptionHtml tags seo{description} collections(first:40){nodes{id handle}}
 variants(first:100){nodes{id selectedOptions{name value}}}}}'''
QN = 'query($h:String!){productByIdentifier(identifier:{handle:$h}){id mediaCount{count} publishedOnPublication(publicationId:"%s") variants(first:100){nodes{id selectedOptions{name value} inventoryItem{id}}}}}' % PUB
MS = 'mutation($i:ProductSetInput!){productSet(synchronous:true,input:$i){product{id variants(first:100){nodes{id selectedOptions{name value} inventoryItem{id}}}} userErrors{field message code}}}'
def opt(v, name): return next((x['value'] for x in v['selectedOptions'] if x['name'].lower() in name), None)
def slug(s): return re.sub(r'-+', '-', re.sub(r"[^a-z0-9]+", '-', s.lower().replace("'", '').replace('*', ''))).strip('-')
def join_words(xs): return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]
results, at_printful = [], None
out = os.path.join(os.path.dirname(__file__), '..', 'results', '011_long_sleeves_front_large.json')
def save(): json.dump(results, open(out, 'w'), indent=1)

c, j = shop.pf('/sync/products/@' + LS_EXAMPLE); LSPROD = j['result']['sync_variants'][0]['product']['product_id']
c, j = shop.pf('/products/%s' % LSPROD); cat = {(v['color'], v['size']): v for v in j['result']['variants']}
print('long-sleeve blank: Printful product', LSPROD, '| colours', sorted({k[0] for k in cat}), flush=True)
c, pj = shop.pf('/mockup-generator/printfiles/%s' % LSPROD); pr = pj['result']
areas = {x['printfile_id']: x for x in pr['printfiles']}; vplace = {x['variant_id']: x['placements'] for x in pr['variant_printfiles']}
LSCOLL = (shop.gql('query{collectionByIdentifier(identifier:{handle:"long-sleeve-t-shirts"}){id}}')['collectionByIdentifier'] or {}).get('id')

for n_done, (tee, tee_title) in enumerate(TEES):
    if time.time() - T_START > BUDGET: print('TIME BUDGET reached; not started:', len(TEES) - n_done, 'designs', flush=True); break
    name = tee_title; rec = {'tee': tee, 'tee_title': tee_title}
    try:
        if EXCLUDE.search(tee_title): rec['status'] = 'skipped: excluded design'; results.append(rec); continue
        t = shop.gql(QT, {'id': 'gid://shopify/Product/' + tee})['product']; name = t['title']
        if t['status'] != 'ACTIVE' or not name.endswith(' Unisex T-Shirt'): rec['status'] = 'skipped: tee not active or renamed'; results.append(rec); continue
        title = name[:-len(' Unisex T-Shirt')] + ' Unisex Long Sleeve Shirt'; handle = slug(title); rec['title'] = title
        colour_of = {v['id'].split('/')[-1]: opt(v, ('color', 'colour')) for v in t['variants']['nodes']}
        tee_cols = list(dict.fromkeys(x for x in colour_of.values() if x))
        c, j = shop.pf('/sync/products/@' + tee)
        if c != 200: rec['status'] = 'skipped: tee not in Printful (HTTP %s)' % c; results.append(rec); continue
        art, types = {}, set()
        for sv in j['result']['sync_variants']:
            fs = [f for f in sv['files'] if f['type'] != 'preview']; types |= {f['type'] for f in fs}
            col = colour_of.get(str(sv.get('external_id')))
            if not col or col in art or not sv.get('synced'): continue
            f = next((f for f in fs if f['type'] in SIMPLE), None)
            if f: art[col] = f
        multi = any(len({f['type'] for f in sv['files'] if f['type'] != 'preview'}) > 1 for sv in j['result']['sync_variants'])
        if types - SIMPLE or multi:
            rec['status'] = 'skipped: tee prints on %s (needs setting by hand)' % sorted(types); results.append(rec); print(name, '|', rec['status'], flush=True); continue
        cols = [x for x in tee_cols if x in art and all((x, s) in cat for s in SIZES)]
        rec['left_out'] = [x for x in tee_cols if x not in cols]; rec['colours'] = cols
        if not cols: rec['status'] = 'skipped: no tee colour on the long-sleeve blank'; results.append(rec); continue
        p = shop.gql(QN, {'h': handle})['productByIdentifier']
        if p and p['publishedOnPublication']: rec.update(pid=p['id'].split('/')[-1], status='already live'); results.append(rec); continue
        if p is None:
            story = re.search(r'<p>.*?</p>', t['descriptionHtml'] or '', flags=re.S)
            seo = re.sub(r'Printed to order on an? [^.]*\.\s*$', 'Printed to order on a long-sleeve tee.', (t['seo'] or {}).get('description') or '')
            def inp(stock):
                iq = {'inventoryItem': {'tracked': True, 'requiresShipping': True}, 'inventoryQuantities': [{'locationId': PF_LOC, 'name': 'available', 'quantity': 9999}]} if stock \
                    else {'inventoryItem': {'tracked': False, 'requiresShipping': True}}
                i = {'title': title, 'handle': handle, 'vendor': 'Rebel News', 'productType': 'Long Sleeve T-Shirt', 'status': 'ACTIVE',
                     'descriptionHtml': (story.group(0) if story else '') + BLANK + '<p>Available in %s.</p>' % join_words(cols) + MADE,
                     'tags': [x for x in t['tags'] if x not in SKIP_TAGS],
                     'productOptions': [{'name': 'Color', 'position': 1, 'values': [{'name': x} for x in cols]}, {'name': 'Size', 'position': 2, 'values': [{'name': s} for s in SIZES]}],
                     'variants': [dict({'optionValues': [{'optionName': 'Color', 'name': x}, {'optionName': 'Size', 'name': s}], 'price': PRICE[s], 'inventoryPolicy': 'CONTINUE'}, **iq) for x in cols for s in SIZES]}
                if seo: i['seo'] = {'description': seo}
                return i
            d = None
            if at_printful is not False:
                try:
                    d = shop.gql(MS, {'i': inp(True)})['productSet']
                    if d['userErrors']: print('  stock at Printful refused:', d['userErrors'][:2], flush=True); d = None; at_printful = False
                    else: at_printful = True
                except Exception as e: print('  stock at Printful not allowed:', str(e)[:200], flush=True); at_printful = False
            if d is None and shop.gql(QN, {'h': handle})['productByIdentifier']:
                rec['status'] = 'created but the stock attempt errored; re-run finishes it'; results.append(rec); save(); continue
            if d is None: d = shop.gql(MS, {'i': inp(False)})['productSet']
            if d['userErrors']: rec['status'] = 'not created: %s' % d['userErrors'][:2]; results.append(rec); continue
            p = {'id': d['product']['id'], 'variants': d['product']['variants'], 'mediaCount': {'count': 0}}
            rec['stock_at_printful'] = bool(at_printful)
            for col in [x for x in t['collections']['nodes'] if x['handle'] not in SKIP_COLL] + ([{'id': LSCOLL, 'handle': 'long-sleeve-t-shirts'}] if LSCOLL else []):
                try: shop.gql('mutation($id:ID!,$p:[ID!]!){collectionAddProducts(id:$id,productIds:$p){userErrors{message}}}', {'id': col['id'], 'p': [p['id']]})
                except Exception as e: print('  collection', col['handle'], 'not added:', str(e)[:90], flush=True)
        pid = p['id'].split('/')[-1]; rec['pid'] = pid
        rec['items'] = [v['inventoryItem']['id'].split('/')[-1] for v in p['variants']['nodes']]
        mine = {v['id'].split('/')[-1]: (opt(v, ('color', 'colour')), opt(v, ('size',))) for v in p['variants']['nodes']}
        svs, t0 = None, time.time()
        while time.time() - t0 < 420:
            c, j = shop.pf('/sync/products/@' + pid)
            if c == 200 and len(j['result']['sync_variants']) >= len(mine): svs = j['result']['sync_variants']; break
            time.sleep(15)
        if svs is None: rec['status'] = 'not imported by Printful after 7 minutes'; results.append(rec); save(); continue
        linked, fails = 0, []
        for sv in svs:
            col, size = mine.get(str(sv.get('external_id')), (None, None))
            if (col, size) not in cat or col not in art: fails.append((col, size)); continue
            cv = cat[(col, size)]['id']
            if sv.get('synced') and sv.get('variant_id') == cv: linked += 1; continue
            f = art[col]; pl = vplace.get(cv) or {}; ftype = f['type'] if f['type'] in pl else ('front' if 'front' in pl else 'default')
            body = {'variant_id': cv, 'files': [{'type': ftype, 'id': f['id']}]}
            area = areas.get(pl.get(ftype)) if pl else None
            if area and f.get('width') and f.get('height'):
                w = area['width']; h = round(f['height'] * w / f['width'])
                if h > area['height']: h = area['height']; w = round(f['width'] * h / f['height'])
                body['files'][0]['position'] = {'area_width': area['width'], 'area_height': area['height'], 'width': w, 'height': h, 'top': 0, 'left': (area['width'] - w) // 2}
            c2, r = shop.pf('/sync/variant/%s' % sv['id'], 'PUT', json=body)
            if c2 != 200 and 'position' in body['files'][0]:
                body['files'][0].pop('position'); c2, r = shop.pf('/sync/variant/%s' % sv['id'], 'PUT', json=body)
            if c2 != 200 and f.get('url'):
                body['files'][0] = {'type': ftype, 'url': f['url']}; c2, r = shop.pf('/sync/variant/%s' % sv['id'], 'PUT', json=body)
            if c2 == 200: linked += 1
            else: fails.append((col, size, c2))
            time.sleep(1.0)
        rec['linked'] = '%d/%d' % (linked, len(mine))
        if linked < len(mine): rec['status'] = 'only %d of %d variants linked' % (linked, len(mine)); results.append(rec); save(); print(title, '|', rec['status'], fails[:3], flush=True); continue
        time.sleep(10)
        n = flatstyle.one(pid, None, True, True)
        g = shop.gql('query($id:ID!){product(id:$id){mediaCount{count} variants(first:100){nodes{media(first:1){nodes{id}}}}}}', {'id': p['id']})['product']
        nophoto = sum(1 for v in g['variants']['nodes'] if not v['media']['nodes'])
        rec['photos'] = g['mediaCount']['count']
        rec['status'] = 'READY, hidden' if not nophoto else 'photos missing on %d variants' % nophoto
        results.append(rec); save()
        print(title, pid, '|', ', '.join(cols), '|', rec['status'], '| %d min' % ((time.time() - T_START) // 60), flush=True)
    except Exception as e:
        rec['status'] = 'error: %s %s' % (type(e).__name__, str(e)[:200]); results.append(rec); save()
        print(name, 'ERROR', type(e).__name__, str(e)[:300], flush=True)
save()
from collections import Counter
print('SUMMARY', dict(Counter(r['status'].split(':')[0] for r in results)), '| stock put at Printful location:', at_printful)
