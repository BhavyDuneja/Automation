# Channels & Posting Rules

```yaml
timezone: Asia/Kolkata     # every scheduled_at is IST; the scripts convert (this PC runs on Japan time)
auto_approve: false        # true = drafts go straight to "approved" and auto-post. Keep false until you trust the output.
linkedin:
  enabled: true
  post_as: personal profile of the founder (Bhavy D., urn:li:person:GymYBFJHOD)
  company_page: anantasutra-digital    # posting as the page needs Community Management API approval
  token_renew_by: 2026-12-01           # tokens last ~60 days; this one assumed created 2026-10-09
  posts_per_week: 4
  days: [Tue, Wed, Thu, Sat]
  time_slots: ["09:30"]                # one post per listed day; performance-report may suggest testing 12:30
instagram:
  enabled: true                        # connected 2026-10-09 (Business account; tested up to an unpublished container)
  handle: anantasutra
  posts_per_week: 4
  days: [Mon, Wed, Fri, Sun]
  time_slots: ["19:30"]                # one post per listed day, IST
draft_horizon_days: 3      # daily-run keeps this many days of drafts ready in content/queue
max_drafts_per_daily_run: 2
```

## Content mix (per 2 weeks)
| Pillar (see brand.md) | Share | LinkedIn formats | Instagram formats |
|---|---|---|---|
| Education: hiring & team-building insights | 35% | text post, document carousel | carousel, quote card |
| Proof: placements, client outcomes, numbers | 25% | story post | carousel, reel script |
| POV / thought leadership (agency vs dedicated expert, AI in teams) | 20% | text post | reel script |
| Offer / CTA (start in 7 days, transparent fee) | 10% | short post + link | single image |
| Culture / wisdom (sutra-of-the-week, behind the scenes) | 10% | text post | single image, story |

## Platform notes
- LinkedIn posts publish from the founder's personal profile: write in first person as the founder, with
  AnantaSutra mentioned naturally — personal lessons and opinions, not corporate "we" announcements.
- LinkedIn: hook in the first 2 lines (before "see more"); 900-1,300 characters; 3 hashtags max; links hurt reach — put the link in the first comment manually or end with "link in comments".
- Instagram: every post needs an image. Save PNG/JPG files in `content/media/` and set `image` (or `images` for a 2-10 slide carousel); the publisher converts them to JPEG and hosts them via ImgBB. Caption ≤ 2,200 chars, first line is the hook, 5-10 hashtags at the end. The tool drafts carousel slide text and reel scripts in `visual_brief`; you design them (e.g. Canva). Reels are posted by hand for now.
