"""Builds the four relaunch + Christmas promo bodies for the Rebel News Store (Christmas Promo theme).
Live titles, prices and lead photos come from the storefront; AUD prices via ?currency=AUD."""
import json, subprocess, sys, html
sys.path.insert(0, '/home/claude/rns-styled-product-photos/email')
from build import hero, h1, h2, p, strong, btn, row, box, divider
S = 'https://rebelnewsstore.com'
CACHE = {}

def fetch(handle, cur):
    k = (handle, cur)
    if k not in CACHE:
        u = S + '/products/' + handle + '.js' + ('?currency=AUD' if cur == 'AUD' else '')
        CACHE[k] = json.loads(subprocess.run(['curl', '-sL', '--max-time', '30', u], capture_output=True, text=True).stdout)
    return CACHE[k]

def money(cents, cur):
    v = cents / 100
    s = ('$%d' % v) if abs(v - round(v)) < 0.001 else ('$%.2f' % v)
    return s + ' ' + cur

class Email:
    def __init__(self, campaign, cur='CAD'):
        self.utm = '?utm_source=nationbuilder&utm_medium=email&utm_campaign=' + campaign + ('&country=AU' if cur == 'AUD' else '')
        self.cur = cur; self.used = []
    def link(self, path): return S + path + self.utm
    def prod(self, handle, note=None):
        j = fetch(handle, self.cur)
        img = j['featured_image']; img = ('https:' + img) if img.startswith('//') else img
        img += ('&' if '?' in img else '?') + 'width=500'
        lo, hi = j['price_min'], j['price_max']
        price = ('From ' if lo != hi else '') + money(lo, self.cur)
        self.used.append((handle, j['title'], price, img))
        d = {'name': j['title'], 'price': price, 'img': img, 'link': self.link('/products/' + handle)}
        if note: d['note'] = note
        return d
    def grid(self, handles):
        ps = [self.prod(h) for h in handles]
        return '\n'.join(row(ps[i], ps[i + 1] if i + 1 < len(ps) else None) for i in range(0, len(ps), 2))
    def coll(self, handle): return self.link('/collections/' + handle)

SIGN = 'Yours truly,<br>Rebel News'
FREE = 'Shipping is free on orders over $100, and every order helps pay for our independent journalism.'

def ca_buyers():
    e = Email('rns_xmas_cabuyers')
    b = [
        hero(e.coll('christmas-shop-2026'), 'HERO_CA', 'The new Rebel News Store'),
        h1('The Rebel News Store is back, and it&rsquo;s all new'),
        p('We&rsquo;ve rebuilt the Rebel News Store from top to bottom, with a whole new look.'),
        p('There are also ' + strong('dozens of new designs and hundreds of new products') + '.'),
        box('&#10052;&#xFE0E; Order by Wednesday, December 9 for Christmas delivery', 'Canada and the U.S. &middot; Everything is made to order'),
        btn(e.link('/'), 'Visit the new store'),
        divider(),
        h2('The Christmas Shop'),
        p('New this year: Christmas designs for everyone who&rsquo;s had enough of Ottawa, plus a Rebel News ornament for the tree.'),
        e.grid(['carney-stole-christmas-unisex-t-shirt', 'fa-la-la-la-la-defund-the-cbc-unisex-t-shirt', 'all-is-calm-all-is-taxed-unisex-t-shirt',
                'true-north-strong-merry-unisex-hoodie', 'rebel-news-christmas-2026-ceramic-ornament', 'all-i-want-for-christmas-is-still-a-new-prime-minister-black-mug']),
        btn(e.coll('christmas-shop-2026'), 'Shop the Christmas Shop'),
        divider(),
        h2('Our all-time best sellers'),
        p('The designs Rebel News viewers have bought most since the store opened, now with new photos and more colours.'),
        e.grid(['i-identify-as-a-conspiracy-theorist-tee', 'freedom-isnt-free-canada-unisex-t-shirt', 'proud-member-of-the-small-fringe-minority-unisex-t-shirt',
                'unisex-god-keep-our-land-unisex-t-shirt', 'rebel-logo-unisex-hoodie', 'i-identify-as-a-conspiracy-theorist-tee-1']),
        btn(e.coll('best-sellers'), 'See all best sellers'),
        divider(),
        h2('New: Told You So'),
        p('Fourteen new designs for everyone who asked questions, got called crazy, and turned out to be right.'),
        e.grid(['lab-leak-theory-told-you-so-unisex-t-shirt', 'i-think-for-myself-unisex-hoodie']),
        btn(e.coll('told-you-so'), 'Shop Told You So'),
        h2('New: Alberta'),
        p('Fresh designs for Albertans who are tired of sending more to Ottawa than they get back.'),
        e.grid(['alberta-makes-ottawa-takes-unisex-t-shirt', 'dont-ottawa-my-alberta-unisex-t-shirt']),
        btn(e.coll('alberta'), 'Shop Alberta'),
        h2('New: Justified'),
        p('Official merch for Tamara Lich&rsquo;s book Justified: The Long Road to Vindication, with the Justified stamp, Unapologetic, Still Standing and more.'),
        e.grid(['justified-stamp-unisex-t-shirt', 'the-process-is-the-punishment-unisex-t-shirt']),
        btn(e.coll('justified'), 'Shop Justified'),
        h2('New: Faith &amp; Freedom'),
        p('Scripture and faith designs, and the Save the Christians collection for persecuted believers around the world.'),
        e.grid(['save-the-christians-unisex-t-shirt', 'ephesians-6-11-armour-of-god-unisex-t-shirt']),
        btn(e.coll('faith-freedom'), 'Shop Faith &amp; Freedom'),
        h2('Hands Off Our Guns'),
        p('For hunters, sport shooters and farmers who are tired of being treated like criminals.'),
        e.grid(['hands-off-our-guns-unisex-t-shirt', 'law-abiding-gun-owner-unisex-t-shirt']),
        btn(e.coll('hands-off-our-guns'), 'Shop Hands Off Our Guns'),
        h2('Free Speech'),
        e.grid(['mean-tweets-are-not-a-crime-unisex-t-shirt', 'journalism-is-not-a-crime-unisex-t-shirt']),
        btn(e.coll('free-speech'), 'Shop Free Speech'),
        divider(),
        h2('Stocking stuffers under $40'),
        e.grid(['m-c-g-a-camo-trucker-hat', 'rebel-logo-cuffed-beanie', 'i-identify-as-a-conspiracy-theorist-sticker', 'bubble-free-stickers']),
        btn(e.coll('gifts-under-40'), 'Shop gifts under $40'),
        p(FREE), p(SIGN)]
    return e, '\n'.join(b)

def au_buyers():
    e = Email('rns_xmas_aubuyers', 'AUD')
    b = [
        hero(e.coll('aussie-patriot'), 'HERO_AU', 'The new Rebel News Store'),
        h1('G&rsquo;day! The Rebel News Store is back, and it&rsquo;s all new'),
        p('We&rsquo;ve rebuilt the Rebel News Store from top to bottom, with a whole new look.'),
        p('There are also ' + strong('dozens of new designs and hundreds of new products') + '.'),
        box('&#10052;&#xFE0E; Order by Tuesday, 1 December for Christmas delivery', 'Australia &middot; Everything is made to order &middot; New Zealand orders now arrive after Christmas'),
        p('Prices are in Australian dollars at checkout, shipping is free on orders over $100, and every order helps pay for Rebel News&rsquo; independent journalism.'),
        btn(e.link('/'), 'Visit the new store'),
        divider(),
        h2('Aussie favourites'),
        p('The designs Australians have bought most, now with new photos and more colours.'),
        e.grid(['this-is-my-pride-flag-unisex-t-shirt-1', 'freedom-isnt-free2-unisex-t-shirt', 'proud-aussie-unisex-t-shirt',
                'australia-stands-with-israel-unisex-t-shirt', 'get-up-for-your-pm-unisex-t-shirt', 'uncensorable-unisex-t-shirt']),
        btn(e.coll('aussie-patriot'), 'Shop Aussie Patriot'),
        h2('New: Defund the ABC'),
        p('Why should taxpayers fund a broadcaster that looks down on them? Now on tees, hoodies, crewnecks and mugs.'),
        e.grid(['defund-the-abc-unisex-t-shirt', 'defund-the-abc-unisex-hoodie']),
        divider(),
        h2('The Christmas Shop'),
        p('New Christmas designs to put Christ back in Christmas, plus a Rebel News ornament for the tree.'),
        e.grid(['its-merry-christmas-unisex-t-shirt', 'defend-christmas-unisex-t-shirt', 'silent-night-not-on-our-watch-unisex-t-shirt',
                'let-freedom-ring-unisex-hoodie', 'rebel-news-christmas-2026-ceramic-ornament', 'due-to-inflation-i-am-your-christmas-gift-two-tone-mug']),
        btn(e.coll('christmas-shop-2026'), 'Shop the Christmas Shop'),
        divider(),
        h2('Our all-time best sellers'),
        e.grid(['i-identify-as-a-conspiracy-theorist-tee', 'ban-idiots-not-guns-unisex-t-shirt', 'rebel-unisex-t-shirt', 'i-identify-as-a-conspiracy-theorist-tee-1']),
        btn(e.coll('best-sellers'), 'See all best sellers'),
        h2('New: Told You So'),
        p('Fourteen new designs for everyone who asked questions, got called crazy, and turned out to be right.'),
        e.grid(['lab-leak-theory-told-you-so-unisex-t-shirt', 'i-think-for-myself-unisex-hoodie']),
        btn(e.coll('told-you-so'), 'Shop Told You So'),
        h2('New: Faith &amp; Freedom'),
        p('Scripture and faith designs, and the Save the Christians collection for persecuted believers around the world.'),
        e.grid(['save-the-christians-unisex-t-shirt', 'ephesians-6-11-armour-of-god-unisex-t-shirt']),
        btn(e.coll('faith-freedom'), 'Shop Faith &amp; Freedom'),
        h2('Free Speech'),
        e.grid(['journalism-is-not-a-crime-unisex-t-shirt', 'mean-tweets-are-not-a-crime-unisex-t-shirt']),
        btn(e.coll('free-speech'), 'Shop Free Speech'),
        divider(),
        h2('Stocking stuffers'),
        e.grid(['proud-aussie-trucker-cap', 'rebel-logo-cuffed-beanie', 'proud-aussie-sticker', 'rebel-box-logo-sticker']),
        btn(e.coll('gifts-under-40'), 'Shop gifts'),
        p('Cheers,<br>Rebel News')]
    return e, '\n'.join(b)

def bf_donors():
    e = Email('rns_blackfriday_donors')
    b = [
        hero(e.link('/'), 'HERO_BF', 'Black Friday at the new Rebel News Store'),
        h1('Black Friday at the all-new Rebel News Store'),
        p('You&rsquo;ve supported Rebel News with a donation. The Rebel News Store is another way to do it: every order helps pay for our journalism, and you get something to wear, or to give.'),
        p('And the store is all new. We&rsquo;ve rebuilt it from top to bottom, with a whole new look and ' + strong('dozens of new designs and hundreds of new products') + '.'),
        box('15% off orders of $100 or more', 'Thursday, November 26 to Tuesday, December 1 &middot; No code needed', kind='code'),
        p('The discount is applied automatically at checkout, and orders over $100 also ship free.'),
        btn(e.link('/'), 'Shop the Black Friday sale'),
        box('&#10052;&#xFE0E; Order by December 9 for Christmas delivery', 'Canada and the U.S. &middot; December 1 for Australia and the U.K. &middot; New Zealand orders now arrive after Christmas'),
        divider(),
        h2('The Christmas Shop'),
        p('New this year: Christmas designs for everyone who&rsquo;s had enough of Ottawa, plus a Rebel News ornament for the tree.'),
        e.grid(['carney-stole-christmas-unisex-t-shirt', 'its-merry-christmas-unisex-t-shirt', 'true-story-nativity-unisex-hoodie',
                'honk-honk-ho-ho-ho-unisex-t-shirt', 'rebel-news-christmas-2026-ceramic-ornament', 'all-i-want-for-christmas-is-still-a-new-prime-minister-black-mug']),
        btn(e.coll('christmas-shop-2026'), 'Shop the Christmas Shop'),
        divider(),
        h2('Our all-time best sellers'),
        p('The designs Rebel News viewers have bought most since the store opened.'),
        e.grid(['i-identify-as-a-conspiracy-theorist-tee', 'proud-member-of-the-small-fringe-minority-unisex-t-shirt', 'ban-idiots-not-guns-unisex-t-shirt',
                'short-sleeve-unisex-t-shirt', 'rebel-logo-unisex-hoodie', 'free-shipping-honk-honk-short-sleeve-unisex-t-shirt']),
        btn(e.coll('best-sellers'), 'See all best sellers'),
        divider(),
        h2('New: Told You So'),
        p('Fourteen new designs for everyone who asked questions, got called crazy, and turned out to be right.'),
        e.grid(['lab-leak-theory-told-you-so-unisex-t-shirt', 'told-you-so-unisex-hoodie']),
        btn(e.coll('told-you-so'), 'Shop Told You So'),
        h2('New: Justified'),
        p('Official merch for Tamara Lich&rsquo;s book Justified: The Long Road to Vindication, with the Justified stamp, Unapologetic, Still Standing and more.'),
        e.grid(['justified-stamp-unisex-t-shirt', 'wolves-unisex-t-shirt']),
        btn(e.coll('justified'), 'Shop Justified'),
        h2('New: Faith &amp; Freedom'),
        p('Scripture and faith designs, and the Save the Christians collection for persecuted believers around the world.'),
        e.grid(['save-the-christians-unisex-t-shirt', 'unisex-god-keep-our-land-unisex-t-shirt']),
        btn(e.coll('faith-freedom'), 'Shop Faith &amp; Freedom'),
        h2('New: Alberta'),
        e.grid(['alberta-makes-ottawa-takes-unisex-t-shirt', 'the-west-wants-out-unisex-t-shirt']),
        btn(e.coll('alberta'), 'Shop Alberta'),
        h2('Hands Off Our Guns'),
        e.grid(['hands-off-our-guns-unisex-t-shirt', 'law-abiding-gun-owner-unisex-t-shirt']),
        btn(e.coll('hands-off-our-guns'), 'Shop Hands Off Our Guns'),
        divider(),
        h2('Stocking stuffers under $40'),
        e.grid(['rebel-logo-baseball-cap', 'm-c-g-a-camo-trucker-hat', 'rebel-box-logo-sticker', 'i-identify-as-a-conspiracy-theorist-sticker']),
        btn(e.coll('gifts-under-40'), 'Shop gifts under $40'),
        p('Thank you for supporting Rebel News.'), p(SIGN)]
    return e, '\n'.join(b)

def alberta():
    e = Email('rns_alberta')
    b = [
        hero(e.coll('alberta'), 'HERO_AB', 'Alberta gear at the new Rebel News Store'),
        h1('Alberta gear at the all-new Rebel News Store'),
        p('We&rsquo;ve rebuilt the Rebel News Store from top to bottom, with a whole new look.'),
        p('There are also ' + strong('dozens of new designs and hundreds of new products') + ', and Alberta is front and centre.'),
        box('&#10052;&#xFE0E; Order by Wednesday, December 9 for Christmas delivery', 'Everything is made to order'),
        btn(e.coll('alberta'), 'Shop the Alberta collection'),
        divider(),
        h2('The Alberta collection'),
        e.grid(['alberta-makes-ottawa-takes-unisex-t-shirt', 'dont-ottawa-my-alberta-unisex-hoodie', 'the-west-wants-out-unisex-t-shirt',
                'save-alberta-farms-unisex-t-shirt', 'alberta-first-unisex-t-shirt', 'short-sleeve-unisex-t-shirt']),
        btn(e.coll('alberta'), 'See all Alberta designs'),
        h2('Sheila Gunn Reid&rsquo;s Alberta books'),
        p('Independence Blueprint looks at Quebec&rsquo;s 1995 referendum and what Alberta can learn from it. The Case for Confederation collects every well-argued reason for Alberta to stay in Canada.'),
        e.grid(['independence-blueprint-what-alberta-can-learn-from-quebec', 'the-case-for-confederation-albertas-compelling-reasons-to-stick-around']),
        btn(e.coll('books'), 'See all books'),
        divider(),
        h2('The Christmas Shop'),
        p('New this year: Christmas designs for everyone who&rsquo;s had enough of Ottawa, plus a Rebel News ornament for the tree.'),
        e.grid(['carney-stole-christmas-unisex-t-shirt', 'santa-brings-coal-ottawa-taxes-it-unisex-t-shirt', 'honk-honk-ho-ho-ho-unisex-hoodie', 'rebel-news-christmas-2026-ceramic-ornament']),
        btn(e.coll('christmas-shop-2026'), 'Shop the Christmas Shop'),
        divider(),
        h2('Our all-time best sellers'),
        e.grid(['i-identify-as-a-conspiracy-theorist-tee', 'proud-member-of-the-small-fringe-minority-unisex-t-shirt', 'stand-with-farmers-unisex-t-shirt', 'rebel-logo-unisex-hoodie']),
        btn(e.coll('best-sellers'), 'See all best sellers'),
        h2('New: Justified'),
        p('Official merch for Tamara Lich&rsquo;s book Justified: The Long Road to Vindication, with the Justified stamp, Unapologetic, Still Standing and more.'),
        e.grid(['justified-stamp-unisex-t-shirt', 'the-long-road-unisex-t-shirt']),
        btn(e.coll('justified'), 'Shop Justified'),
        h2('Hands Off Our Guns'),
        e.grid(['hands-off-our-guns-unisex-t-shirt', 'hunters-sport-shooters-farmers-not-criminals-unisex-t-shirt']),
        btn(e.coll('hands-off-our-guns'), 'Shop Hands Off Our Guns'),
        h2('New: Told You So'),
        e.grid(['i-did-my-own-research-unisex-t-shirt', 'certified-misinformation-spreader-unisex-t-shirt']),
        btn(e.coll('told-you-so'), 'Shop Told You So'),
        divider(),
        h2('Stocking stuffers under $40'),
        e.grid(['alberta-first-trucker-cap', 'alberta-first-cuffed-beanie', 'alberta-first-sticker', 'ungovernable-baseball-cap']),
        btn(e.coll('gifts-under-40'), 'Shop gifts under $40'),
        p(FREE), p(SIGN)]
    return e, '\n'.join(b)

if __name__ == '__main__':
    out = {}
    for name, fn in [('ca', ca_buyers), ('au', au_buyers), ('bf', bf_donors), ('ab', alberta)]:
        e, body = fn(); out[name] = {'body': body, 'used': e.used}
        print(name, len(body), 'chars,', len(e.used), 'products')
    json.dump(out, open('/home/claude/promo/bodies.json', 'w'), indent=1)
