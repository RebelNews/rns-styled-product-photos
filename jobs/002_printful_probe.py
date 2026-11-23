"""Read-only: learn what the Printful token can do for the Rebel News store, so the mock-up job can be written correctly. Changes nothing."""
import json, shop
def show(label, c, j, keep=600): print(label, c, json.dumps(j.get('result', j) if isinstance(j, dict) else j)[:keep], flush=True)
c, j = shop.pf('/store'); show('store', c, {'result': {k: (j.get('result') or {}).get(k) for k in ('id', 'name', 'type')}} if c == 200 else j)
c, j = shop.pf('/sync/products?limit=3'); show('sync products', c, {'result': [{k: p.get(k) for k in ('id', 'external_id', 'name', 'variants', 'synced')} for p in (j.get('result') or [])], 'paging': j.get('paging')} if c == 200 else j)
first = ((j.get('result') or [{}])[0]).get('id') if c == 200 else None
if first:
    c, j = shop.pf(f'/sync/products/{first}')
    v = ((j.get('result') or {}).get('sync_variants') or [{}])[0]
    show('one sync variant', c, {'result': {'variant_id': v.get('variant_id'), 'product': v.get('product'), 'files': [{k: f.get(k) for k in ('type', 'id', 'filename', 'width', 'height', 'preview_url')} for f in v.get('files') or []], 'options': v.get('options')}} if c == 200 else j, 1500)
for pid in (71, 146, 145, 360, 356):
    c, j = shop.pf(f'/mockup-generator/printfiles/{pid}'); r = j.get('result') or {}
    show(f'printfiles {pid}', c, {'result': {'placements': r.get('available_placements'), 'n_variant_printfiles': len(r.get('variant_printfiles') or [])}} if c == 200 else j)
c, j = shop.pf('/mockup-generator/templates/71'); r = j.get('result') or {}
show('templates 71', c, {'result': {'n_templates': len(r.get('templates') or []), 'first': (r.get('templates') or [{}])[0], 'option_groups': r.get('option_groups'), 'options': r.get('options')}} if c == 200 else j, 2500)
c, j = shop.pf('/product-templates?limit=3'); show('product templates', c, j, 900)
