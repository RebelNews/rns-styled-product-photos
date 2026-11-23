"""Product order on collection pages.

Three patterns, all computed from live store data so the job can be re-run as a refresh:
- campaign pages: up to four strong sellers (10+ sold in a year or 5+ in 90 days), then the tee of every design, then hoodies, sweatshirts, long sleeves,
  women's tees, mugs, hats, stickers. Designs with sales come first, then the newest.
- product-type pages: eight proven sellers, then new launches rotated across campaigns with a proven seller after
  every three, then everything else in its previous (best-selling) order.
- New: products published in the last N days, one type at a time, rotated across campaigns.
Nothing is deleted. The previous order of every page is saved so it can be put back."""
import re, json, time, datetime
TYPE_RANK = {'Unisex T-Shirt': 0, 'Unisex Hoodie': 1, 'Unisex Sweatshirt': 2, 'Long Sleeve T-Shirt': 3, "Women's T-Shirt": 4, 'Mug': 5, 'Hat': 6, 'Sticker': 7}
SUF = [r"\s*[-–]?\s*Unisex (Crewneck |Heavy Blend )?(T-Shirt|Tee|Hoodie|Sweatshirt|Long Sleeve (T-)?Shirt)( \(Australia\))?$", r"\s*Women'?s (Relaxed |Racerback )?(T-Shirt|Tank|Tee)$",
       r"\s*Men'?s Tank Top$", r"\s*(Black |White |Ceramic |Coffee )?Mug$", r"\s*[-–]?\s*(Vintage |Distressed |Camo |Denim )?(Trucker Cap|Baseball Cap|Dad Hat|Cuffed Beanie|Beanie|Hat|Toque|Cap)$",
       r"\s*(Bumper )?Sticker$", r"\s*[-–]?\s*Poster$", r"\s*(Ceramic )?Ornament$", r"\s*Flag$", r"\s*Headband$", r"\s*T-Shirt$"]
def design(title):
    d = title
    for s in SUF:
        n = re.sub(s, '', d, flags=re.I)
        if n != d and n.strip(): d = n; break
    return re.sub(r'[\s\-–:]+$', '', d).strip().lower()
# Units sold: (last 90 days, last 365 days), Shopify analytics, Nov 23 2026. Refresh this table when re-running.
SALES = {"I Identify as a Conspiracy Theorist Unisex T-Shirt": (26, 94), "This Is My Pride Flag Unisex T-Shirt": (10, 50), "REBEL Logo Unisex T-Shirt": (9, 39), "Rebel Box Logo Sticker": (16, 38),
 "Rebel News Typography Logo Unisex T-Shirt": (5, 35), "Rebel News Bullhorn Sticker": (12, 33), "I Identify as a Conspiracy Theorist Mug": (5, 32), "REBEL Logo Unisex Hoodie": (4, 29),
 "Get Up for Your PM Unisex T-Shirt": (1, 28), "UNGOVERNABLE Unisex T-Shirt": (6, 21), "John 8:32 Unisex Hoodie": (2, 21), "Freedom Isn't Free Canada Unisex T-Shirt": (9, 21),
 "Proud Aussie Unisex T-Shirt": (2, 20), "Ban Idiots Not Guns Unisex T-Shirt": (5, 18), "REBEL Trucker Cap": (2, 17), "REBEL Logo Cuffed Beanie": (2, 16),
 "Freedom Isn't Free Unisex T-Shirt (Australia)": (3, 15), "Ostrich Poster Unisex T-Shirt": (3, 15), "Proud Member of the Small Fringe Minority Unisex T-Shirt": (4, 15), "F*ck Hamas Sticker": (6, 15),
 "Rebel News Stacked Logo Baseball Cap": (3, 14), "F*ck Hamas II Unisex T-Shirt": (4, 14), "REBEL Logo Baseball Cap": (3, 13), "God Keep Our Land Unisex T-Shirt": (2, 13),
 "My Rights Don't End Where Your Feelings Begin Unisex T-Shirt": (3, 13), "UNGOVERNABLE Unisex Hoodie": (3, 12), "This Is My Pride Flag (Canada) Unisex T-Shirt": (1, 12), "Rebel Typography Logo Unisex Hoodie": (5, 12),
 "No Human Balls! Sticker": (5, 11), "All I Want for Christmas Is a New Prime Minister Mug": (0, 11), "Alberta First Unisex T-Shirt": (2, 11), "Keep Your Head Out of the Sand Ostrich Unisex T-Shirt": (0, 10),
 "Rebel News Logo Mug": (2, 10), "Freedom Never Dies Unisex T-Shirt": (0, 10), "Make Canada Great Again Baseball Cap": (1, 10), "Freedom Isn't Free Canada Unisex Hoodie": (2, 9),
 "F*ck Hamas Unisex T-Shirt": (1, 9), "Happy Australia Day Unisex T-Shirt": (2, 9), "Two Genders Unisex T-Shirt": (1, 8), "Make Canada Great Again Camo Trucker Cap": (0, 8),
 "REBEL Logo Unisex Crewneck Sweatshirt": (0, 8), "True Story Nativity Unisex Hoodie": (7, 8), "My Boycott Coffee Mug": (3, 8), "Rebel News Logo Horn Background Unisex T-Shirt": (1, 7),
 "UNGOVERNABLE Unisex Crewneck Sweatshirt": (0, 7), "Rebel Bullhorn Logo Unisex T-Shirt": (0, 7), "Stand Tall Unisex T-Shirt": (1, 7), "Ostrich Avengers Unisex T-Shirt": (0, 7),
 "Cluck the System Unisex T-Shirt": (2, 7), "Definition of a Woman Unisex T-Shirt": (4, 6), "F*ck Hamas Unisex Hoodie": (1, 6), "True Story Nativity Unisex Long Sleeve Shirt": (5, 6),
 "Make Canada Great Again Unisex T-Shirt": (0, 6), "Proud Member of the Small Fringe Minority Unisex Hoodie": (3, 6), "True Story Nativity Unisex T-Shirt": (1, 6), "True North Strong and Free Unisex T-Shirt": (1, 6),
 "No Balls in Women's Stalls Unisex T-Shirt": (4, 4), "Galatians 5:13 Unisex Hoodie": (4, 5), "UNGOVERNABLE Cuffed Beanie": (4, 5), "Rebel at Heart Unisex Crewneck Sweatshirt": (2, 5)}
def sold(p): return SALES.get(p['title'], (0, 0))
def score(p):
    """Twelve-month units plus double weight on the last 90 days, so one recent bulk order does not outrank a steady seller."""
    a, b = sold(p); return b + 2 * a
def strong(p):
    a, b = sold(p); return b >= 10 or a >= 5
def age_days(p, today): return (today - datetime.date.fromisoformat(p['published'][:10])).days
def campaign_order(ps, lead=4):
    """ps: the page's products in their current order."""
    top = sorted((p for p in ps if strong(p)), key=score, reverse=True)[:lead]
    ids = {p['id'] for p in top}; rest = [p for p in ps if p['id'] not in ids]
    info = {}
    for i, p in enumerate(ps):
        d = design(p['title']); s = score(p); e = info.setdefault(d, [s, p['published'][:10], i])
        if s > e[0]: e[0] = s
        if p['published'][:10] > e[1]: e[1] = p['published'][:10]
    def dkey(d):
        s, pub, first = info[d]
        return (-s, -datetime.date.fromisoformat(pub).toordinal(), first)
    dorder = {d: k for k, d in enumerate(sorted(info, key=dkey))}
    rest.sort(key=lambda p: (TYPE_RANK.get(p['type'], 8), dorder[design(p['title'])]))
    return top + rest
def rotate(groups):
    """Round-robin over lists: one from each in turn until all are empty."""
    out, groups = [], [list(g) for g in groups if g]
    while groups:
        for g in groups: out.append(g.pop(0))
        groups = [g for g in groups if g]
    return out
def by_campaign(ps, camp_of, camp_seq):
    g = {}
    for p in ps: g.setdefault(camp_of.get(p['id'], 'other'), []).append(p)
    return rotate([g[c] for c in list(camp_seq) + ['other'] if c in g])
def type_order(ps, camp_of, camp_seq, today, lead=8, new_days=30):
    proven = sorted((p for p in ps if sold(p)[1] > 0), key=score, reverse=True)
    pid = {p['id'] for p in proven}
    new = by_campaign([p for p in ps if p['id'] not in pid and age_days(p, today) <= new_days], camp_of, camp_seq)
    nid = {p['id'] for p in new}; old = [p for p in ps if p['id'] not in pid and p['id'] not in nid]
    out, more = proven[:lead], proven[lead:]
    while new or more:
        out += new[:3]; new = new[3:]
        if more: out.append(more.pop(0))
    return out + old
def new_order(ps, camp_of, camp_seq):
    out = []
    for r in sorted({TYPE_RANK.get(p['type'], 8) for p in ps}):
        out += by_campaign([p for p in ps if TYPE_RANK.get(p['type'], 8) == r], camp_of, camp_seq)
    return out
def gifts_order(ps, xmas_ids):
    pri = {'Mug': 0, 'Ornament': 1, 'Sticker': 2, 'Hat': 3}
    x = sorted((p for p in ps if p['id'] in xmas_ids), key=lambda p: pri.get(p['type'], 4))
    return x + [p for p in ps if p['id'] not in xmas_ids]

# ---------- Shopify side ----------
PUB = 'gid://shopify/Publication/2929601'  # Online Store
QC = '''query($h:String!,$a:String){collectionByIdentifier(identifier:{handle:$h}){id title sortOrder products(first:250,after:$a){pageInfo{hasNextPage endCursor}
 nodes{id title productType status createdAt publishedAt publishedOnPublication(publicationId:"%s")}}}}''' % PUB
def fetch(shop, handle):
    after, out, meta = None, [], None
    while True:
        c = shop.gql(QC, {'h': handle, 'a': after})['collectionByIdentifier']
        if c is None: return None, []
        meta = {'id': c['id'], 'title': c['title'], 'sortOrder': c['sortOrder']}
        for n in c['products']['nodes']:
            out.append({'id': n['id'], 'title': n['title'], 'type': n['productType'] or '', 'published': (n.get('publishedAt') or n['createdAt']), 'live': n['status'] == 'ACTIVE' and bool(n['publishedOnPublication'])})
        if not c['products']['pageInfo']['hasNextPage']: break
        after = c['products']['pageInfo']['endCursor']
    return meta, out
def wait_job(shop, job):
    if not job or job.get('done'): return
    for _ in range(90):
        time.sleep(2)
        if shop.gql('query($id:ID!){job(id:$id){done}}', {'id': job['id']})['job']['done']: return
    raise RuntimeError('reorder job did not finish')
def apply(shop, handle, meta, current, target, log=print):
    """Make `target` (list of products) the first products on the page, in that order."""
    if [p['id'] for p in current[:len(target)]] == [p['id'] for p in target] and meta['sortOrder'] == 'MANUAL': log(handle, 'already in this order'); return 0
    if meta['sortOrder'] != 'MANUAL':
        d = shop.gql('mutation($c:CollectionUpdateInput!){collectionUpdate(collection:$c){collection{id sortOrder} userErrors{field message}}}', {'c': {'id': meta['id'], 'sortOrder': 'MANUAL'}})['collectionUpdate']
        if d['userErrors']: raise RuntimeError(str(d['userErrors'])[:200])
        time.sleep(6)
    moves = [{'id': p['id'], 'newPosition': str(i)} for i, p in enumerate(target)]
    for k in range(0, len(moves), 250):
        d = shop.gql('mutation($id:ID!,$m:[MoveInput!]!){collectionReorderProducts(id:$id,moves:$m){job{id done} userErrors{field message}}}', {'id': meta['id'], 'm': moves[k:k + 250]})['collectionReorderProducts']
        if d['userErrors']: raise RuntimeError(str(d['userErrors'])[:200])
        wait_job(shop, d['job'])
    time.sleep(2); _, after = fetch(shop, handle)
    ok = [p['id'] for p in after[:len(target)]] == [p['id'] for p in target]
    log(handle, 'reordered', len(target), 'products |', 'verified' if ok else 'NOT VERIFIED: order on Shopify differs', '| was', meta['sortOrder'], flush=True)
    return len(target) if ok else 0
def set_membership(shop, coll_id, add, remove, log=print):
    """Join/leave a manual collection, 20 products per request."""
    n = 0
    for ids, key in ((add, 'collectionsToJoin'), (remove, 'collectionsToLeave')):
        for k in range(0, len(ids), 20):
            chunk = ids[k:k + 20]
            q = 'mutation{' + ' '.join('m%d:productUpdate(product:{id:"%s",%s:["%s"]}){userErrors{message}}' % (i, pid, key, coll_id) for i, pid in enumerate(chunk)) + '}'
            d = shop.gql(q)
            errs = [v['userErrors'] for v in d.values() if v['userErrors']]
            if errs: log('membership userErrors', str(errs)[:200])
            n += len(chunk) - len(errs)
    return n
