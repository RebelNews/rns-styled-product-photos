#!/usr/bin/env python3
"""Cut a flat product mock-up off its white (or transparent) background and place it on a Rebel News background."""
import os,sys,json,glob,io,subprocess
import numpy as np, cv2
from PIL import Image, ImageFilter
BGDIR=os.environ.get('BGDIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bg') + '/')
OUT=1600
_bg={}
def bgs():
    if not _bg:
        for f in sorted(glob.glob(BGDIR+'*.png')):
            im=Image.open(f).convert('RGB')
            a=np.asarray(im.resize((64,64)))[12:52,12:52].reshape(-1,3).astype(np.float32)
            lab=cv2.cvtColor(a.reshape(1,-1,3).astype(np.uint8),cv2.COLOR_RGB2LAB).reshape(-1,3).astype(np.float32)
            _bg[os.path.basename(f)[:-4]]=(im,lab.mean(0),lab.std(0).mean())
    return _bg
THEMES={'xmas':['xmas_gifts','xmas_plaid','xmas_snow','snowroad','redpaper'],
 'west':['bluebarn','prairie','wood','truckbed','bench'],'canada':['maple','ice','snowroad','forest'],
 'aus':['outback','beach'],'faith':['pew','linen','wood'],'news':['newsdesk','newsprint','neon','redpaper','navy'],
 'convoy':['road','truckbed','snowroad','maple'],'guns':['camp','forest','bench','wood'],'mug':['coffee','wood','newsdesk','linen']}
def theme_for(cols,ptype,title=''):
    c='|'.join(cols).lower()+' '+title.lower(); t=[]
    if 'christmas' in c: t+=THEMES['xmas']
    if any(k in c for k in('alberta','western','farmers','ostrich','ungovernable')): t+=THEMES['west']
    if any(k in c for k in('canada-day','make-canada','proud-patriot','canada')): t+=THEMES['canada']
    if 'aussie' in c or 'australia' in c: t+=THEMES['aus']
    if any(k in c for k in('faith','christians','church')): t+=THEMES['faith']
    if any(k in c for k in('convoy','tamara','hold-the-line','justified')): t+=THEMES['convoy']
    if any(k in c for k in('guns','hunting')): t+=THEMES['guns']
    if any(k in c for k in('free-speech','rebel-gear','headlines','told-you-so','political-humour','journalism')): t+=THEMES['news']
    if ptype=='Mug' and 'christmas' not in c: t+=THEMES['mug']
    return t or THEMES['news']
def cutout(im):
    """returns RGBA with alpha for a flat mock-up on white/transparent; None if it is not a flat mock-up"""
    if im.mode in('RGBA','LA','P'):
        rgba=im.convert('RGBA'); a=np.asarray(rgba)[...,3]
        if (a<250).mean()>0.08: return rgba,'transparent'
    rgb=np.asarray(im.convert('RGB')); h,w=rgb.shape[:2]
    mn=rgb.min(2)
    border=np.concatenate([mn[:6].ravel(),mn[-6:].ravel(),mn[:,:6].ravel(),mn[:,-6:].ravel()])
    if (border>=244).mean()<0.97:
        # something touches an edge: on-model or lifestyle shot
        top=(mn[:8]<235).mean(); bot=(mn[-8:]<235).mean()
        return None,('model' if (top>0.02 or bot>0.02) and (border>=244).mean()>0.6 else 'not_white')
    # flood fill near-white from the border
    near=(mn>=238).astype(np.uint8)
    ff=near.copy(); mask=np.zeros((h+2,w+2),np.uint8)
    for x in range(0,w,8):
        for y in(0,h-1):
            if ff[y,x]==1: cv2.floodFill(ff,mask,(x,y),2)
    for y in range(0,h,8):
        for x in(0,w-1):
            if ff[y,x]==1: cv2.floodFill(ff,mask,(x,y),2)
    fg=(ff!=2).astype(np.uint8)
    # keep the largest blobs, fill holes that are not strongly white-connected
    n,lab,st,_=cv2.connectedComponentsWithStats(fg,8)
    if n<2: return None,'empty'
    keep=np.zeros_like(fg); big=st[1:,4].max()
    for i in range(1,n):
        if st[i,4]>=0.02*big: keep[lab==i]=1
    area=keep.mean()
    garment=rgb[keep==1]; lum=garment.mean()
    light=lum>185
    if light:
        # white/ash garment on white: the flood fill leaks into the garment, so use a segmentation model and union
        try:
            from rembg import remove,new_session
            global _sess
            try: _sess
            except NameError: _sess=new_session('u2net')
            m=np.asarray(remove(im.convert('RGB'),session=_sess,only_mask=True))
            m=cv2.resize(m,(w,h))
            keep=((m>110)|(keep==1)).astype(np.uint8)
            # but never keep pure-white pixels connected to the border when the model says background
            keep[(ff==2)&(m<=110)]=0
            k=np.ones((5,5),np.uint8); keep=cv2.morphologyEx(keep,cv2.MORPH_CLOSE,k)
        except Exception as e:
            print('rembg failed',e,file=sys.stderr)
    # soft edge: erode 1px then feather
    a=(keep*255).astype(np.uint8)
    a=cv2.erode(a,np.ones((3,3),np.uint8),iterations=1)
    a=cv2.GaussianBlur(a,(0,0),0.8)
    out=np.dstack([rgb,a])
    return Image.fromarray(out,'RGBA'),('flat_light' if light else 'flat')
def garment_lab(rgba):
    a=np.asarray(rgba); m=a[...,3]>200
    if m.sum()<100: return np.array([128,128,128],np.float32)
    px=a[...,:3][m]
    # the garment colour is the most common colour, not the mean (prints skew the mean)
    q=(px//16).astype(np.int32); key=q[:,0]*256+q[:,1]*16+q[:,2]
    vals,cnt=np.unique(key,return_counts=True); top=vals[cnt.argmax()]
    sel=px[key==top].mean(0)
    return cv2.cvtColor(np.uint8([[sel]]),cv2.COLOR_RGB2LAB)[0,0].astype(np.float32)
GLOBAL={}
def pick_bg(glab,theme,used):
    tot=sum(GLOBAL.values())+1
    def score(name):
        im,lab,tex=bgs()[name]
        dE=float(np.linalg.norm(glab-lab)); dL=abs(float(glab[0])-float(lab[0]))
        return 0.5*dE+0.2*dL-40*used.get(name,0)-140*GLOBAL.get(name,0)/tot-0.2*tex, dE
    pick=None
    for pool in (list(dict.fromkeys(theme)), list(bgs())):
        c=[(score(n)[0],n) for n in pool if score(n)[1]>=42]
        if c: pick=max(c)[1]; break
    if pick is None: pick=max((score(n)[0],n) for n in bgs())[1]
    GLOBAL[pick]=GLOBAL.get(pick,0)+1
    return pick
def compose(rgba,bgname,fill=0.80):
    bg=bgs()[bgname][0].resize((OUT,OUT),Image.LANCZOS).copy()
    a=np.asarray(rgba)[...,3]; ys,xs=np.where(a>20)
    crop=rgba.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
    s=min(OUT*fill/crop.width,OUT*fill/crop.height)
    crop=crop.resize((max(1,int(crop.width*s)),max(1,int(crop.height*s))),Image.LANCZOS)
    x=(OUT-crop.width)//2; y=(OUT-crop.height)//2
    # soft drop shadow
    sh=Image.new('L',(OUT,OUT),0); sh.paste(crop.split()[3],(x+10,y+22))
    sh=sh.filter(ImageFilter.GaussianBlur(26)).point(lambda v:int(v*0.55))
    bg.paste(Image.new('RGB',(OUT,OUT),(0,0,0)),(0,0),sh)
    bg.paste(crop,(x,y),crop)
    return bg
if __name__=='__main__':
    # usage: styled.py jobs.json  -> jobs: [{src,out,cols,ptype,title,pid}]
    jobs=json.load(open(sys.argv[1])); used={}; res=[]; GRP={}
    for j in jobs:
        try:
            im=Image.open(j['src']); im.load()
            rgba,kind=cutout(im)
            if rgba is None: res.append({**j,'kind':kind,'ok':False}); continue
            if kind=='transparent': res.append({**j,'kind':kind,'ok':False}); continue
            u=used.setdefault(j['pid'],{}); gk=(j['pid'],j.get('grp'))
            if j.get('grp') and gk in GRP: b=GRP[gk]
            else:
                g=garment_lab(rgba); b=pick_bg(g,theme_for(j['cols'],j['ptype'],j.get('title','')),u)
                u[b]=u.get(b,0)+1; GRP[gk]=b
            compose(rgba,b).save(j['out'],quality=88,optimize=True)
            res.append({**j,'kind':kind,'bg':b,'ok':True})
        except Exception as e:
            res.append({**j,'kind':'error:'+str(e)[:80],'ok':False})
    json.dump(res,open(sys.argv[2],'w'))
    import collections
    print(collections.Counter(r['kind'] for r in res), collections.Counter(r.get('bg') for r in res if r['ok']).most_common(8))
