"""Flat styled mock-ups for every garment in Christmas Shop 2026 and Best Sellers.
Each colour's main image is replaced in place. Blank mock-ups are refused. Nothing is deleted.
Stops starting new products after 80 minutes and logs what is left."""
import shop, flatstyle
GARMENTS = {'Unisex T-Shirt', "Women's T-Shirt", 'Unisex Sweatshirt', 'Unisex Hoodie', 'Long Sleeve T-Shirt'}
ids = []
for cid in ('512970850438', '269579583622'):
    after = None
    while True:
        d = shop.gql('query($id:ID!,$a:String){collection(id:$id){products(first:100,after:$a){pageInfo{hasNextPage endCursor} nodes{id productType status}}}}', {'id': f'gid://shopify/Collection/{cid}', 'a': after})['collection']['products']
        ids += [n['id'].split('/')[-1] for n in d['nodes'] if n['productType'] in GARMENTS and n['status'] == 'ACTIVE']
        if not d['pageInfo']['hasNextPage']: break
        after = d['pageInfo']['endCursor']
ids = list(dict.fromkeys(ids))
print('products', len(ids), flush=True)
flatstyle.run(ids, minutes=80)
