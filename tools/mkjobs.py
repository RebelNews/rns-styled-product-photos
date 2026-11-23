import json,os,re,sys,subprocess,concurrent.futures as cf
P={p['id']:p for p in json.load(open('data/products_public.json'))}
F=json.load(open('data/img_features.json'))
rows={int(str(r['id']).split('/')[-1]):r for r in json.load(open('data/rows.json'))}
scope=sys.argv[1].split(','); out=sys.argv[2]
jobs=[]
for p in P.values():
    c=rows.get(p['id'],{}).get('collections','').split('|')
    if not any(s in c for s in scope): continue
    for im in p['images']:
        if F.get(str(im['id']),{}).get('detail')!='white': continue
        fn=im['src'].split('/')[-1].split('?')[0]
        grp=re.sub(r'-(front|back|left|right|left-front|right-front|handle-on-left|handle-on-right|front-view)?-?[0-9a-f]{10,}\.\w+$','',fn)
        grp=re.sub(r'-(front|back|left|right|left-front|right-front)$','',grp)
        jobs.append({'iid':im['id'],'fn':fn,'url':im['src'].split('?')[0],'src':f'work/src/{im["id"]}.jpg','out':f'work/out/{im["id"]}.jpg','cols':c,'ptype':p['product_type'],'title':p['title'],'pid':p['id'],'grp':grp})
def dl(j):
    if not os.path.exists(j['src']) or os.path.getsize(j['src'])<2000:
        subprocess.run(['curl','-sS','-m','90','-o',j['src'],j['url']+'?width=1600'])
with cf.ThreadPoolExecutor(8) as ex: list(ex.map(dl,jobs))
json.dump(jobs,open(out,'w')); print(len(jobs),'jobs',len({j['pid'] for j in jobs}),'products')
