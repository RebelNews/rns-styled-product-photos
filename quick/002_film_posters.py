"""Film posters: one poster product per Rebel News film, sold through Printful (Enhanced Matte Paper Poster, 12x18 in).

For each poster in posters/posters.json:
1. Create the Shopify product (not yet visible on the store) with its description, a styled lead photo and the poster art,
   in the Posters collection.
2. Wait for Printful to import it, then link its variant to the Printful poster and attach the print file.
3. Only when Printful confirms the link: publish it to the Online Store.
A poster that cannot be linked stays unpublished and is listed at the end. Re-running skips posters that already exist."""
import json, re, time, os, shop
RAW = 'https://raw.githubusercontent.com/RebelNews/rns-styled-product-photos/main/posters/'
PUB = 'gid://shopify/Publication/2929601'; POSTERS = 'gid://shopify/Collection/262796279942'
SIZE = '12″×18″'; PRICE = '25.00'
items = json.load(open('posters/posters.json'))
# --- Printful: find the poster and its 12x18 variant
c, j = shop.pf('/products'); cat = [p for p in j.get('result') or [] if 'enhanced matte paper poster' in (p.get('title') or p.get('model') or '').lower() and '(in)' in (p.get('title') or p.get('model') or '').lower()]
if not cat: raise SystemExit('Printful poster product not found in the catalog: HTTP %s' % c)
c, j = shop.pf('/products/%s' % cat[0]['id']); vs = j['result']['variants']
v12 = [v for v in vs if re.match(r'^\s*12\D+18\b', str(v.get('size') or '')) or re.search(r'12\D{1,3}18', str(v.get('name') or ''))]
if not v12: raise SystemExit('12x18 variant not found; sizes offered: %s' % sorted({str(v.get('size')) for v in vs}))
CATV = v12[0]['id']; print('Printful product', cat[0]['id'], cat[0].get('title'), '| 12x18 variant', CATV, v12[0].get('name'), '| in stock', v12[0].get('in_stock'), flush=True)
def html(it):
    return ('<p>The poster for <em>%s</em>. %s</p><p>Printed to order on thick, enhanced matte paper, 12″×18″ (30×46 cm). Ships rolled in a protective tube. Frame not included.</p>' % (it['film'], it['blurb']))
Q = 'query($h:String!){productByIdentifier(identifier:{handle:$h}){id status variants(first:3){nodes{id}} publishedOnPublication(publicationId:"%s")}}' % PUB
M = 'mutation($i:ProductSetInput!){productSet(synchronous:true,input:$i){product{id variants(first:3){nodes{id}}} userErrors{field message code}}}'
made, linked, live, problems = [], 0, 0, []
for it in items:
    try:
        p = shop.gql(Q, {'h': it['handle']})['productByIdentifier']
        if p is None:
            i = {'title': it['title'], 'handle': it['handle'], 'descriptionHtml': html(it), 'vendor': 'Rebel News', 'productType': 'Poster', 'tags': it['tags'], 'status': 'ACTIVE', 'collections': [POSTERS],
                 'productOptions': [{'name': 'Size', 'position': 1, 'values': [{'name': SIZE}]}],
                 'variants': [{'optionValues': [{'optionName': 'Size', 'name': SIZE}], 'price': PRICE, 'inventoryPolicy': 'CONTINUE', 'inventoryItem': {'tracked': False, 'requiresShipping': True}}],
                 'files': [{'originalSource': RAW + 'listing/' + it['file'], 'alt': it['title'], 'contentType': 'IMAGE'}, {'originalSource': RAW + it['file'], 'alt': it['film'] + ' poster art', 'contentType': 'IMAGE'}]}
            d = shop.gql(M, {'i': i})['productSet']
            if d['userErrors']: problems.append((it['title'], 'Shopify: ' + str(d['userErrors'])[:160])); print(it['title'], 'NOT CREATED', d['userErrors'][:2], flush=True); continue
            p = {'id': d['product']['id'], 'variants': d['product']['variants'], 'publishedOnPublication': False}; print('created', it['title'], p['id'].split('/')[-1], flush=True)
        else: print('exists ', it['title'], p['id'].split('/')[-1], '| on store' if p['publishedOnPublication'] else '| not on store', flush=True)
        made.append((it, p))
    except Exception as e: problems.append((it['title'], 'create: %s %s' % (type(e).__name__, str(e)[:160]))); print(it['title'], 'ERROR', type(e).__name__, str(e)[:200], flush=True)
print('products ready in Shopify:', len(made), '| waiting for Printful to import them', flush=True)
pending = list(made); t0 = time.time()
while pending and time.time() - t0 < 600:
    time.sleep(20); still = []
    for it, p in pending:
        pid = p['id'].split('/')[-1]; c, j = shop.pf('/sync/products/@' + pid)
        if c != 200: still.append((it, p)); continue
        try:
            svs = j['result']['sync_variants']; ok = True
            for sv in svs:
                if sv.get('synced') and sv.get('variant_id') == CATV: continue
                c2, r = shop.pf('/sync/variant/%s' % sv['id'], 'PUT', json={'variant_id': CATV, 'files': [{'type': 'default', 'url': RAW + 'print/' + it['file']}]})
                if c2 != 200: ok = False; problems.append((it['title'], 'Printful link HTTP %s %s' % (c2, str(r)[:140]))); print(it['title'], 'LINK FAILED', c2, str(r)[:160], flush=True)
                time.sleep(1.5)
            if not ok: continue
            linked += 1
            if not p['publishedOnPublication']:
                d = shop.gql('mutation($id:ID!,$in:[PublicationInput!]!){publishablePublish(id:$id,input:$in){userErrors{field message}}}', {'id': p['id'], 'in': [{'publicationId': PUB}]})['publishablePublish']
                if d['userErrors']: problems.append((it['title'], 'publish: ' + str(d['userErrors'])[:140])); print(it['title'], 'linked but NOT PUBLISHED', d['userErrors'][:2], flush=True); continue
            live += 1; print('live   ', it['title'], flush=True)
        except Exception as e: problems.append((it['title'], 'link: %s %s' % (type(e).__name__, str(e)[:160]))); print(it['title'], 'ERROR', type(e).__name__, str(e)[:200], flush=True)
    pending = still
for it, p in pending: problems.append((it['title'], 'Printful had not imported it after 10 minutes; left unpublished')); print(it['title'], 'not imported by Printful; left unpublished', flush=True)
print('TOTAL created or found', len(made), '| linked in Printful', linked, '| live on the store', live, '| problems', len(problems))
for t, why in problems: print('PROBLEM', t, '->', why)
