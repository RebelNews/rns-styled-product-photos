import re, json, html, textwrap, urllib.request, sys
FONT = "Trebuchet MS,Arial,Helvetica,sans-serif"
A = "https://assets.nationbuilder.com/themes/6b033dd441324004ff0ce0f4/attachments/original/"

# ---------- body snippets (every style inline; no quoted CSS strings) ----------
def hero(link, img, alt):
    return ('<p style="margin:0 0 20px;"><a href="%s" style="text-decoration:none;">'
            '<img src="%s" width="528" alt="%s" style="display:block;width:100%%;max-width:100%%;height:auto;border:0;"></a></p>' % (link, img, html.escape(alt)))
def h1(t): return '<h1 style="margin:0 0 14px;font-family:%s;font-size:30px;line-height:34px;font-weight:800;letter-spacing:.01em;text-transform:uppercase;color:#FFFFFF;">%s</h1>' % (FONT, t)
def h2(t): return '<h2 style="margin:28px 0 12px;padding:0 0 0 10px;border-left:4px solid #DE1F3E;font-family:%s;font-size:21px;line-height:25px;font-weight:800;letter-spacing:.02em;text-transform:uppercase;color:#FFFFFF;">%s</h2>' % (FONT, t)
def p(t): return '<p style="margin:0 0 16px;font-family:%s;font-size:16px;line-height:25px;color:#E4E6E8;">%s</p>' % (FONT, t)
def strong(t): return '<strong style="color:#FFFFFF;">%s</strong>' % t
def btn(link, t):
    return ('<p style="margin:6px 0 22px;text-align:center;"><a class="rns-btn" href="%s" style="display:inline-block;background-color:#DE1F3E;'
            'color:#FFFFFF;font-family:%s;font-size:16px;line-height:20px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;'
            'border-top:14px solid #DE1F3E;border-bottom:14px solid #DE1F3E;border-left:28px solid #DE1F3E;border-right:28px solid #DE1F3E;">%s</a></p>' % (link, FONT, t))
def card(c):
    note = ('<p style="margin:0 0 8px;font-size:13px;line-height:19px;color:#B4B8BC;">%s</p>' % c['note']) if c.get('note') else ''
    return ('<td class="rns-col rns-card" width="50%%" align="center" valign="top" style="width:50%%;padding:8px 7px 24px;text-align:center;font-family:%s;font-size:15px;line-height:20px;color:#FFFFFF;">'
            '<a href="%s" style="text-decoration:none;"><img src="%s" width="250" alt="%s" style="display:block;width:100%%;max-width:250px;height:auto;margin:0 auto;border:0;"></a>'
            '<p style="margin:10px 0 4px;font-family:%s;font-size:15px;line-height:20px;font-weight:700;color:#FFFFFF;">%s</p>'
            '<p style="margin:0 0 8px;font-family:%s;font-size:15px;line-height:20px;font-weight:700;color:#FEC70A;">%s</p>%s'
            '<p style="margin:0;font-family:%s;font-size:13px;line-height:18px;"><a class="rns-shop" href="%s" style="font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#FFFFFF;text-decoration:none;border-bottom:2px solid #DE1F3E;">Shop &rarr;</a></p></td>'
            % (FONT, c['link'], c['img'], html.escape(c['name']), FONT, html.escape(c['name']).replace('T-Shirt','<span style="white-space:nowrap;">T-Shirt</span>'), FONT, c['price'], note, FONT, c['link']))
def row(a, b=None):
    cells = card(a) + (card(b) if b else '<td class="rns-col" width="50%" style="width:50%;">&nbsp;</td>')
    return '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:collapse;"><tbody><tr>' + cells + '</tr></tbody></table>'
def box(t, sub=None, kind='deadline'):
    bg, bd, subc = ('#0C2A1A', '2px solid #2F8F4E', '#C9E7D3') if kind == 'deadline' else ('#15181C', '2px dashed #FEC70A', '#B4B8BC')
    s = ('<br><span style="font-size:13px;line-height:19px;font-weight:400;letter-spacing:0;color:%s;">%s</span>' % (subc, sub)) if sub else ''
    return ('<table role="presentation" width="100%%" cellpadding="0" cellspacing="0" border="0" style="width:100%%;border-collapse:collapse;margin:0 0 18px;"><tbody><tr>'
            '<td align="center" bgcolor="%s" style="background-color:%s;border:%s;padding:14px 12px;text-align:center;font-family:%s;font-size:17px;line-height:23px;font-weight:700;letter-spacing:.02em;color:#FFFFFF;">%s%s</td></tr></tbody></table>'
            % (bg, bg, bd, FONT, t, s))
def divider():
    return '<p style="margin:26px 0;"><img src="%s1795374562/xmas_divider_snowflakes.png" width="528" alt="" style="display:block;width:100%%;max-width:100%%;height:auto;border:0;"></p>' % A

SNIPPETS = '''HERO IMAGE:
%s

HEADLINE:
%s

SECTION HEADING:
%s

PARAGRAPH (bold a phrase with %s):
%s

BUTTON:
%s

TWO-UP PRODUCT ROW (repeat the whole table for more rows):
%s
Optional one-line description under the price: <p style="margin:0 0 8px;font-size:13px;line-height:19px;color:#B4B8BC;">SHORT DESCRIPTION</p>

DISCOUNT CODE BOX (gold dashed):
%s
''' % (hero('LINK','IMAGE_URL','DESCRIPTION'), h1('HEADLINE'), h2('SECTION HEADING'), strong('PHRASE'), p('ONE OR TWO SENTENCES ABOUT THE STORY BEHIND THE DESIGN.'),
       btn('LINK','Shop the collection'),
       row({'link':'LINK','img':'IMAGE_URL','name':'PRODUCT NAME','price':'$39 CAD'},{'link':'LINK','img':'IMAGE_URL','name':'PRODUCT NAME','price':'$39 CAD'}),
       box('Use code CODE for 15% off until DATE', kind='code'))
XMAS_SNIPPETS = '''CHRISTMAS: ORDER-BY DEADLINE BOX (green; use the right date for the audience, e.g. Dec. 10 for Canada, 5 December for Australia):
%s

CHRISTMAS: SNOWFLAKE DIVIDER (between sections):
%s
''' % (box('&#10052;&#xFE0E; Order by DATE for Christmas delivery','Made to order and printed near you'), divider())
RULES = '''HOW TO USE: paste snippets into the email body in HTML/source view, then replace the CAPS placeholders.
Every snippet carries its own styling on purpose. Gmail throws away shared styles when NationBuilder re-wraps the email, so nothing here relies on them.
Two rules when editing: (1) keep the style="..." text on each tag exactly as it is; (2) never put a font name in quotes anywhere in an email or theme.
Add ?utm_source=nationbuilder&utm_medium=email&utm_campaign=CAMPAIGN_NAME to every store link so sales show up in Shopify.
'''

MSO = '''<!--[if mso]>
<noscript><xml><o:OfficeDocumentSettings>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings></xml></noscript>
<style>
body,table,td,div,p,a,span,h1,h2,strong{
font-family:Trebuchet MS,Arial,sans-serif !important;
mso-hyphenate:none;}
.rns-card img{display:inline !important;}
a.rns-shop{text-decoration:underline !important;}
</style>
<![endif]-->'''
STYLE = '''<style>
:root{color-scheme:dark;supported-color-schemes:dark;}
body{margin:0;padding:0;background:#040707;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}
table{border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt;}
img{border:0;-ms-interpolation-mode:bicubic;}
a{color:#FEC70A;}
a[x-apple-data-detectors]{color:inherit !important;text-decoration:none !important;}
.rns-body{font-family:FONT;font-size:16px;line-height:25px;color:#E4E6E8;}
.rns-body p{margin:0 0 16px;}
.rns-body h1{font-size:30px;line-height:34px;margin:0 0 14px;font-weight:800;text-transform:uppercase;color:#FFFFFF;}
.rns-body h2{font-size:21px;line-height:25px;margin:28px 0 12px;font-weight:800;text-transform:uppercase;color:#FFFFFF;}
.rns-body img{max-width:100%;height:auto;}
@media only screen and (max-width:620px){
.rns-wrap{width:100% !important;}
.rns-pad{padding:22px 16px !important;}
.rns-col{display:block !important;width:100% !important;}
.rns-nav a{font-size:10px !important;letter-spacing:.02em !important;}
.rns-nav td{padding:0 3px !important;}
.rns-nav td.rns-nav-pill{padding:3px 5px !important;}
.rns-logo{width:250px !important;}
.rns-body h1{font-size:25px !important;line-height:29px !important;}
.rns-merry{font-size:17px !important;}
.rns-btn{font-size:15px !important;border-left-width:16px !important;border-right-width:16px !important;}
}
</style>'''.replace('FONT', FONT)

def xmas_theme():
    s = open('/home/claude/rns-styled-product-photos/email/christmas_promo_v2.html').read()
    s = re.sub(r'<!--\[if mso\]><noscript>.*?<!\[endif\]-->\n', '', s, flags=re.S)
    s = re.sub(r'<style>.*?</style>\n<!--\[if mso\]>.*?<!\[endif\]-->', lambda m: STYLE + '\n' + MSO, s, count=1, flags=re.S)
    s = s.replace("'Futura PT','Jost','Trebuchet MS',Arial,Helvetica,sans-serif", FONT)
    s = s.replace('font-size:16px;line-height:1.55;color:#E4E6E8;">\n{{ body }}', 'font-size:16px;line-height:25px;color:#E4E6E8;">\n{{ body }}')
    notes = ('{% comment %}\nCHRISTMAS VERSION of "Rebel News Store - Merch Promo v1" (updated Nov 23, 2026).\n' + RULES + '\n' + SNIPPETS + '\n' + XMAS_SNIPPETS +
             '\nThe garland, candy-cane stripe, mistletoe sign-off and snow footer are built into the theme; nothing to paste for those.\nSwitch back to "Rebel News Store - Merch Promo v1" after Christmas.\n{% endcomment %}')
    s = re.sub(r'<!--\nCHRISTMAS VERSION.*?-->', lambda m: notes, s, flags=re.S)
    s = re.sub(r"url\('([^' ]+)'\)", r'url(\1)', s)
    a = '<table role="presentation" cellpadding="0" cellspacing="0" border="0" class="rns-wrap" width="600" bgcolor="#0A0B0D" style="width:600px;max-width:600px;background:#0A0B0D;">'
    assert a in s
    s = s.replace(a, '<!--[if mso]>\n<table role="presentation" width="600" align="center"\ncellpadding="0" cellspacing="0" border="0"><tr><td>\n<![endif]-->\n<table role="presentation" cellpadding="0" cellspacing="0" border="0" class="rns-wrap" width="100%" align="center" bgcolor="#0A0B0D" style="width:100%;max-width:600px;margin:0 auto;background-color:#0A0B0D;">')
    z = '</table>\n</td></tr></table>\n{% comment %}'
    assert z in s
    s = s.replace(z, '</table>\n<!--[if mso]>\n</td></tr></table>\n<![endif]-->\n</td></tr></table>\n{% comment %}')
    assert "'" not in re.sub(r"url\('[^' ]+'\)", '', s.split('{% comment %}')[0]), 'quote left'
    return s

def nbwrap(s, width=72):
    """Imitate NationBuilder's mailer: break long lines at spaces, even inside attributes and CSS."""
    out = []
    for line in s.split('\n'):
        while len(line) > width:
            i = line.rfind(' ', 0, width + 1)
            if i <= 0:
                i = line.find(' ', width)
                if i < 0: break
            out.append(line[:i]); line = line[i+1:]
        out.append(line)
    return '\n'.join(out)

if __name__ == '__main__':
    open('christmas_promo_v3.html','w').write(xmas_theme())
    open('snippets.txt','w').write(RULES + '\n' + SNIPPETS + '\n' + XMAS_SNIPPETS)
    print(len(xmas_theme()))
