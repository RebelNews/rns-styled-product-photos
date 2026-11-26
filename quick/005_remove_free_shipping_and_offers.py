"""Remove free-shipping and discount/offer wording from every product description (active, draft and archived).

A scan on Nov 26, 2026 found two things to remove:
  1. "Free shipping in Canada, the US, Australia and New Zealand on orders over $100." at the end of the italic
     made-to-order line of about 907 products (827 live, 80 draft or archived). The rest of that line stays, e.g.
     "Made to order: ships in 2-5 business days plus transit." and, where present, "Order early for Christmas delivery."
  2. "BONUS! Enjoy a free month of RebelNews+ ... sign up with the code included in the confirmation email." in 6
     archived documentary downloads. The "To find out more about our premium subscription" link stays.
The scan also looked for discount, % off, sale, coupon, promo code, save $, deal and similar: the only matches were
ordinary words ("Hands Off Our Guns", "plea deal", "NOT FOR PUBLIC SALE"), so nothing else is touched.

This job reads every product fresh from the Admin API, so anything added since the scan is covered too. Any other
sentence that mentions free shipping is removed the same way and logged. Only those sentences change; every other
character of the description, including its HTML, stays as it is. An italic paragraph left empty is removed.
Old descriptions are saved to results/quick_005_backup.json so any product can be put back.
Safety stops: no product loses more than 600 characters, and the job stops before writing if more than 1,200
products would change."""
import json, re, shop

FREE_SHIP = re.compile(r'(?:\s|&nbsp;|\xa0)*[^.!?<>]*\bfree[\s-]*shipping\b[^.!?<>]*[.!?]?', re.I)
BONUS = re.compile(
    r'<strong>\s*BONUS!\s*</strong>.*?convenient place\.'
    r'(?:(?:\s|\xa0|&nbsp;|<span>(?:\xa0|&nbsp;|\s)*</span>)*Simply(?:\s|\xa0|&nbsp;|<span>(?:\xa0|&nbsp;|\s)*</span>)*'
    r'sign up with the code included in the confirmation email\.)?'
    r'(?:\s*<br\s*/?>){0,2}', re.S | re.I)
EMPTY = re.compile(r'<p[^>]*>\s*<(em|i)>\s*</\1>\s*</p>', re.I)


def clean(html):
    removed = []
    def ship(m):
        removed.append(m.group(0).strip()); return ''
    def bonus(m):
        removed.append(re.sub(r'<[^>]+>|\s+|\xa0', ' ', m.group(0)).strip()); return ''
    new = FREE_SHIP.sub(ship, html)
    new = BONUS.sub(bonus, new)
    new = EMPTY.sub('', new)
    return new, removed


def all_products():
    q = '''query($a:String){ products(first:100, after:$a){ pageInfo{hasNextPage endCursor}
            nodes{ id handle status descriptionHtml } } }'''
    a = None
    while True:
        d = shop.gql(q, {'a': a})['products']
        yield from d['nodes']
        if not d['pageInfo']['hasNextPage']: return
        a = d['pageInfo']['endCursor']


ps = list(all_products())
print('products read:', len(ps), flush=True)
todo = []
for p in ps:
    old = p['descriptionHtml'] or ''
    new, removed = clean(old)
    if new != old:
        lost = len(old) - len(new)
        if lost > 600: raise SystemExit(f'STOP: {p["handle"]} would lose {lost} characters')
        todo.append((p, old, new, removed))
print('descriptions to change:', len(todo), flush=True)
if len(todo) > 1200: raise SystemExit('STOP: more than 1,200 products would change')

kinds = {}
for _, _, _, rm in todo:
    for r in rm: kinds[r] = kinds.get(r, 0) + 1
print('sentences removed (count, text):')
for k, v in sorted(kinds.items(), key=lambda x: -x[1]): print(f'  {v:4d}  {k[:160]}')

json.dump({p['id']: {'handle': p['handle'], 'old': old} for p, old, _, _ in todo},
          open('results/quick_005_backup.json', 'w'))

M = 'mutation($p:ProductUpdateInput!){ productUpdate(product:$p){ product{ id } userErrors{ field message } } }'
ok = bad = 0
for p, old, new, removed in todo:
    r = shop.gql(M, {'p': {'id': p['id'], 'descriptionHtml': new}})['productUpdate']
    if r['userErrors']:
        bad += 1; print('ERROR', p['handle'], r['userErrors'], flush=True)
    else:
        ok += 1; print('changed', p['status'].lower(), p['handle'], flush=True)
print(f'updated {ok}, errors {bad}', flush=True)

left = [(p['status'].lower(), p['handle']) for p in all_products()
        if re.search(r'free[\s-]*shipping|free month of RebelNews', p['descriptionHtml'] or '', re.I)]
print('still mentioning free shipping or the free month after the run:', len(left), left[:20], flush=True)
