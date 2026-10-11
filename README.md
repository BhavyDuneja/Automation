# AnantaSutra Marketing OS

A private marketing system for anantasutra.com. It runs inside your AI coding assistant on your existing
subscription, so it needs no paid API key and no paid SEO, analytics or email tools.

```
competitors + your site --(Python scripts, free)--> data/ --(assistant skills)--> reports/ + content/queue/
                                                                                   │ you approve
                                                     Task Scheduler --> publish_queue.py --> LinkedIn / Instagram
```

## Commands (type in the assistant, opened in this folder)
| Command | What it does | Output |
|---|---|---|
| `/market-intel` | Shows today's competitor changes and market news, and updates the gap list | data/intel/log.md, gaps.md, reports/alerts.md |
| `/competitive-brief` | Full competitor analysis, including where competitors' audiences are | reports/competitive-brief-*.md |
| `/seo-audit` | Crawls your site and runs PageSpeed (and Search Console if set up), then gives a fix list | reports/seo-audit-*.md |
| `/aeo-geo` | Checks whether AI search can find and cite you, gives llms.txt/schema fixes, tracks visibility | reports/aeo/, data/aeo/visibility.csv |
| `/campaign-plan` | Plans a campaign, including how to reach competitors' audiences, and writes the calendar | reports/campaigns/, content/calendar.md |
| `/draft-content` | Writes LinkedIn/Instagram posts into the queue, plus blogs and pages | content/queue/, content/blog/ |
| `/brand-review` | Checks drafts against your brand voice and flags legal issues | review field in each draft |
| `/social-schedule` | Lists, plans, approves or moves posts, or shows a dry-run | content/queue/ |
| `/email-sequence` | Writes nurture or onboarding email sequences | email/sequences/ |
| `/performance-report` | Weekly or monthly report with recommendations | reports/performance-*.md |
| `/daily-run` | Runs the full daily routine (Task Scheduler runs this every morning) | reports/daily/ |

The rules and facts every skill uses live in **context/**: `brand.md`, `competitors.yaml`, `channels.md` and `aeo-prompts.md`.
Fix anything wrong there first.

## Privacy
- Skills and assistant settings live only on this PC and are kept out of git. Nothing is installed on the shared account.
- Local assistant sessions are stored on this PC, not in the shared account's chat history.
- The project settings turn off the account's connectors and forbid Artifacts, Docs, `/schedule` and Remote Control.
- Still visible to others on the account: **usage**. Your runs use up the shared 5-hour and weekly limits.
- Keep `.env` and `secrets/` private. The assistant is denied from reading them.

## One-time setup
1. **Python packages:** `python -m pip install -r requirements.txt` (already done on this PC).
2. **Config:** copy `.env.example` to `.env`.
3. **PageSpeed key (free):** Google Cloud Console → enable "PageSpeed Insights API" → create an API key → `PAGESPEED_API_KEY`.
   Without a key, Google returns a 429 rate-limit error.
4. **LinkedIn**
   - Go to https://www.linkedin.com/developers/apps → create an app (it must be linked to your company page).
   - To post as your **personal profile** (easiest), add the products "Share on LinkedIn" and "Sign In with LinkedIn using OpenID Connect".
     Get a token at https://www.linkedin.com/developers/tools/oauth/token-generator with scopes `openid profile w_member_social`.
     Put it in `LINKEDIN_ACCESS_TOKEN` and check it with `python scripts/linkedin.py whoami`.
     `LINKEDIN_AUTHOR_URN` and `LINKEDIN_API_VERSION` can stay empty: posts go to the token owner's profile, and
     the API version is picked automatically.
   - To post as the **company page**, request the "Community Management API" product (LinkedIn reviews it and
     needs business verification). Then use scope `w_organization_social` and author `urn:li:organization:<page id>`.
   - Tokens expire after about 60 days. Generate a new one when a post fails with 401.
5. **Instagram**: connected on 2026-10-09 to @anantasutra, a Business account. If it ever breaks, set
   `instagram.enabled: false` in `context/channels.md` to stop Instagram drafts and posts. Your own account doesn't need App Review or Business Verification: the app can stay in
   **Development mode**. Those are only required for other people's accounts.
   1. Switch the Instagram account to professional: Instagram app → Settings → Account type and tools → Switch to
      professional account (Business).
   2. At https://developers.facebook.com/apps, create an app with the use case "Manage messaging & content on
      Instagram". Skip connecting a business portfolio if it asks. Don't publish the app.
   3. App dashboard → App roles → Roles → Add people → **Instagram Tester** → your Instagram username.
      Accept the invite at instagram.com → Settings → Apps and websites → Tester invites.
   4. Use cases → Instagram → **API setup with Instagram login** → Generate access tokens → Add account. Log in and
      allow access, then copy the token into `IG_ACCESS_TOKEN` in `.env`. `IG_USER_ID` can stay empty.
   5. For free image hosting, create an account at https://imgbb.com, get a key at https://api.imgbb.com, and add
      `IMGBB_API_KEY=<key>` to `.env`. Instagram only accepts public JPEG links. The publisher converts your local
      image (PNG or JPG in `content/media/`) to JPEG, hosts it on ImgBB for 7 days, and then posts it.
   6. Check it with `python scripts/instagram.py whoami`, which should show `account_type` as BUSINESS or MEDIA_CREATOR.
      Then set `instagram.enabled: true`.
   The token lasts 60 days. The publisher renews it once a week and saves the new one to `.env`.
6. **Search Console + GA4 (free, for real keyword and traffic data).** GA4 is already on the site (`G-XLLGBKC9LK`),
   and the DNS already has a Google verification record.
   1. Go to https://console.cloud.google.com and create a project named `anantasutra-marketing`.
   2. Under APIs & Services → Library, enable **Google Search Console API** and **Google Analytics Data API**.
   3. Under IAM & Admin → Service Accounts, create a service account named `marketing-reader` and skip the role steps.
      Open it → Keys → Add key → Create new key → JSON, and save the file as `secrets/google-sa.json`.
      - If Google says "Service account key creation is disabled", your Workspace organization blocks keys.
      - Fix: create the project from a personal @gmail.com account instead, or turn off the org policy
        "Disable service account key creation" (that needs the Organization Policy Administrator role).
   4. In https://search.google.com/search-console, open the `anantasutra.com` property → Settings → Users and permissions → Add user.
      Enter the service-account email (`…@….iam.gserviceaccount.com`) with permission **Restricted**. Only an Owner can add users.
      - If there is no property yet, add a **Domain** property for `anantasutra.com` and verify it with the DNS TXT record it gives you.
   5. In https://analytics.google.com, go to Admin → Property access management → + → Add users, and add the same email as **Viewer**.
      Then copy the numeric **Property ID** from Admin → Property details. Don't use the `G-…` measurement ID.
   6. In `.env`, set `GSC_SITE=sc-domain:anantasutra.com` and `GA4_PROPERTY_ID=<number>`.
      If your Search Console property is a URL-prefix one, use `GSC_SITE=https://www.anantasutra.com/` instead.
   7. Test with `python scripts/google_data.py --check`, then run `python scripts/google_data.py --days 28`.
7. **Assistant CLI for the daily automation:** nothing to install. `automation/run-daily.ps1` (kept on this PC, not in
   git) finds the CLI on PATH or inside the VS Code extension, which shares your existing login. It uses a lighter model
   to go easy on the shared usage limits.
8. **Schedule it** (done on 2026-10-11): `python automation/register_tasks.py` sets up two tasks that run hidden:
   - the daily routine at 10:00 PC time, starting tomorrow (change it with `--daily-at 09:00`)
   - the publisher every 30 minutes, all day
   Remove both with `python automation/register_tasks.py --remove`.
   The laptop must be on and you must be logged in. Missed runs start when the laptop wakes up.
   This PC runs on Japan time, but post times in `content/queue/` are always IST. The scripts convert them.

## Daily flow
1. Every morning (10:00 PC time), competitors are snapshotted. The assistant then updates intel, drafts posts for empty slots and writes `reports/daily/<date>.md`.
2. You open the assistant and run `/social-schedule`. Review the drafts, add images, and say "approve ...".
3. The publisher posts approved items at their `scheduled_at` time and moves them to `content/posted/`.
4. Every Monday you get a weekly report, and on the 1st an SEO audit plus a monthly report.

## Limits to know
- Without Search Console there is no real keyword volume or ranking data. Reports label those values as estimates.
- LinkedIn post analytics need extra API approval. Export the CSV from LinkedIn analytics into `data/manual/` instead.
- Carousels and reels are drafted as slide text or scripts. You design or shoot them yourself.
- Competitor sites that block bots show up as errors in the daily log. Remove them or change their `pages` in `context/competitors.yaml`.
