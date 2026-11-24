"""Light-garment version of the Defund the ABC art. Used by job 015."""
import numpy as np, cv2
from PIL import Image
INK=(4,7,7)
def make_light(im):
    """Light-blank version of the Defund the ABC art: the DEFUND lettering and the white stars become near-black,
    the lettering's black drop shadow and outline are removed, and the TV, antennas, red and transparency stay as they are."""
    a=np.array(im.convert('RGBA')).astype(np.float32); H,W=a.shape[:2]; k=W/2228.0
    rgb=a[...,:3]/255.0; al=a[...,3]
    mx,mn=rgb.max(-1),rgb.min(-1); sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
    light=(mx>0.62)&(sat<0.22)&(al>0)
    black=(mx<0.2)&(sat<0.35)&(al>0)
    ker=lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(max(3,int(2*r*k)|1),)*2)
    # the lettering band: from the top down to where light pixels thin out
    prof=light.sum(1); top=int(np.argmax(prof>0.02*W)); end=top; run=0
    for y in range(top,H):
        if prof[y]<0.02*W: run+=1
        else: run=0; end=y
        if run>int(12*k)+2: break
    band=np.zeros((H,W),bool); band[:end+1]=True
    letters=light&band
    # free-standing light shapes (the stars): mostly transparent around them
    n,lab,st,_=cv2.connectedComponentsWithStats((light&~band).astype(np.uint8),8)
    free=np.zeros((H,W),bool)
    for i in range(1,n):
        x,y,w,h,area=st[i]
        if area<30*k*k: continue
        p=int(16*k)+2; y0,y1,x0,x1=max(0,y-p),min(H,y+h+p),max(0,x-p),min(W,x+w+p)
        c=(lab[y0:y1,x0:x1]==i).astype(np.uint8)
        ring=(cv2.dilate(c,ker(12))>0)&~(cv2.dilate(c,ker(4))>0)
        empty=(al[y0:y1,x0:x1]<40)|black[y0:y1,x0:x1]
        if ring.sum() and empty[ring].mean()>0.6 and area<0.01*H*W: free[y0:y1,x0:x1]|=c>0
    shadow=black&(cv2.dilate(letters.astype(np.uint8),ker(60))>0)
    shadow[int(end+30*k):]=False
    out=a.copy(); m=letters|free
    out[m,0],out[m,1],out[m,2]=INK
    out[shadow,3]=0
    stats={'band_top':top,'band_end':end,'letters':int(letters.sum()),'stars':int(free.sum()),'shadow':int(shadow.sum())}
    return Image.fromarray(out.astype(np.uint8),'RGBA'),stats
