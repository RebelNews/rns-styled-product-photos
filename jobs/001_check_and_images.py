"""1) Confirm the Shopify and Printful credentials work (read-only). 2) Swap the last 55 Christmas Shop mock-ups for their styled versions, in place."""
import json, shop
print(shop.gql('{shop{name myshopifyDomain}}'))
for path in ('/store', '/sync/products?limit=1', '/mockup-generator/printfiles/71', '/mockup-generator/templates/71', '/product-templates?limit=1', '/files?limit=1'):
    c, j = shop.pf(path)
    r = j.get('result') if isinstance(j, dict) else None
    print('printful', path, c, (r.get('name') if isinstance(r, dict) and 'name' in r else (j.get('paging') or (j.get('error') or {}).get('message') or (list(r)[:4] if isinstance(r, dict) else type(r).__name__))), flush=True)
man = json.load(open('jobs/001_images.json'))
RAW = 'https://raw.githubusercontent.com/RebelNews/rns-styled-product-photos/main/c/'
done = 0
for i in range(0, len(man), 20):
    files = [dict(id=f"gid://shopify/MediaImage/{m['mid']}", originalSource=f"{RAW}m{m['mid']}.jpg", **({'alt': m['alt']} if m.get('alt') else {})) for m in man[i:i+20]]
    d = shop.gql('mutation($f:[FileUpdateInput!]!){fileUpdate(files:$f){files{id} userErrors{field message code}}}', {'f': files})['fileUpdate']
    done += len(d['files'] or [])
    if d['userErrors']: print('userErrors', d['userErrors'][:3])
print('images swapped', done, 'of', len(man))
