# Styled product photo tools

- `styled.py` cuts a flat Printful mock-up off its white background and places it on one of the 24 backgrounds in `bg/`.
  The background is chosen per garment colour for contrast, with a preference for backgrounds that fit the product's campaign, and is rotated so all 24 get used.
  On-model photos are detected and skipped. White garments use a segmentation model (rembg / u2net).
- `mkjobs.py` builds the job list from the store's public product data.
- `up.py` uploads finished images to Shopify staged upload targets.

Images are swapped in place with the Admin API `fileUpdate` mutation (`originalSource`), which keeps the media ID, variant links and gallery order.
