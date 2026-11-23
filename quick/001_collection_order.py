"""Product order on the menu's collection pages (approved Nov 23, 2026). Re-runnable as a refresh.

1. Campaign pages: up to four strong sellers (10+ sold in a year or 5+ in the last 90 days), then the tee of every design, then hoodies, sweatshirts, long sleeves,
   women's tees, mugs, hats and stickers. Designs with sales first, then the newest.
2. Product-type pages: eight proven sellers, then new launches rotated across campaigns with a proven seller after
   every three, then the rest in their previous best-selling order. These pages switch from automatic to manual order.
3. Best Sellers: the 16 best sellers of the last 90 days, in that order.
4. Christmas: the True Story Nativity hoodie moves to the fourth spot. Nothing else on that page changes.
5. Gifts Under $40: Christmas mugs, ornament and stickers first, then the previous best-selling order.
6. New: products published in the last 90 days only, one product type at a time, rotated across campaigns.

Before anything changes, every page's current sort setting and product order is saved to
results/collection_order_before.json. Nothing is deleted, archived or unpublished."""
import json, datetime, os, shop, collorder as co
today = datetime.date.today()
CAMP_SEQ = ['christmas-shop-2026', 'told-you-so', 'justified', 'save-the-christians', 'faith-freedom', 'alberta', 'hands-off-our-guns', 'free-speech',
            'stand-with-farmers', 'from-the-headlines-2025-26-campaign-merch', 'political-humour', 'freedom-convoy', 'ostrich-farm', 'tamara-lich',
            'proud-patriot', 'rebel-gear', 'aussie-patriot', 'make-canada-great-again', 'f-ck-hamas', 'protect-female-athletes', 'irish-pride', 'filmmerch']
CAMPAIGN_PAGES = [h for h in CAMP_SEQ if h != 'christmas-shop-2026']
TYPE_PAGES = ['unisex-t-shirt', 'womens-t-shirt', 'unisex-hoodie', 'unisex-sweatshirt', 'mugs', 'hats', 'hats-stickers-mugs']
BEST = [
    ("6866757681286", "I Identify as a Conspiracy Theorist Unisex T-Shirt"),
    ("7139123265670", "Rebel Box Logo Sticker"),
    ("6927580627078", "Rebel News Bullhorn Sticker"),
    ("7316973256838", "This Is My Pride Flag Unisex T-Shirt"),
    ("6889484648582", "REBEL Logo Unisex T-Shirt"),
    ("6873574375558", "Freedom Isn't Free Canada Unisex T-Shirt"),
    ("6947372859526", "True Story Nativity Unisex Hoodie"),
    ("6831724101766", "UNGOVERNABLE Unisex T-Shirt"),
    ("6890777804934", "Rebel News Typography Logo Unisex T-Shirt"),
    ("6866758336646", "I Identify as a Conspiracy Theorist Mug"),
    ("6897726128262", "Ban Idiots Not Guns Unisex T-Shirt"),
    ("6890817257606", "Rebel Typography Logo Unisex Hoodie"),
    ("6947730915462", "True Story Nativity Unisex Long Sleeve Shirt"),
    ("6890460250246", "REBEL Logo Unisex Hoodie"),
    ("6875620409478", "Proud Member of the Small Fringe Minority Unisex T-Shirt"),
    ("7068487811206", "F*ck Hamas II Unisex T-Shirt")
]
NATIVITY_HOODIE = "gid://shopify/Product/6947372859526"
NEW_DAYS = 90
pages, before, total, errors = {}, {}, 0, 0
for h in CAMP_SEQ + TYPE_PAGES + ['best-sellers', 'gifts-under-40', 'new-arrivals']:
    meta, ps = co.fetch(shop, h)
    if meta is None: print(h, 'collection not found'); continue
    pages[h] = (meta, ps); before[h] = {'id': meta['id'], 'sortOrder': meta['sortOrder'], 'products': [p['id'] for p in ps]}
os.makedirs('results', exist_ok=True); json.dump(before, open('results/collection_order_before.json', 'w'))
print('pages read', len(pages), '| previous order saved', flush=True)
def live(h): return [p for p in pages[h][1] if p['live']]
def run(h, target):
    global total, errors
    try: total += co.apply(shop, h, pages[h][0], pages[h][1], target)
    except Exception as e: errors += 1; print(h, 'ERROR', type(e).__name__, str(e)[:200], flush=True)
def show(h, target): print('  ', h, 'first 8:', ' | '.join(p['title'][:28] for p in target[:8]), flush=True)
camp_of, pos = {}, {}
for h in CAMP_SEQ:
    if h not in pages: continue
    t = live(h) if h == 'christmas-shop-2026' else co.campaign_order(live(h))
    for i, p in enumerate(t): camp_of.setdefault(p['id'], h); pos.setdefault(p['id'], i)
    if h != 'christmas-shop-2026': show(h, t); run(h, t)
def in_campaign_order(ps): return sorted(ps, key=lambda p: pos.get(p['id'], 10 ** 6))
for h in TYPE_PAGES:
    if h not in pages: continue
    cur = live(h); order = {p['id']: i for i, p in enumerate(cur)}
    t = co.type_order(in_campaign_order(cur), camp_of, CAMP_SEQ, today)
    known = {p['id'] for p in t if co.sold(p)[1] > 0 or co.age_days(p, today) <= 30}
    t = [p for p in t if p['id'] in known] + sorted((p for p in t if p['id'] not in known), key=lambda p: order[p['id']])
    show(h, t); run(h, t)
# Best Sellers
if 'best-sellers' in pages:
    meta, ps = pages['best-sellers']; want = ['gid://shopify/Product/' + i for i, _ in BEST]; have = {p['id'] for p in ps}
    n = co.set_membership(shop, meta['id'], [i for i in want if i not in have], [p['id'] for p in ps if p['live'] and p['id'] not in want])
    print('best-sellers membership changes', n, flush=True)
    pages['best-sellers'] = co.fetch(shop, 'best-sellers'); byid = {p['id']: p for p in pages['best-sellers'][1]}
    t = [byid[i] for i in want if i in byid]; show('best-sellers', t); run('best-sellers', t)
# Christmas: one move
if 'christmas-shop-2026' in pages:
    cur = live('christmas-shop-2026'); hd = [p for p in cur if p['id'] == NATIVITY_HOODIE]
    if hd:
        rest = [p for p in cur if p['id'] != NATIVITY_HOODIE]; t = rest[:3] + hd + rest[3:]; show('christmas-shop-2026', t); run('christmas-shop-2026', t)
    else: print('christmas-shop-2026: Nativity hoodie not on the page; left as is')
# Gifts Under $40
if 'gifts-under-40' in pages and 'christmas-shop-2026' in pages:
    t = co.gifts_order(live('gifts-under-40'), {p['id'] for p in pages['christmas-shop-2026'][1]}); show('gifts-under-40', t); run('gifts-under-40', t)
# New: last 90 days
if 'new-arrivals' in pages:
    meta, ps = pages['new-arrivals']; allp, after = [], None
    while True:
        d = shop.gql('query($a:String){products(first:250,after:$a,query:"status:active"){pageInfo{hasNextPage endCursor} nodes{id title productType status createdAt publishedAt publishedOnPublication(publicationId:"%s")}}}' % co.PUB, {'a': after})['products']
        allp += [{'id': n['id'], 'title': n['title'], 'type': n['productType'] or '', 'published': n.get('publishedAt') or n['createdAt'], 'live': bool(n['publishedOnPublication'])} for n in d['nodes']]
        if not d['pageInfo']['hasNextPage']: break
        after = d['pageInfo']['endCursor']
    fresh = [p for p in allp if p['live'] and p['type'] not in ('Vify Gift Card',) and co.age_days(p, today) <= NEW_DAYS]; fid = {p['id'] for p in fresh}; have = {p['id'] for p in ps}
    add = [p['id'] for p in fresh if p['id'] not in have]; rem = [p['id'] for p in ps if p['live'] and p['id'] not in fid]
    print('new-arrivals: live products', sum(p['live'] for p in allp), '| published in the last', NEW_DAYS, 'days', len(fresh), '| adding', len(add), '| removing', len(rem), flush=True)
    try:
        co.set_membership(shop, meta['id'], add, rem); pages['new-arrivals'] = co.fetch(shop, 'new-arrivals')
        t = co.new_order(in_campaign_order(live('new-arrivals')), camp_of, CAMP_SEQ); show('new-arrivals', t); run('new-arrivals', t)
    except Exception as e: errors += 1; print('new-arrivals ERROR', type(e).__name__, str(e)[:200])
print('TOTAL products placed', total, '| errors', errors)
