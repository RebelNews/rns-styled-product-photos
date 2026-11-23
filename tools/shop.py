"""Helpers for jobs: Shopify Admin GraphQL (client credentials grant) and Printful. Never print credentials."""
import os, time, requests
STORE = os.environ['SHOPIFY_STORE']; VER = '2026-10'
PF_STORE = '1626324'  # Rebel News store in Printful
_tok = None
def token():
    global _tok
    if not _tok:
        r = requests.post(f'https://{STORE}/admin/oauth/access_token', data={'client_id': os.environ['SHOPIFY_CLIENT_ID'], 'client_secret': os.environ['SHOPIFY_CLIENT_SECRET'], 'grant_type': 'client_credentials'}, timeout=30)
        if r.status_code != 200: raise SystemExit(f'Shopify token exchange failed: HTTP {r.status_code}')
        j = r.json(); _tok = j['access_token']; print('shopify token ok; scopes:', j.get('scope'), flush=True)
    return _tok
def gql(q, v=None):
    for a in range(8):
        r = requests.post(f'https://{STORE}/admin/api/{VER}/graphql.json', json={'query': q, 'variables': v or {}}, headers={'X-Shopify-Access-Token': token()}, timeout=90)
        if r.status_code == 429: time.sleep(3 + a * 2); continue
        r.raise_for_status(); j = r.json()
        if any((e.get('extensions') or {}).get('code') == 'THROTTLED' for e in j.get('errors') or []): time.sleep(3 + a * 2); continue
        if j.get('errors'): raise RuntimeError(str(j['errors'])[:400])
        return j['data']
    raise RuntimeError('throttled')
def pf(path, method='GET', **kw):
    for a in range(6):
        r = requests.request(method, 'https://api.printful.com' + path, headers={'Authorization': 'Bearer ' + os.environ['PRINTFUL_TOKEN'], 'X-PF-Store-Id': PF_STORE}, timeout=90, **kw)
        if r.status_code == 429: time.sleep(15 + a * 10); continue
        try: return r.status_code, r.json()
        except Exception: return r.status_code, {'text': r.text[:200]}
    return 429, {}
