// Converts a Rebel News Store email body written with the old class-based snippets
// into the inline-styled form that survives Gmail, Outlook and Apple Mail.
// Usage in the NationBuilder email editor console:  rnInline(tinymce.editors[0].getContent())
window.rnInline = function (html) {
  var FONT = 'Trebuchet MS,Arial,Helvetica,sans-serif';
  var d = new DOMParser().parseFromString('<div id="r">' + html + '</div>', 'text/html');
  var r = d.getElementById('r'), R = {cards: 0, btns: 0, h1: 0, h2: 0, p: 0, hero: 0, boxes: 0, dividers: 0, rows: 0, other: []};
  function S(el, css) { el.setAttribute('style', css); }
  function swap(el, tag, css) { var n = d.createElement(tag); n.innerHTML = el.innerHTML; S(n, css); el.parentNode.replaceChild(n, el); return n; }
  function align(el) { var m = /text-align:\s*(center|right|left)/i.exec(el.getAttribute('style') || ''); return m ? 'text-align:' + m[1].toLowerCase() + ';' : ''; }
  // product cards
  [].slice.call(r.querySelectorAll('td.rns-card')).forEach(function (td) {
    R.cards++;
    td.setAttribute('align', 'center'); td.setAttribute('valign', 'top'); td.setAttribute('width', '50%');
    S(td, 'width:50%;padding:8px 7px 24px;text-align:center;font-family:' + FONT + ';font-size:15px;line-height:20px;color:#FFFFFF;');
    [].slice.call(td.querySelectorAll('img')).forEach(function (i) {
      if (!i.getAttribute('width')) i.setAttribute('width', '250');
      S(i, 'display:block;width:100%;max-width:250px;height:auto;margin:0 auto;border:0;');
      if (i.parentNode.tagName === 'A') S(i.parentNode, 'text-decoration:none;');
    });
    [].slice.call(td.querySelectorAll('.rns-name')).forEach(function (e) { swap(e, 'p', 'margin:10px 0 4px;font-family:' + FONT + ';font-size:15px;line-height:20px;font-weight:700;color:#FFFFFF;'); });
    [].slice.call(td.querySelectorAll('.rns-price')).forEach(function (e) { swap(e, 'p', 'margin:0 0 8px;font-family:' + FONT + ';font-size:15px;line-height:20px;font-weight:700;color:#FEC70A;'); });
    [].slice.call(td.querySelectorAll('.rns-note')).forEach(function (e) { swap(e, 'p', 'margin:0 0 8px;font-family:' + FONT + ';font-size:13px;line-height:19px;color:#B4B8BC;'); });
    [].slice.call(td.querySelectorAll('a.rns-shop')).forEach(function (a) {
      S(a, 'font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#FFFFFF;text-decoration:none;border-bottom:2px solid #DE1F3E;');
      if (a.parentNode === td) { var p = d.createElement('p'); S(p, 'margin:0;font-family:' + FONT + ';font-size:13px;line-height:18px;'); td.replaceChild(p, a); p.appendChild(a); }
    });
    var t = td.closest('table');
    if (t && !t.getAttribute('data-rn')) { t.setAttribute('data-rn', '1'); R.rows++; t.setAttribute('width', '100%'); t.setAttribute('cellpadding', '0'); t.setAttribute('cellspacing', '0'); t.setAttribute('border', '0'); S(t, 'width:100%;border-collapse:collapse;'); }
  });
  [].slice.call(r.querySelectorAll('table[data-rn]')).forEach(function (t) { t.removeAttribute('data-rn'); });
  // boxes
  [['rns-deadline', '#0C2A1A', '2px solid #2F8F4E', '#C9E7D3'], ['rns-code', '#15181C', '2px dashed #FEC70A', '#B4B8BC']].forEach(function (b) {
    [].slice.call(r.querySelectorAll('div.' + b[0])).forEach(function (div) {
      R.boxes++;
      [].slice.call(div.querySelectorAll('span')).forEach(function (sp) { S(sp, 'font-size:13px;line-height:19px;font-weight:400;letter-spacing:0;color:' + b[3] + ';'); sp.parentNode.insertBefore(d.createElement('br'), sp); });
      var t = d.createElement('table'); t.setAttribute('width', '100%'); t.setAttribute('cellpadding', '0'); t.setAttribute('cellspacing', '0'); t.setAttribute('border', '0');
      S(t, 'width:100%;border-collapse:collapse;margin:0 0 18px;');
      t.innerHTML = '<tbody><tr><td align="center" bgcolor="' + b[1] + '" style="background-color:' + b[1] + ';border:' + b[2] + ';padding:14px 12px;text-align:center;font-family:' + FONT + ';font-size:17px;line-height:23px;font-weight:700;letter-spacing:.02em;color:#FFFFFF;">' + div.innerHTML + '</td></tr></tbody>';
      div.parentNode.replaceChild(t, div);
    });
  });
  // headings, buttons, dividers
  [].slice.call(r.querySelectorAll('h1')).forEach(function (e) { R.h1++; S(e, 'margin:0 0 14px;font-family:' + FONT + ';font-size:30px;line-height:34px;font-weight:800;letter-spacing:.01em;text-transform:uppercase;color:#FFFFFF;' + align(e)); });
  [].slice.call(r.querySelectorAll('h2')).forEach(function (e) { R.h2++; S(e, 'margin:28px 0 12px;padding:0 0 0 10px;border-left:4px solid #DE1F3E;font-family:' + FONT + ';font-size:21px;line-height:25px;font-weight:800;letter-spacing:.02em;text-transform:uppercase;color:#FFFFFF;'); });
  [].slice.call(r.querySelectorAll('a.rns-btn')).forEach(function (a) {
    R.btns++;
    S(a, 'display:inline-block;background-color:#DE1F3E;color:#FFFFFF;font-family:' + FONT + ';font-size:16px;line-height:20px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;text-decoration:none;border-top:14px solid #DE1F3E;border-bottom:14px solid #DE1F3E;border-left:28px solid #DE1F3E;border-right:28px solid #DE1F3E;');
    if (a.parentNode.tagName === 'P') { a.parentNode.setAttribute('data-rn', 'btn'); S(a.parentNode, 'margin:6px 0 22px;text-align:center;'); }
  });
  [].slice.call(r.querySelectorAll('img.rns-divider')).forEach(function (i) {
    R.dividers++; S(i, 'display:block;width:100%;max-width:100%;height:auto;border:0;');
    if (i.parentNode.tagName === 'P') { i.parentNode.setAttribute('data-rn', 'div'); S(i.parentNode, 'margin:26px 0;'); }
    else { var p = d.createElement('p'); S(p, 'margin:26px 0;'); i.parentNode.replaceChild(p, i); p.appendChild(i); p.setAttribute('data-rn', 'div'); }
  });
  // paragraphs and hero images outside cards
  [].slice.call(r.querySelectorAll('p')).forEach(function (p) {
    if (p.getAttribute('data-rn')) { p.removeAttribute('data-rn'); return; }
    if (p.closest('td')) return;
    var img = p.querySelector('img'), text = p.textContent.replace(/\s+/g, '');
    if (img && !text) {
      R.hero++; S(p, 'margin:0 0 20px;'); S(img, 'display:block;width:100%;max-width:100%;height:auto;border:0;');
      if (img.parentNode.tagName === 'A') S(img.parentNode, 'text-decoration:none;');
    } else { R.p++; S(p, 'margin:0 0 16px;font-family:' + FONT + ';font-size:16px;line-height:25px;color:#E4E6E8;' + align(p)); }
  });
  [].slice.call(r.querySelectorAll('img')).forEach(function (i) { if (!i.closest('td') && !i.closest('p')) { R.hero++; S(i, 'display:block;width:100%;max-width:100%;height:auto;border:0;margin:0 0 20px;'); } });
  [].slice.call(r.querySelectorAll('strong')).forEach(function (s) { if (!s.closest('td')) S(s, 'color:#FFFFFF;'); });
  [].slice.call(r.querySelectorAll('ul,ol')).forEach(function (l) { S(l, 'margin:0 0 16px;padding:0 0 0 22px;font-family:' + FONT + ';font-size:16px;line-height:25px;color:#E4E6E8;'); R.other.push(l.tagName); });
  [].slice.call(r.querySelectorAll('a')).forEach(function (a) { if (!a.getAttribute('style')) { S(a, 'color:#FEC70A;'); } });
  [].slice.call(r.children).forEach(function (c) { if (['P', 'H1', 'H2', 'TABLE', 'UL', 'OL'].indexOf(c.tagName) < 0) R.other.push(c.tagName + (c.className ? '.' + c.className : '')); });
  R.unstyled = [].slice.call(r.querySelectorAll('[class*="rns-"]')).filter(function (e) { return !e.getAttribute('style'); }).map(function (e) { return e.tagName + '.' + e.className; });
  R.quotes = (r.innerHTML.match(/style="[^"]*'[^"]*"/g) || []).length;
  return {html: r.innerHTML, report: R};
};
