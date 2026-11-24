"""Two things.

A. Lead photos for 27 mugs, stickers, hats, the ornament and the headband that still opened on a plain white (or
   transparent) photo. The styled versions were made and checked by eye beforehand and are in c/; this swaps each one in
   place, so nothing is added or removed and variants keep pointing at the same photo.

B. Long-sleeve pilot. For three designs that have a unisex tee, create the matching "Unisex Long Sleeve Shirt"
   (Bella+Canvas 3501, the blank the store's three existing long sleeves use; S to 2XL at $45 / $48):
   1. Read the tee's story, tags, collections and colours from Shopify, and each colour's print file from Printful.
   2. Create the long sleeve in Shopify, not yet visible on the store, in the tee's campaign collections.
   3. Wait for Printful to import it, link every variant to the Printful blank with the same print file as the tee's colour.
   4. Make a flat styled photo of each colour (same tool as the garment photo jobs).
   5. Leave it hidden from the store. It is a pilot: the stock location still has to be moved to Printful's (this
      job's Shopify access cannot do that) and the photos checked by eye before it is published.
   Colours the long-sleeve blank does not come in are skipped and logged. Re-running skips long sleeves that already exist."""
import json, re, time, shop
RAW = 'https://raw.githubusercontent.com/RebelNews/rns-styled-product-photos/main/'
PUB = 'gid://shopify/Publication/2929601'
# ---------------------------------------------------------------- A. lead photos
LEADS = [
  (46873296961670, 'Save the Christians Sticker'),
  (46873291522182, 'Pray for Nigeria Black Mug'),
  (46873287819398, 'Not Forgotten Black Mug'),
  (46873284739206, 'We Will Not Look Away Black Mug'),
  (46873283625094, 'And Still They Go to Church Black Mug'),
  (46873281724550, 'Save the Christians Black Mug'),
  (46870902571142, 'Justified Stamp Sticker'),
  (46869271871622, "Freedom Isn't Free Canada Sticker"),
  (46869220982918, 'Proud Aussie Sticker'),
  (46869181038726, 'UNGOVERNABLE Sticker'),
  (46869127266438, 'Alberta First Sticker'),
  (46869096824966, 'John 8:32 Sticker'),
  (46869049081990, 'Two Genders Sticker'),
  (46869024669830, 'God Keep Our Land Sticker'),
  (46868989247622, 'Ban Idiots Not Guns Sticker'),
  (46868968505478, 'Proud Member of the Small Fringe Minority Sticker'),
  (46868912930950, 'I Identify as a Conspiracy Theorist Sticker'),
  (46838896492678, 'Hands Off Our Guns Blaze Orange Beanie'),
  (46838896066694, 'Hands Off Our Guns Camo Trucker Cap'),
  (46834495193222, 'Rebel News Christmas 2026 Ceramic Ornament'),
  (26550336422022, 'Fringe Minority Trucker Cap'),
  (26397840605318, 'Proud Member of the Small Fringe Minority Vintage Baseball Cap'),
  (26078426366086, 'Rebel Box Logo Sticker'),
  (25929289924742, 'Make Canada Great Again Camo Trucker Cap'),
  (26174003642502, 'F*ck Hamas Headband'),
  (24980722319494, 'Rebel News Bullhorn Sticker'),
  (24408771690630, 'Brilliant Cross Distressed Baseball Cap')
]
done = 0
try:
    for k in range(0, len(LEADS), 9):
        files = [{'id': 'gid://shopify/MediaImage/%d' % mid, 'originalSource': RAW + 'c/m%d.jpg' % mid, 'alt': title} for mid, title in LEADS[k:k + 9]]
        d = shop.gql('mutation($f:[FileUpdateInput!]!){fileUpdate(files:$f){files{id} userErrors{field message code}}}', {'f': files})['fileUpdate']
        done += len(d['files'] or [])
        if d['userErrors']: print('lead photos userErrors', d['userErrors'][:3], flush=True)
    time.sleep(25)
    q = shop.gql('query($ids:[ID!]!){nodes(ids:$ids){... on MediaImage{id fileStatus image{width height}}}}', {'ids': ['gid://shopify/MediaImage/%d' % m for m, _ in LEADS]})['nodes']
    ok = [n for n in q if n and (n.get('image') or {}).get('width') == 1600]
    print('LEAD PHOTOS swapped', done, 'of', len(LEADS), '| now 1600 px:', len(ok), '| not yet:', [n['id'].split('/')[-1] + ':' + str(n.get('fileStatus')) for n in q if n and n not in ok], flush=True)
except Exception as e: print('LEAD PHOTOS ERROR', type(e).__name__, str(e)[:300], flush=True)
# ---------------------------------------------------------------- B. long-sleeve pilot
import flatstyle
TEES = ['15498367959174', '15491825959046', '6866757681286']   # Justified Stamp, Hands Off Our Guns, I Identify as a Conspiracy Theorist
LS_EXAMPLE = '6947730915462'                                    # True Story Nativity Unisex Long Sleeve Shirt, for the Printful blank
SIZES = ['S', 'M', 'L', 'XL', '2XL']; PRICE = {'S': '45.00', 'M': '45.00', 'L': '45.00', 'XL': '45.00', '2XL': '48.00'}
SKIP_COLL = {'all', 'unisex', 'unisex-t-shirt', 'mens-all', 'mens-t-shirts', 'best-sellers', 'featured', 'hall-of-fame', 'gifts-under-40', 'add-ons',
             'womens-all', 'sheila-gunn-reids-picks', 'avi-yeminis-picks', 'drea-humphreys-picks'}
SKIP_TAGS = {'light-colours-done', 'gift-under-40'}
BLANK = '<p><strong>Bella+Canvas 3501 long-sleeve tee.</strong> 100% combed ring-spun cotton (heathers are a cotton-poly blend), 4.2 oz, retail fit. Unisex sizing.</p>'
MADE = '<p><em>Made to order: ships in 2-5 business days plus transit. Free shipping in Canada, the US, Australia and New Zealand on orders over $100.</em></p>'
QT = '''query($id:ID!){product(id:$id){title descriptionHtml tags seo{description} collections(first:40){nodes{id handle}}
 variants(first:100){nodes{id selectedOptions{name value}}}}}'''
QN = 'query($h:String!){productByIdentifier(identifier:{handle:$h}){id publishedOnPublication(publicationId:"%s") variants(first:100){nodes{id selectedOptions{name value}}}}}' % PUB
MS = 'mutation($i:ProductSetInput!){productSet(synchronous:true,input:$i){product{id variants(first:100){nodes{id selectedOptions{name value}}}} userErrors{field message code}}}'
def opt(v, name): return next((x['value'] for x in v['selectedOptions'] if x['name'].lower() in name), None)
def slug(s): return re.sub(r'-+', '-', re.sub(r"[^a-z0-9]+", '-', s.lower().replace("'", ''))).strip('-')
def join_words(xs): return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]
results = []
try:
    c, j = shop.pf('/sync/products/@' + LS_EXAMPLE); LSPROD = j['result']['sync_variants'][0]['product']['product_id']
    c, j = shop.pf('/products/%s' % LSPROD); cat = {(v['color'], v['size']): v for v in j['result']['variants']}
    print('long-sleeve blank: Printful product', LSPROD, j['result']['product'].get('title') or j['result']['product'].get('model'), '| colours', sorted({k[0] for k in cat}), '| sizes', sorted({k[1] for k in cat}), flush=True)
    c, pj = shop.pf('/mockup-generator/printfiles/%s' % LSPROD); pr = pj['result']
    areas = {x['printfile_id']: x for x in pr['printfiles']}; vplace = {x['variant_id']: x['placements'] for x in pr['variant_printfiles']}
    print('placements on the blank:', sorted({p for v in vplace.values() for p in v}), '| mock-up styles:', pr.get('option_groups'), flush=True)
    LSCOLL = (shop.gql('query{collectionByIdentifier(identifier:{handle:"long-sleeve-t-shirts"}){id}}')['collectionByIdentifier'] or {}).get('id')
except Exception as e:
    print('PILOT could not read the long-sleeve blank from Printful:', type(e).__name__, str(e)[:300], flush=True); TEES = []
for tee in TEES:
    name = tee
    try:
        t = shop.gql(QT, {'id': 'gid://shopify/Product/' + tee})['product']; name = t['title']
        if not name.endswith(' Unisex T-Shirt'): print(name, 'SKIPPED: title does not end in "Unisex T-Shirt"'); continue
        title = name[:-len(' Unisex T-Shirt')] + ' Unisex Long Sleeve Shirt'; handle = slug(title)
        colour_of = {v['id'].split('/')[-1]: opt(v, ('color', 'colour')) for v in t['variants']['nodes']}
        tee_cols = list(dict.fromkeys(c for c in colour_of.values() if c))
        # each tee colour's print file, from Printful
        c, j = shop.pf('/sync/products/@' + tee)
        if c != 200: print(name, 'SKIPPED: tee not found in Printful, HTTP', c); continue
        art = {}
        for sv in j['result']['sync_variants']:
            col = colour_of.get(str(sv.get('external_id')))
            if not col or col in art or not sv.get('synced'): continue
            f = next((f for f in sv['files'] if f['type'] in ('default', 'front')), None) or next((f for f in sv['files'] if f['type'] != 'preview'), None)
            if f: art[col] = f
        cols = [c for c in tee_cols if c in art and all((c, s) in cat for s in SIZES)]
        left = [c for c in tee_cols if c not in cols]
        print(name, '| tee colours', tee_cols, '| long-sleeve colours', cols, '| left out', left, '| print files', {c: (art[c]['id'], art[c]['type'], art[c].get('width'), art[c].get('height'), bool(art[c].get('url'))) for c in cols}, flush=True)
        if not cols: print(name, 'SKIPPED: no colour of the tee exists on the long-sleeve blank'); continue
        p = shop.gql(QN, {'h': handle})['productByIdentifier']
        if p is None:
            story = re.search(r'<p>.*?</p>', t['descriptionHtml'] or '', flags=re.S)
            seo = re.sub(r'Printed to order on an? [^.]*\.\s*$', 'Printed to order on a long-sleeve tee.', (t['seo'] or {}).get('description') or '')
            i = {'title': title, 'handle': handle, 'vendor': 'Rebel News', 'productType': 'Long Sleeve T-Shirt', 'status': 'ACTIVE',
                 'descriptionHtml': (story.group(0) if story else '') + BLANK + '<p>Available in %s.</p>' % join_words(cols) + MADE,
                 'tags': [x for x in t['tags'] if x not in SKIP_TAGS],
                 'productOptions': [{'name': 'Color', 'position': 1, 'values': [{'name': c} for c in cols]}, {'name': 'Size', 'position': 2, 'values': [{'name': s} for s in SIZES]}],
                 'variants': [{'optionValues': [{'optionName': 'Color', 'name': c}, {'optionName': 'Size', 'name': s}], 'price': PRICE[s], 'inventoryPolicy': 'CONTINUE',
                               'inventoryItem': {'tracked': False, 'requiresShipping': True}} for c in cols for s in SIZES]}
            if seo: i['seo'] = {'description': seo}
            d = shop.gql(MS, {'i': i})['productSet']
            if d['userErrors']: print(title, 'NOT CREATED', d['userErrors'][:3], flush=True); results.append((title, None, 'not created')); continue
            p = {'id': d['product']['id'], 'variants': d['product']['variants'], 'publishedOnPublication': False}; print('created', title, p['id'].split('/')[-1], flush=True)
            for col in [x for x in t['collections']['nodes'] if x['handle'] not in SKIP_COLL] + ([{'id': LSCOLL, 'handle': 'long-sleeve-t-shirts'}] if LSCOLL else []):
                try:
                    r = shop.gql('mutation($id:ID!,$p:[ID!]!){collectionAddProducts(id:$id,productIds:$p){userErrors{message}}}', {'id': col['id'], 'p': [p['id']]})['collectionAddProducts']
                    print('  collection', col['handle'], '->', 'added' if not r['userErrors'] else r['userErrors'][0]['message'][:70], flush=True)
                except Exception as e: print('  collection', col['handle'], '-> not added:', str(e)[:90], flush=True)
        else: print('exists ', title, p['id'].split('/')[-1], flush=True)
        pid = p['id'].split('/')[-1]; mine = {v['id'].split('/')[-1]: (opt(v, ('color', 'colour')), opt(v, ('size',))) for v in p['variants']['nodes']}
        # wait for Printful to import it
        svs, t0 = None, time.time()
        while time.time() - t0 < 420:
            c, j = shop.pf('/sync/products/@' + pid)
            if c == 200 and len(j['result']['sync_variants']) >= len(mine): svs = j['result']['sync_variants']; break
            time.sleep(20)
        if svs is None: print(title, 'Printful had not imported it after 7 minutes; left hidden', flush=True); results.append((title, pid, 'not imported by Printful')); continue
        linked, fails, shown = 0, [], False
        for sv in svs:
            col, size = mine.get(str(sv.get('external_id')), (None, None))
            if (col, size) not in cat or col not in art: fails.append((col, size, 'no blank or art')); continue
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
                why = str(r)[:140]; body['files'][0].pop('position'); c2, r = shop.pf('/sync/variant/%s' % sv['id'], 'PUT', json=body)
                if not shown: print('  note: Printful refused the placement (%s); linked without it: HTTP %s' % (why, c2), flush=True)
            if c2 != 200 and f.get('url'):
                body['files'][0] = {'type': ftype, 'url': f['url']}; c2, r = shop.pf('/sync/variant/%s' % sv['id'], 'PUT', json=body)
            if not shown: print('  first link:', col, size, '-> blank variant', cv, '| file as', ftype, '| placement sent', body['files'][0].get('position'), '| HTTP', c2, str(r)[:160] if c2 != 200 else '', flush=True); shown = True
            if c2 == 200: linked += 1
            else: fails.append((col, size, 'HTTP %s %s' % (c2, str(r)[:80])))
            time.sleep(1.2)
        print(title, '| variants linked', linked, 'of', len(svs), '| failed', fails[:4], flush=True)
        if linked < len(mine): results.append((title, pid, 'only %d of %d variants linked; left hidden' % (linked, len(mine)))); continue
        time.sleep(20)
        n = flatstyle.one(pid, None, True, False); print(title, '| colour photos made', n, 'of', len(cols), flush=True)
        g = shop.gql('query($id:ID!){product(id:$id){mediaCount{count} variants(first:100){nodes{media(first:1){nodes{id}} inventoryItem{inventoryLevels(first:3){nodes{location{name}}}}}}}}', {'id': p['id']})['product']
        nophoto = sum(1 for v in g['variants']['nodes'] if not v['media']['nodes'])
        print(title, '| photos in gallery', g['mediaCount']['count'], '| variants without a photo', nophoto, '| stock location', sorted({l['location']['name'] for v in g['variants']['nodes'] for l in v['inventoryItem']['inventoryLevels']['nodes']}), flush=True)
        if n < len(cols) or nophoto: results.append((title, pid, 'photos missing for some colours; left hidden')); continue
        results.append((title, pid, 'READY, hidden'))
    except Exception as e:
        print(name, 'ERROR', type(e).__name__, str(e)[:300], flush=True); results.append((name, None, 'error: %s' % type(e).__name__))
for r in results: print('PILOT', r[0], '|', r[1], '|', r[2])
print('TOTAL lead photos', done, 'of', len(LEADS), '| long sleeves ready', sum(1 for r in results if r[2].startswith('READY')), 'of', len(TEES))
