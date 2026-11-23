# Rebel News Store email templates

- `christmas_promo_v3.html` is the NationBuilder theme "Rebel News Store - Christmas Promo v1".
- `snippets.txt` holds the body snippets to paste into an email (the same text sits in a Liquid comment at the bottom of each theme, which is not sent to recipients).
- `build.py` builds the theme and the snippets; `body.py` builds a whole email body from product handles, pulling live titles, prices and first images from the store.
- `inline_body.js` converts a body written with the old class-based snippets into the inline form.

Two rules that keep Gmail, Outlook and Apple Mail working:

1. Never put a font name in quotes, in a theme or in a body. NationBuilder re-wraps the HTML at about 72 characters and will split `'Trebuchet MS'` across two lines. That is invalid CSS, and Gmail then discards every shared style in the email.
2. Every body element carries its own `style="..."`. Shared styles in the theme are only a fallback and the phone layout.
