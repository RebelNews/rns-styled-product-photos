"""Defund the ABC: look at the light-colour print file and draft a dark-lettered version. Changes nothing in Printful or Shopify.

On Athletic Heather, Sport Grey and White, the Defund the ABC garments print "DEFUND" in white, so it barely shows.
Every light colour of the set uses Printful file 1119089622 (defund-the-abc-light.png); the dark colours use 1117450807
(rn26r_40_art.png). This run:
  1. reads both files' details from Printful and saves a preview of each,
  2. drafts a light-blank version from the dark-blank original: white and near-white lettering and stars become
     near-black (#040707); the red, the TV's colours and the transparency are left as they are,
  3. saves the draft at full size plus a review sheet of it on white, Athletic Heather and Sport Grey.
Nothing is uploaded or applied here. The draft is checked by eye first; a later job applies it.
"""
import io, os, json, requests
import numpy as np
from PIL import Image
import shop

OUT = 'results/014'
os.makedirs(OUT, exist_ok=True)
DARK, LIGHT = 1117450807, 1119089622
INK = (4, 7, 7)


def fetch(fid):
    c, j = shop.pf(f'/files/{fid}')
    r = j.get('result') or {}
    info = {k: r.get(k) for k in ('id', 'type', 'filename', 'status', 'width', 'height', 'dpi', 'size', 'visible')}
    info['has_url'] = bool(r.get('url')); info['has_preview'] = bool(r.get('preview_url')); info['http'] = c
    print('file', json.dumps(info), flush=True)
    src = r.get('url') or r.get('preview_url') or r.get('thumbnail_url')
    if not src: return info, None
    im = Image.open(io.BytesIO(requests.get(src, timeout=180).content)).convert('RGBA')
    print('file', fid, 'downloaded', im.size, 'from', 'url' if r.get('url') else 'preview', flush=True)
    return info, im


def on(bg, im, w=600):
    im = im.copy(); im.thumbnail((w, w))
    base = Image.new('RGBA', (w, w), bg + (255,))
    base.alpha_composite(im, ((w - im.width) // 2, (w - im.height) // 2))
    return base.convert('RGB')


def darken(im):
    a = np.array(im).astype(np.float32)
    rgb, al = a[..., :3] / 255.0, a[..., 3]
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    # hue, for finding the TV's blue body
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    blue = (b > r + 0.12) & (b > g + 0.02) & (sat > 0.25) & (al > 128)
    light = (mx > 0.62) & (sat < 0.22) & (al > 0)
    keep = np.zeros_like(light)
    ys, xs = np.nonzero(blue)
    if len(ys) > 50:
        y0, y1, x0, x1 = np.percentile(ys, 1), np.percentile(ys, 99), np.percentile(xs, 1), np.percentile(xs, 99)
        py, px = (y1 - y0) * 0.04, (x1 - x0) * 0.04
        yy, xx = np.mgrid[0:light.shape[0], 0:light.shape[1]]
        keep = (yy >= y0 - py) & (yy <= y1 + py) & (xx >= x0 - px) & (xx <= x1 + px)
        print('TV box (kept as is):', int(x0), int(y0), int(x1), int(y1), 'of', im.size, flush=True)
    else:
        print('no blue TV found; every light pixel will be darkened', flush=True)
    m = light & ~keep
    out = a.copy(); out[m, 0], out[m, 1], out[m, 2] = INK
    print('pixels darkened:', int(m.sum()), 'of', int((al > 0).sum()), 'visible', flush=True)
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


di, dark = fetch(DARK)
li, light = fetch(LIGHT)
if dark is None: raise SystemExit('no image for the dark-blank file')
on((40, 40, 40), dark, 900).save(f'{OUT}/dark_blank_original_preview.png')
if light is not None: on((255, 255, 255), light, 900).save(f'{OUT}/current_light_file_on_white.png')
new = darken(dark)
new.save(f'{OUT}/defund_the_abc_light_v2.png', optimize=True)
print('draft saved', new.size, flush=True)
cols = [('White', (255, 255, 255)), ('Athletic Heather', (196, 196, 194)), ('Sport Grey', (170, 170, 168))]
row = [on(c, new) for _, c in cols]
if light is not None: row = [on(cols[1][1], light)] + row
sheet = Image.new('RGB', (600 * len(row), 600), 'white')
for i, im in enumerate(row): sheet.paste(im, (600 * i, 0))
sheet.save(f'{OUT}/review_sheet.jpg', quality=88)
print('review sheet: current light file on Athletic Heather, then the draft on White, Athletic Heather, Sport Grey' if light is not None else 'review sheet: draft on White, Athletic Heather, Sport Grey', flush=True)
