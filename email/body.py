import json, subprocess, re, sys
from build import *
UTM='?utm_source=nationbuilder&utm_medium=email&utm_campaign=rns_xmas_cabuyers_112326'
S='https://rebelnewsstore.com'
def prod(handle):
    j=json.loads(subprocess.run(['curl','-sL','--max-time','30',S+'/products/'+handle+'.js'],capture_output=True,text=True).stdout)
    img=j['featured_image']; img=('https:'+img) if img.startswith('//') else img
    img=img+('&' if '?' in img else '?')+'width=500'
    return {'name':j['title'],'price':'$%d CAD'%round(j['price']/100),'img':img,'link':S+'/products/'+handle+UTM}
H=['carney-stole-christmas-unisex-t-shirt','fa-la-la-la-la-defund-the-cbc-unisex-t-shirt','all-is-calm-all-is-taxed-unisex-t-shirt','rebel-ugly-christmas-sweater-unisex-crewneck-sweatshirt','rebel-news-christmas-2026-ceramic-ornament','all-i-want-for-christmas-is-still-a-new-prime-minister-black-mug','told-you-so-unisex-hoodie','i-did-my-own-research-unisex-t-shirt']
P=[prod(h) for h in H]
for x in P: print(x['name'],'|',x['price'],'|',x['img'][-70:])
X=S+'/collections/christmas-shop-2026'+UTM
body='\n'.join([
 hero(X,'https://cdn.shopify.com/s/files/1/0825/9255/collections/christmas_2026_hero_mobile.jpg?v=1795117163&width=1056','Rebel News Store Christmas Shop 2026'),
 h1('The Christmas Shop is open'),
 p('Our Christmas 2026 collection is in the store, with new designs including Carney Stole Christmas, All Is Calm, All Is Taxed and Fa La La La La, Defund the CBC. There&rsquo;s a Rebel News ceramic ornament for the tree and a mug for the stocking, too.'),
 p('Everything is made to order, and most orders arrive in 5 to 15 business days. Order by '+strong('December 9')+' for Christmas delivery in Canada and the U.S.'),
 p('Shipping is free on orders over $100, and every purchase supports our independent journalism.'),
 btn(X,'Shop the Christmas collection'),
 h2('New this Christmas'), row(P[0],P[1]), row(P[2],P[3]), row(P[4],P[5]),
 btn(X,'See all Christmas designs'),
 h2('Also new: Told You So'),
 p('Fourteen new designs for everyone who asked questions and turned out to be right, on tees, hoodies and mugs.'),
 row(P[6],P[7]),
 btn(S+'/collections/told-you-so'+UTM,'See the Told You So collection'),
 p('Yours truly,<br>Rebel News')])
open('xmas_body_v3.html','w').write(body); print(len(body))
