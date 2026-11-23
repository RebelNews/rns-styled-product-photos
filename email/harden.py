import re,sys
src,dst=sys.argv[1],sys.argv[2]
s=open(src).read()
def rep(a,b,count=1):
    global s
    assert a in s, 'missing: '+a[:60]
    s=s.replace(a,b,count)
rep('<html lang="en">','<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">')
rep('<meta name="viewport" content="width=device-width, initial-scale=1">','<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta http-equiv="X-UA-Compatible" content="IE=edge">\n<meta name="x-apple-disable-message-reformatting">\n<meta name="format-detection" content="telephone=no,date=no,address=no,email=no,url=no">')
rep('<style>','<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->\n<style>')
rep('-webkit-text-size-adjust:100%;}','-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}')
rep('table{border-collapse:collapse;}','table{border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt;}')
rep('img{border:0;max-width:100%;height:auto;display:block;}','img{border:0;max-width:100%;height:auto;display:block;-ms-interpolation-mode:bicubic;}')
rep('a{color:#FEC70A;}','a{color:#FEC70A;}\na[x-apple-data-detectors]{color:inherit !important;text-decoration:none !important;font-size:inherit !important;font-family:inherit !important;font-weight:inherit !important;line-height:inherit !important;}')
# Outlook ignores padding on links, so the button is built from borders instead
rep('text-decoration:none;padding:15px 30px;border-radius:0;}','text-decoration:none;padding:0;border-top:15px solid #DE1F3E;border-bottom:15px solid #DE1F3E;border-left:30px solid #DE1F3E;border-right:30px solid #DE1F3E;border-radius:0;}')
rep('.rns-nav a{font-size:11px !important;padding:0 4px !important;}','.rns-nav a{font-size:10px !important;letter-spacing:.02em !important;}\n.rns-nav td{padding:0 3px !important;}')
if '.rns-nav a.rns-nav-pill{padding:3px 6px !important;}' in s: rep('.rns-nav a.rns-nav-pill{padding:3px 6px !important;}','.rns-nav td.rns-nav-pill{padding:3px 5px !important;}')
rep('</style>','</style>\n<!--[if mso]><style>body,table,td,div,p,a,span,h1,h2,strong{font-family:\'Trebuchet MS\',Arial,Helvetica,sans-serif !important;}.rns-card img{display:inline !important;}</style><![endif]-->')
rep('<div style="display:none;max-height:0;overflow:hidden;','<div style="display:none;mso-hide:all;visibility:hidden;opacity:0;max-height:0;max-width:0;overflow:hidden;')
s=s.replace('<table role="presentation"','<table role="presentation" cellpadding="0" cellspacing="0" border="0"')
# nav: one table cell per link, because Outlook ignores padding on links
m=re.search(r'(<tr><td[^>]*class="rns-nav"[^>]*>)(.*?)(</td></tr>)',s,re.S); assert m
cells=[]
for a in re.findall(r'<a [^>]*>.*?</a>',m.group(2),re.S):
    st=re.search(r'style="([^"]*)"',a).group(1); pill='rns-nav-pill' in a
    st2=re.sub(r'padding:[^;]*;?','',st); st2=re.sub(r'background:[^;]*;?','',st2)
    a2=re.sub(r'style="[^"]*"','style="'+st2+'white-space:nowrap;"',a).replace(' class="rns-nav-pill"','')
    cells.append(('<td class="rns-nav-pill" bgcolor="#FEC70A" style="padding:4px 9px;background:#FEC70A;">' if pill else '<td style="padding:0 9px;">')+a2+'</td>')
s=s[:m.start(2)]+'\n<table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center"><tr>'+''.join(cells)+'</tr></table>\n'+s[m.end(2):]
open(dst,'w').write(s); print('wrote',dst,len(s))
