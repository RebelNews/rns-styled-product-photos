"""Styled colour photos for the six Australia-only garments.

These products are published only to the AU and NZ market, so the earlier store-wide jobs (008, 009), which worked
from the storefront list, never saw them. Each has one styled hero photo, but every colour option still points at
Printful's own mock-up on a plain background. This run gives every colour its own styled photo, the same way job 009
did: colours already styled (1600 x 1600) are left alone, colours that share a photo each get their own, and a blank
Printful mock-up is asked for again rather than swapped in. Nothing is deleted here; the old Printful photos are
removed afterwards, once the new ones are checked.

  15493775229062  Defund the ABC Unisex T-Shirt
  15493775458438  Defund the ABC Women's Relaxed T-Shirt
  15493775622278  Defund the ABC Unisex Crewneck Sweatshirt
  15493775753350  Defund the ABC Unisex Hoodie
  15491570237574  Australia Stands With Israel Unisex Crewneck Sweatshirt
  15491570073734  Australia Stands With Israel Women's Relaxed T-Shirt
"""
import flatstyle

IDS = """
 15493775229062 15493775458438 15493775622278 15493775753350 15491570237574 15491570073734
""".split()
flatstyle.run(IDS, minutes=120, shared=True, skip_done=True)
