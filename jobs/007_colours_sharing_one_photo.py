"""Follow-up to job 006 for the 50 colours it skipped.

A. 14 Christmas products where Black, Navy and Dark Grey Heather / Forest Green variants all point at one photo.
   For each product the log first prints LINKS (how those colours are linked now) and PLAN (which photo each will get).
   The first colour keeps the shared photo; each other colour takes one of the spare Printful preview photos that no
   variant uses, and its variants are re-pointed to it. If there is no spare photo, a new one is added. Nothing is deleted,
   and a product's lead photo is never replaced.
B. 9 women's tees where Printful returned a blank Forest Green mock-up. The colour is requested again on its own; it is
   swapped only if the design is on it, and up to three blank results are saved to results/mockups/ for inspection."""
import flatstyle
SHARED = {
 '15489701347462': ['Black', 'Navy', 'Dark Grey Heather'], '15490828796038': ['Black', 'Navy', 'Dark Grey Heather'],
 '15489704231046': ['Black', 'Navy', 'Forest Green'], '15490828861574': ['Black', 'Navy', 'Dark Grey Heather'],
 '15489704132742': ['Black', 'Navy', 'Dark Grey Heather'], '15489703968902': ['Black', 'Navy', 'Dark Grey Heather'],
 '15490828828806': ['Black', 'Navy', 'Dark Grey Heather'], '15489704067206': ['Black', 'Navy', 'Dark Grey Heather'],
 '15489703772294': ['Black', 'Navy', 'Forest Green'], '15490828959878': ['Black', 'Navy', 'Forest Green'],
 '15489703936134': ['Black', 'Navy', 'Dark Grey Heather'], '15490828992646': ['Black', 'Navy', 'Forest Green'],
 '15489703870598': ['Black', 'Navy', 'Forest Green'], '15489704001670': ['Black', 'Navy']}
BLANK = {p: ['Forest Green'] for p in ('15491578888326', '15491579117702', '15491579379846', '15491579674758', '15491579936902',
                                        '15491580231814', '15491580493958', '15491580756102', '15491581051014')}
only = dict(SHARED, **BLANK)
print('products', len(only), '| colours', sum(len(v) for v in only.values()), flush=True)
flatstyle.run(list(only), minutes=85, only=only, shared=True)
