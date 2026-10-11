# AnantaSutra monthly performance report: baseline

- **Period:** Thu 10 Sep to Wed 7 Oct 2026 (28 days). **Compared with:** Thu 13 Aug to Wed 9 Sep 2026 (28 days). **Written:** Fri 9 Oct 2026 (IST).
- **Type:** first report, so this is the baseline. No earlier performance report exists, nothing has been posted, and Instagram, LinkedIn and email have no data.
- **Sources read:**
  - `data/google/google-2026-10-09.json`: Search Console + GA4, pulled by `scripts/google_data.py --days 28`, not re-run.
  - `data/seo/audit-anantasutra.com-2026-10-09.json`: the 40-page crawl (re-read after another run refreshed it; my first read saw a 1-page version).
  - `data/aeo/visibility.csv` and the first 110 lines of `reports/aeo/aeo-geo-2026-10-09.md`: the AEO baseline run today by another skill.
  - `data/intel/changes-2026-10-09.json`: merged first-run snapshot of 5 competitors (re-read).
  - `context/brand.md`, `context/channels.md` (re-read after it changed), `README.md`, and `scripts/google_data.py` (only to confirm pull limits).
  - A live check of `/contact` and `/services/dedicated-experts`: 2 WebFetch calls, 0 WebSearch.
- **Freshness:** other runs updated the audit, the AEO log and the competitor snapshot while this report was being written. It uses their state at the time of the final edit. The Google/GA4 file did not change.
- **Window:** Search Console lags about 2 days, so both Google sources end on 7 Oct.
- **Labels:** *computed* = my arithmetic on the files. *Inference* = a reasoned reading the data cannot prove. *Proposal* = a suggested target, not an agreed one.
- **Terms:** *human baseline* = sessions that are not Singapore-tagged (section 3.3). *Marketing-attributed* = sessions from every channel except Direct.

---

## 1. Executive summary

GA4 reports **885 sessions, +614% on the previous 28 days (124)**, but this is not growth. **677 sessions arrived on one day (Thu 17 Sep)**, 90% of all sessions are tagged Singapore, 96.5% are Direct, and 585 landed on the `/blog` index, which Search Console shows only 10 impressions and 0 clicks for. I treat it as automated traffic. Only **88 sessions (10%) were not Singapore-tagged**, so the human baseline is about **3 sessions a day**. Every channel marketing can influence (all except Direct) delivered **31 sessions vs 27**, which is flat. **Key events are 0 on every channel**, so no lead can be traced to any source today. Google showed the site **189 impressions and 1 click**, none for the dedicated-experts offer, and today's AEO baseline found AnantaSutra cited for **0 of 7** buyer prompts in AI search. The site audit shows a likely cause on the Google side: the flagship page and 13 other service pages declare `/services` as their canonical and share its title.

- **Headline metric:** human sessions of about 88 per 28 days (about 3.1 a day) against 885 raw. The previous period (124) cannot be cleaned the same way because country data was not pulled for it, so no human trend can be stated yet.
- **One key win:** AI assistants already send visitors (7 sessions, equal to 44% of Organic Search's 16), the founder page is the only page that earned a click (1 click on 12 impressions at position 3.3), and crawl access is open (174 sitemap URLs, `llms.txt`, 10 AI crawlers allowed, no non-200 pages or broken internal links in the 40-page audit).
- **One area of concern:** the campaign can be neither measured nor found. No conversion events exist, the flagship page has zero Google impressions (and a canonical pointing elsewhere), AI search does not cite the site, and the raw GA4 numbers are polluted. Fix measurement first.

**Three priorities** (detail in section 12):
1. **Make conversions measurable.** GA4 key events on the two `/contact` forms, plus a "Dedicated experts" option in the form dropdowns (section 4).
2. **Clean the data.** Report on a Singapore-free human view, switch on an internal-traffic filter, check host logs for edge protection (section 3.4).
3. **Make the flagship page findable.** Give it its own title, description and canonical (R3), add tracked CTAs on the posts that already rank (R4), then build a hire-intent content cluster (R6). See section 5.3.

---

## 2. Key metrics: raw vs human baseline

No targets have been agreed, so every status is "Baseline". The target column holds **proposals** (full list with reasoning in section 12.3). Every row is small-number data: from chance alone expect swings of about ±21% at 88 sessions and about ±35% at 31 sessions (*computed*, 1.96/√n).

| Metric | This period, raw | This period, human baseline | Previous period | Change | Target (proposal) | Status |
|---|---|---|---|---|---|---|
| GA4 sessions | 885 | **about 88** (upper bound) | 124 (cannot be cleaned: no country data pulled) | not comparable | at least 115 | Baseline |
| Sessions per day | 31.6 | about 3.1 | 4.4 | not comparable | about 4.1 | Baseline |
| Users (approximate) | 871 | about 73 (India 43, US 28, Japan 2) | 115 | not comparable | none | Baseline |
| Marketing-attributed sessions | 31 | 31 | 27 | +14.8% (4 sessions, within noise) | at least 45 | Baseline |
| of which Organic Search | 16 | 16 | 10 | +60% | hold at 16 or more | Baseline |
| of which AI Assistant | 7 | 7 | 8 | -12.5% | hold at 7 or more | Baseline |
| of which Organic Social | 7 | 7 | 5 | +40% | at least 20 | Baseline |
| of which Referral | 1 | 1 | 4 | -75% | at least 3 | Baseline |
| Direct sessions | 854 | not cleanable | 97 | +780% (spike) | not targeted | Baseline |
| Engagement rate | 54.4% | not cleanable (37% to 57% depending on method) | 35.5% | not comparable | none (sample too small) | Baseline |
| Key events (leads) | 0 | 0 (not tracked) | 0 | n/a | tracking live by Fri 16 Oct | Baseline |
| Search Console impressions (all pages) | 189 | n/a | not pulled | n/a | at least 10 on the flagship page | Baseline |
| Search Console clicks (all pages) | 1 | n/a | not pulled | n/a | none | Baseline |
| Search Console impressions (named queries) | 33 | n/a | 71 | -54% (one query: 50 to 13) | none | Baseline |
| Brand query impressions ("ananta sutra") | 1 | n/a | 0 visible | +1 | at least 5 | Baseline |
| AI search: buyer prompts citing anantasutra.com (7 prompts) | 0 of 7 | n/a | first run, no earlier log | n/a | at least 1 of 7 | Baseline |

Notes on the table:
- "Human baseline" sessions = 885 total minus 797 Singapore = 88 (*computed*). The daily series totals 886, which gives 89. India 49 + US 28 + Japan 12 = 89 matches.
- Users in the human column are the three country rows (43 + 28 + 2). Raw users are summed across channel rows and can double count.
- Engagement rate cannot be cleaned from the aggregates. A landing-page method (top landing pages excluding the `/blog` index and `/admin`, 107 sessions) gives 37%. A country method (India, US, Japan) gives 57%. The previous period was 35.5%. Treat the jump to 54.4% as a by-product of the spike.
- The AEO row comes from the AEO baseline (`data/aeo/visibility.csv`). Those checks use web-search summaries as a proxy for AI answer engines, so read them as approximate.

---

## 3. Traffic quality: the 17 September spike

### 3.1 Verdict

**Very likely automated traffic.** Confidence: high for the 17 Sep spike itself, medium-high that most of the other Singapore-tagged sessions share the same source. It is not proven: the file has no browser, device, city or hostname data. Step A in 3.4 is a 10-minute check that would prove it.

### 3.2 Evidence

| # | Signal | What the data shows | Reading |
|---|---|---|---|
| 1 | Shape | Thu 17 Sep: 677 sessions and 677 users, which is 76% of the 886 sessions in the daily series and 113x the median of the other days (6). The day before: 5. After: 27, 26, then 3 to 10 a day. | A one-day step with no build-up and an abrupt drop. Content that goes viral decays over days; scripts and crawlers do not. |
| 2 | Geography | Singapore: 797 sessions (90.1% of 885), 798 users, equal to 93% of the Direct count. | Singapore is not a target market in `brand.md` (India, US, UK, UAE, AU) and no marketing ran there. Singapore hosts major cloud regions, a common origin for crawlers and monitors (general knowledge, not from the file). |
| 3 | Source | Direct is 854 of 885 sessions (96.5%; 78.2% before). All other channels together: 31 (27 before). | The surge sits entirely inside Direct (visits with no referrer). Because non-Direct channels total only 31, at least 646 of the 677 spike sessions were Direct. |
| 4 | Landing page | `/blog`: 585 sessions, 584 users, 66% of all sessions. Search Console: 10 impressions and 0 clicks for `/blog` and `/blog/` combined. | No search, social or campaign path explains hundreds of visits to a blog index (`content/posted/` is empty). An index page as the entry for many one-visit users is how a crawler starts. |
| 5 | Visitor pattern | Sessions equal users: 677/677 on the day, 797/798 for Singapore, 585/584 for `/blog`. | Every visit is a brand-new visitor and nobody returns. India, by contrast, has repeat visitors (49 sessions from 43 users). |
| 6 | Engagement | Singapore 55.7% engaged. Whole site 54.4% now vs 35.5% in the previous period. | Script-driven browsers can still meet GA4's engaged-session rule (10 seconds, or 2+ page views), so a high rate does not prove people. |
| 7 | Table does not add up | The 15 country rows sum to 1,150 sessions; GA4's own totals are 885 (channels) and 886 (days). Overshoot: 265 (+30%). | GA4 counts a session under every country it appears in, so rows overshoot when a visit's IP location changes mid-session. That is typical of rotating proxy addresses (*inference*). |
| 8 | Second cluster | Brazil 88, Pakistan 32, South Africa 29, Argentina 24, Vietnam 21, Bangladesh 14, Mexico 13, Iraq 12, Russia 11, Chile 10, Ecuador 10 = 264 sessions from 264 users, 90% engaged. | Same one-visit-per-user fingerprint. Singapore + India + US + Japan add up to exactly 886, so these 11 rows have no room as separate visits. They look like the same automated sessions seen from other exit points (*inference*). |

**What looks human or internal:**
- India: 49 sessions, 43 users, 69% engaged, with repeat visitors. The most human-looking row.
- United States: 28 sessions, 28 users, 32% engaged. Could be real, could be data-centre traffic.
- Japan: 12 sessions from 2 users. Probably the team (the founder splits time between Delhi and Osaka per `brand.md`) (*inference*).
- `/admin` as a landing page: 10 sessions, 7 users. `robots.txt` disallows `/admin/`, so this is almost certainly internal use or probing.

**What would change my mind:**
- GA4 Explore (step A below) shows a normal device and browser mix and normal engagement time for 17 Sep.
- Someone on the team ran a crawler, uptime tool or load test that day. That would still be non-human traffic, just benign.
- A real campaign is very unlikely: nothing was published or promoted.

### 3.3 Cleaned baseline next to the raw numbers

| View | How it is cleaned | Sessions (28 days) | Per day | Comment |
|---|---|---|---|---|
| Raw | none (GA4 as reported) | **885** (daily series: 886) | 31.6 | Not usable. |
| Excl. 17 Sep | drop the spike day | 209 | 7.7 (27 days) | Ceiling only: at least 120 of these (57%) are still Singapore-tagged. |
| Excl. 17 to 19 Sep | drop the spike and its two elevated days | 156 | 6.2 (25 days) | Ceiling only: at least 67 of these (43%) are still Singapore-tagged. |
| **Human baseline (use this)** | **drop every Singapore-tagged session (885 - 797)** | **about 88** | **about 3.1** | Upper bound for human sessions. India 49, US 28, Japan 12. |
| Marketing-attributed | non-Direct channels only | 31 | 1.1 | Unaffected by the spike. Previous period: 27. |

How the "still Singapore-tagged" floors are derived (*computed*): at most 677 Singapore sessions can fall on 17 Sep, so at least 797 - 677 = 120 fall on other days. If 18 and 19 Sep were also entirely Singapore (27 + 26), at least 797 - 730 = 67 fall outside 17 to 19 Sep. Excluding the spike alone therefore leaves a figure of which at least 57% is Singapore-tagged.

Reading the ladder:
- **Why not 209 or 156.** Both date-based figures still contain Singapore traffic on ordinary days, so they are ceilings, not baselines. The Singapore-free count is the safer base for target-setting because it is also the rule I recommend reporting on going forward.
- **Japan.** If the 12 Japanese sessions are the team, external human sessions are about 77 (India 49, US 28).
- **Caveat.** "Human" here means "not Singapore-tagged". The US row could still hide automated visits, and a handful of real Singapore visitors would be lost. Neither changes the picture at this scale.
- **Previous period.** 124 sessions, 97 of them Direct at 34.0% engagement. It might also contain automated traffic, but the file has no daily or country split to check. Pull both next time.

### 3.4 How to handle it in GA4 going forward

**A. Confirm (10 minutes, GA4 Explore).** Free-form exploration for 10 to 20 Sep. Rows: Date, Country, City. Add Device category, Browser, Operating system, Screen resolution, Session source / medium and Hostname. Values: Sessions, Engaged sessions, Average engagement time, Event count. Signs of automation: one browser/OS/resolution combination, city "(not set)", engagement time near 0 s or exactly 10 s, and a hostname other than anantasutra.com (ghost traffic).

**B. Report on a human view; do not try to edit history.** GA4 cannot delete or reprocess past data. Save a comparison (Reports) and a segment (Explore) named "Human": Country does not exactly match Singapore. Always show Raw and Human side by side. Keep the 17 to 19 Sep dates noted in reports so nobody reads the spike as a win.

**C. Filter what GA4 can filter.**
- *Internal traffic.* Admin, Data streams, your web stream, Configure tag settings, Define internal traffic: add the Delhi and Osaka IPs. Then Admin, Data filters, Internal traffic: set it to Testing, check it in reports, then Active. Active filters cannot be undone retroactively. If IPs are dynamic, use a cookie-based `traffic_type` flag or the GA opt-out add-on instead.
- *Skip the GA tag on `/admin`.* Don't render the analytics component in the admin layout (10 `/admin` landing sessions this period).

**D. Stop the source at the edge, not in GA4.** GA4 has no country or bot data filter (only internal-traffic and developer-traffic filters). It already excludes known bots and spiders automatically, but this traffic ran JavaScript and got through. Check host or CDN logs for 17 Sep: if the same IPs or ASN hit `/blog`, add a firewall rule that challenges or rate-limits that range (Vercel Firewall or Cloudflare bot protection, whichever hosts the site; the hosting provider is not stated in the files). Prefer a challenge over a blanket Singapore block. Optional: load the GA tag after the first scroll or click. The trade-off is that quick human bounces go uncounted.

**E. Alert and rule.** Create a GA4 custom insight for a daily-sessions surge. In every future report, flag any day above 3x the median daily sessions (this period: median 6, or 6.5 counting the two zero days, so a threshold of about 18 to 20, which flags exactly 17, 18 and 19 Sep). Extending the pull to include date by country makes the human view automatic (recommendation R5).

---

## 4. Conversion tracking (priority 1)

The campaign cannot be judged without this. With about 3 human sessions a day, leads will be few, so each one has to be counted and attributed to a source.

### 4.1 What the data and the live site show

- GA4 `keyEvents` is **0 on all 5 channels in both periods**, so no event is marked as a key event, or none fires.
- Live check on 9 Oct (WebFetch summaries of the pages, **verify in code before building**):
  - `/contact` has **two forms**. "Book a Free Consultation": name, email, phone, service, date, time slot, button "Book Appointment" (built-in calendar, Asia/Kolkata). "Send us a message": name, email, service, message, button "Send Message". The audit's H2 list for `/contact` ("Book a Free Consultation", "Send us a message", "Common Questions") agrees.
  - **No WhatsApp link** (`wa.me` or `api.whatsapp.com`), no `tel:` link and no Calendly, Cal.com or other booking embed on `/contact` or the flagship page. The only WhatsApp reference is the text "Bring your preferred WhatsApp number if you want quicker coordination."
  - `mailto:contact@anantasutra.com` and `mailto:co-founder@anantasutra.com` exist.
  - Every primary CTA on the flagship page ("Get Your Expert", "Book Free Consultation", "Let's Talk") and the header "Get Started" goes to `/contact`. The funnel is flagship page, then `/contact`, then one of the two forms.
  - **The service dropdown has 9 options** (AI Voice Agents, AI Video Generators, Social Media Automation, Gmail Automation, AI Marketing Tools, Recruiter AI, Marketing Agency, Content & Shooting, Other). **"Dedicated experts" is missing**, so flagship leads would be filed as "Other" or "Marketing Agency".
  - No success message or thank-you redirect is visible in the static HTML, so fire events from the submit-success handler.
- Landing pages: `/contact` had 3 sessions (2 users) and `/services/dedicated-experts` had 3 sessions (3 users). No booking or WhatsApp page appears in the top-25 landing pages, so there is nothing to track there.
- Worth a 2-minute manual check: the fetched booking calendar showed September 2026. It may only be a static snapshot, but open `/contact` in a browser and confirm October slots can be booked.

### 4.2 Events to add

| Event | Fires when | Key event? | Why |
|---|---|---|---|
| `generate_lead` | "Send us a message" submitted successfully | **Yes** | GA4's standard lead event; usable later for Google Ads and audiences. |
| `book_consultation` | "Book Appointment" submitted successfully | **Yes** | Highest-intent action and the brand's primary CTA ("Book a free consultation"). |
| `cta_click` | Click on a primary CTA, with `cta_text` and `cta_location` | No | Measures the flagship page to `/contact` step without inflating leads. |
| `click_email` | Click on a `mailto:` link | No (make it a key event only if you want email intent counted as a lead) | The only other contact route found on the site. |
| `click_whatsapp` or booking-link click | **Not needed yet.** | n/a | No such links exist today. Add them with the WhatsApp test (E2, section 12.2) if you create them. |

Register event-scoped custom dimensions `service_interest`, `form_id` and `cta_location` so the parameters are reportable (they only collect from the moment of registration).

Each form fires exactly one key event, so a submission is never counted twice. A "lead" in reports = `generate_lead` + `book_consultation`.

### 4.3 Next.js snippet

The GA4 tag is already on the site (README), so only event calls are needed. Never send name, email or phone to GA4.

```tsx
// lib/track.ts
declare global {
  interface Window { gtag?: (...args: unknown[]) => void }
}

export function track(name: string, params: Record<string, string | number | boolean> = {}) {
  if (typeof window !== "undefined" && typeof window.gtag === "function") {
    window.gtag("event", name, params);
  }
}
```

```tsx
// "Send us a message" handler, after the request succeeds
track("generate_lead", { form_id: "contact_message", service_interest: values.service });

// "Book a Free Consultation" handler, after the booking is saved
track("book_consultation", { form_id: "contact_booking", service_interest: values.service });

// Primary CTAs: flagship hero, header "Get Started", footer "Let's Talk"
<Link href="/contact" onClick={() => track("cta_click", { cta_text: "Get Your Expert", cta_location: "dedicated_experts_hero" })}>
  Get Your Expert
</Link>
```

```tsx
// components/MailtoTracker.tsx: mount once in the root layout
"use client";
import { useEffect } from "react";
import { track } from "@/lib/track";

export default function MailtoTracker() {
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const a = (e.target as Element).closest<HTMLAnchorElement>('a[href^="mailto:"]');
      if (a) track("click_email", { link_url: a.getAttribute("href") ?? "" });
    };
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);
  return null;
}
```

If the site uses `@next/third-parties/google`, `sendGAEvent("event", "generate_lead", {...})` does the same. Adjust the import alias to your project.

### 4.4 GA4 setup and verification

1. Add "Dedicated experts" to the service dropdown on **both** forms, and use that value as `service_interest`.
2. Ship the event calls. Submit a test through each form with DebugView on (Admin, DebugView; use the Google Analytics Debugger extension) and confirm both events and their parameters arrive.
3. Admin, Key events, New key event: `generate_lead` and `book_consultation`. This works before the first event arrives.
4. Admin, Custom definitions: register the three dimensions above.
5. After 24 to 48 hours, check Reports, Engagement, Events, and compare the count against the contact inbox and booking records. Do not rely on Enhanced Measurement's automatic `form_submit`: it can fire on attempts that fail validation, and it is unreliable for JavaScript forms.
6. `scripts/google_data.py` already pulls `keyEvents`, so the next report picks the new key events up with no script change.

Timeline (*proposal*): events live by Fri 16 Oct, reconcile against the inbox by Fri 23 Oct, first full tracked month ends Fri 6 Nov.

**Lead baseline you can fill in today without tracking:** leads received 10 Sep to 7 Oct = `[ADD: count of form submissions, bookings and enquiry emails from the contact inbox / booking records]`, and the same for 13 Aug to 9 Sep.

### 4.5 Attribution for the campaign

LinkedIn posts go out from the founder's personal profile, with links in the first comment (`context/channels.md`). Clicks from the LinkedIn mobile app often arrive without a referrer and land in Direct, so tag every campaign link: `?utm_source=linkedin&utm_medium=social&utm_campaign=<post-slug>`. Keep names lowercase and consistent, and do not tag internal links. Without this, the first tracked leads cannot be tied to a post.

---

## 5. Organic search: what Google shows

Search Console returned all rows under the 50-row cap (20 pages, 14 queries), so the page list is complete for Google web search. Named queries cover only 17.5% of page impressions (33 of 189); Google hides rare queries.

**Totals:** 189 impressions, **1 click**, CTR 0.53%, impression-weighted average position 21.6. At this size one click more or less moves CTR by about half a point (1/189), so the click count is noise. The constraint is volume, not snippets, so I would not tune titles on this sample.

### 5.1 Topics, positions and fit (page level, 189 impressions)

"Fit" is my judgement against the flagship offer: vetted, dedicated domain experts placed in a client's team, paid at salary plus a transparent fee.

| Topic (pages) | Impressions | Share | Avg position | Clicks | Fit with "dedicated experts" |
|---|---|---|---|---|---|
| Social commerce in India (1 post) | 42 | 22% | 34.1 | 0 | None. D2C and social-selling readers, no hiring intent. |
| Campus recruitment / AI recruitment (2 posts) | 25 | 13% | 60.9 (campus post: 23 at 65.7; recruitment-pipeline post: 2 at 6.0) | 0 | Low. A hiring theme, but HR-tech buyers; belongs to Recruiter AI. |
| Brand: home page and `/co-founder` | 24 | 13% | 3.3 | **1** | Trust asset. The only click in the period (1 of 12 on `/co-founder`, a 1,981-word page with Person schema). |
| Color psychology / branding (1 post) | 17 | 9% | 6.5 | 0 | Low to medium. Marketing and design are expert domains. |
| Generative AI, AI marketing tools, responsible AI (3 posts) | 17 | 9% | 12.3 | 0 | Medium. AI and marketing are 2 of the 12 expert domains. |
| Video production budget (1 post) | 15 | 8% | 9.8 | 0 | Medium. Video is an expert domain; "budget" speaks to the cost pillar. |
| AI calling for e-commerce sellers (1 post) | 12 | 6% | 11.4 | 0 | Low. A product (AI voice agents), not experts. |
| Blog index and tag page (3 URLs) | 12 | 6% | 6.0 | 0 | Not applicable. |
| Google Ads cost per click, India (2 URLs: www and apex) | 11 | 6% | 26.0 | 0 | Medium. Agency-cost pain is the markup message. |
| Gmail productivity (1 post) | 7 | 4% | 4.9 | 0 | None. |
| Newsletter; Next.js vs WordPress (2 posts) | 4 | 2% | 8.2 | 0 | Low. |
| Ritualist app (subdomain) | 3 | 2% | 5.0 | 0 | None. Consumer app, different audience. |
| **Total** | **189** | 100% | 21.6 | 1 | **0 impressions are for hire-an-expert intent** |

**Position bands (pages, *computed*):** average position 10 or better for 15 pages (92 impressions, 49%), but no page in that band has more than 17 impressions; positions 10 to 20 for 2 pages (23 impressions); 20 to 50 for 2 pages (51); beyond 50 for 1 page (23). The pages with real volume (social commerce 42, campus recruitment 23) sit at positions 34 and 66. Pages on page one rank for long-tail phrases almost nobody searches.

### 5.2 Queries (named, current vs previous)

| Query | Impr. now | Position now | Impr. before | Position before |
|---|---|---|---|---|
| campus recruitment automation | 13 | 61.8 | 50 | 54.6 |
| india social commerce market | 3 | 78.3 | new | |
| social commerce india | 3 | 72.7 | new | |
| cost per click rates india | 2 | 44 | new | |
| social commerce platforms in india | 2 | 65.5 | new | |
| student recruitment automation tools | 2 | 80.5 | 1 | 65 |
| ai for campus hiring | 1 | 73 | 1 | 73 |
| ai hiring for universities | 1 | 69 | 1 | 74 |
| ai-powered campus recruitment | 1 | 72 | 1 | 69 |
| ananta sutra | 1 | 9 | new | |
| generative ai agency | 1 | 28 | new | |
| generative engine marketing india | 1 | 87 | new | |
| google ads per click cost in india | 1 | 68 | new | |
| top social listening tools for d2c brands india 2026 | 1 | 97 | new | |

- Named-query impressions fell **71 to 33 (-54%)**. One query explains it: "campus recruitment automation" went from 50 to 13 impressions and from position 54.6 to 61.8.
- Gone since last period (17 impressions): "campus hiring solution" (6 at 82), "is zapier an indian company?" (4 at 10), "indian school whatsapp group" (2 at 10), three Gmail label/filter queries (5 combined, positions 33 to 53).
- New this period: 9 queries, 15 impressions.
- Campus recruitment is 55% of named-query impressions (18 of 33) at an average position of 65.5. Social commerce is 24% (8 of 33) at 73.0.
- Only **1 of 14 queries ranks on page one**: the brand query "ananta sutra" (1 impression, position 9). 11 of 14 queries (29 impressions) are beyond position 50.
- Brand demand is almost invisible: 1 impression for the brand name, and it is spelled as two words.

### 5.3 What this says about fit with the flagship offer

1. **The offer has no search footprint, and the audit shows a likely reason.** `/services/dedicated-experts`, `/services` itself, every other `/services/*` page, `/contact`, `/portfolio` and `/testimonials` have no row in the page report: zero Google web-search impressions in 28 days. The 40-page audit (raw HTML, no JavaScript) shows that **14 of 16 audited `/services/*` pages, including the flagship, declare `https://anantasutra.com/services` as their canonical**, and that 15 pages (the hub plus those 14) share one title (81 characters) and one meta description (201 characters) that do not mention dedicated experts. Only `/services/ai-automation` and `/services/marketing` have their own metadata and a self-canonical. Google normally treats a page whose canonical points elsewhere as a duplicate of that page, so these URLs are unlikely to rank in their own right. Confirm in Search Console with URL Inspection (look at the Google-selected canonical). In Next.js a canonical set in the `/services` layout is inherited by every child page unless the page overrides it (*inference*). Is it intentional? See "Needs your input". Not one of the 14 queries or 20 pages is about hiring, embedding or renting an expert.
2. **What the site ranks for is how-to content for marketers and SME owners** (social commerce, Ads cost per click, colour palettes, video budgets). That audience wants to learn or to buy a service, not to staff a team. GA4 shows the same pattern: the most-visited blog landing pages are mostly social media, Instagram, Google Ads and WhatsApp marketing posts at 3 to 5 sessions each.
3. **The nearest bridges** are posts on pains the offer solves: Google Ads cost (agency spend), the agency business model, video budgets, AI marketing. They rank on or near page one. Whether those posts point readers to the flagship page cannot be told from the files; check, and add tracked CTAs (R4).
4. **Competitors own the buyer language.** From `data/intel/changes-2026-10-09.json` (5 tracked; Turing was dropped):
   - Uplers: "Hire Software Engineers from India | AI Recruitment Partner"
   - Toptal: "Toptal - Hire Freelance Talent from the Top 3%"
   - Flexiple: "Build Your Offshore India Team in Weeks | Flexiple"
   - Virtual Employee: "Hire Remote Staff in India - From $9/Hour", with an H2 "Not Freelancers or Project-Based Outsourcing"
   - Second Talent: a "Cost to Hire a Software Developer: Freelance Rates by Country - 2026" guide and a "Top 25 Platforms to Hire Vetted Developers Compared - 2026" page

   AnantaSutra has no presence for "hire X", "dedicated team" or "offshore team" phrasing, and no cost guide or comparison page.
5. **AI search shows the same gap** (AEO baseline, `data/aeo/visibility.csv`; web-search proxy, approximate). anantasutra.com is cited for **0 of 7 buyer prompts** (0 of 63 result links), and the brand name itself returns unrelated meanings (the Anant Chaturdashi thread, a Buddhist sutra). The answers cite vendor blogs, "Toptal alternatives" roundups, cost guides, directories (Clutch, TechBehemoths, G2) and dev.to. Those are the formats to build for (R6). The AEO report has the llms.txt, schema and entity fixes; this report does not repeat them.
6. **Candidate query themes to validate** (hypotheses; this stack has no keyword-volume data, and Search Console only shows queries we already appear for): "dedicated [role] expert India", "hire [role] without agency markup", "offshore expert team India", "staff augmentation alternative", plus one per domain (AI engineer, designer, marketer, video editor, legal, healthcare, finance, real estate).
7. **Near-term read.** With no search visibility for the offer today, early demand has to come from LinkedIn and direct outreach, while search is a slower build.

### 5.4 Hygiene findings (audit: 40 of 174 sitemap URLs, raw HTML)

- **Service-page metadata and canonicals:** see 5.3 item 1 and R3. This is the one item that blocks the flagship.
- **Title and description length:** 34 of 40 titles exceed 60 characters and 31 of 40 descriptions exceed 160.
- **Blog posts:** all 17 audited posts have two H1 tags. The `/blog` index has no H1 and only 12 words in the raw HTML (its post list is built in the browser). Blog posts also respond slowly in the audit: 1.0 to 3.9 s (median 1.3 s) against 0.1 to 0.5 s for every other page (*audit-measured server response*). No PageSpeed data exists yet.
- **Thin domain pages:** five of the expert-domain pages (e-commerce, real estate, immigration, business, academic) have 41 to 48 words in the raw HTML. These are the natural landing pages for domain-specific hire queries. The audit does not run JavaScript, so client-rendered text is not counted.
- **Duplicate hosts and URLs:** 5 pages (23 impressions) appear on `www.anantasutra.com` next to the apex host. The Google Ads post shows on both: 9 impressions at position 29.7 (www) and 2 at 9.5 (apex). `/blog` and `/blog/` both appear, and a `/blog?tag=Deal%20Closure` URL is indexed. The audit fetched www pages (200) whose canonical points to the apex; confirm www redirects to the apex with a 301.
- **Homepage:** title 76 characters, description 238, H1 is the tagline "Infinite Wisdom Applied" (does not state the offer), 1 image without alt text. Schema is Organization and WebSite only; the flagship has HowTo, ItemList and Organization but no Service or FAQPage.
- **Coverage:** `/portfolio` and `/testimonials` were not audited. No broken internal links and no non-200 pages among the 40 audited.

---

## 6. Channel summary

| Channel | Result this period | Notes |
|---|---|---|
| Organic Search (GA4) | 16 sessions, 7 users, 56.3% engaged (before: 10, 9, 70.0%) | Search Console shows 1 click. The gap means most of these sessions are from other search engines or other Google surfaces; add source / medium to the pull. 16 sessions from 7 users is also a sign of repeat visits, possibly the team. |
| AI Assistant | 7 sessions, 7 users, 28.6% engaged = 2 engaged sessions (before: 8, 6, 37.5%) | Equal to 44% of Organic Search. Landing pages unknown; the 7 visits probably land on how-to blog posts rather than hire-intent pages, since the AEO baseline finds no buyer prompt citing the site (*inference*). Technical readiness is good: `llms.txt` present and consistent with `brand.md`, 10 AI crawlers allowed except `/admin/` and `/api/`. |
| Organic Social | 7 sessions, 71.4% engaged = 5 engaged (before: 5, 20.0%) | Zero posts published, so this comes from existing profile links. Platform unknown. |
| Referral | 1 session (before: 4) | Too small to read. |
| Direct | 854 sessions | Dominated by the spike. Section 3. |
| LinkedIn | no data | `content/posted/` is empty; no CSV in `data/manual/`. Plan in `channels.md`: 4 posts a week (Tue, Wed, Thu, Sat) at 09:30 IST, published from the founder's personal profile; a 12:30 slot is a test candidate. |
| Instagram | no data | `enabled: false` in `channels.md` (Meta app verification pending); `social_insights.py` skipped. |
| Email | no data | No sends, no export. |
| Paid | none | No paid spend. Budget vs plan: not applicable. |
| Competitors | baseline only | First snapshot of 5 sites (Uplers, Toptal, Flexiple, Virtual Employee, Second Talent); no changes yet. Per the AEO report, of the tracked competitors only Toptal appears in AI answers (3 of 7 prompts), so the tracked list does not match who AI answers name. |

**Where visitors land** (GA4 top-25 landing pages, 702 of 885 sessions; the other 183 are spread over pages with 2 sessions or fewer):

| Landing group | Sessions | Notes |
|---|---|---|
| `/blog` index | 585 | The spike. Excluded from any human read. |
| Home page `/` | 37 | 34 users, 48.6% engaged. The largest real landing page. |
| Blog posts (15 posts in the top 25) | 40 | 22.5% engaged (weighted). Topics: Instagram, Google Ads, WhatsApp, AI calling, AI marketing tools, leadership. |
| Service pages | 12 | `/services/marketing` 5, `/services/ai-automation` 4, `/services/dedicated-experts` 3. |
| `/admin` | 10 | 7 users. Internal or probing. |
| `/portfolio` | 8 | 6 users, 62.5% engaged. |
| `/co-founder`, `/contact` | 3 each | `/contact`: 2 users. |
| "(not set)" | 4 | 0% engaged. |

The flagship page received 3 landing sessions (1.4% of the 209 non-spike sessions, *computed*). Visits that reach it after landing elsewhere are not visible; the pull has no page-path views.

---

## 7. Trend analysis

Four weekly points plus one earlier period are far below the 8 to 12 points needed for a trend. Everything here is directional.

| Week (Thu to Wed) | Thu | Fri | Sat | Sun | Mon | Tue | Wed | Total | Excl. 17 Sep |
|---|---|---|---|---|---|---|---|---|---|
| 10 to 16 Sep | 13 | 16 | 0 | 11 | 9 | 11 | 5 | 65 | 65 |
| 17 to 23 Sep | **677** | 27 | 26 | 3 | 6 | 3 | 5 | 747 | 70 |
| 24 to 30 Sep | 10 | 9 | 4 | 2 | 7 | 3 | 0 | 35 | 35 |
| 1 to 7 Oct | 7 | 6 | 7 | 3 | 5 | 4 | 7 | 39 | 39 |

- The days with no row in the file (Sat 12 Sep, Wed 30 Sep) are shown as 0.
- **Inflection point:** Thu 17 Sep. Cause: automated traffic (section 3).
- **Underlying level:** on ordinary days sessions averaged 9.3 a day (10 to 16 Sep) and 5.1 a day (20 Sep to 7 Oct), against 4.4 a day in the previous period. These are unfiltered by country, so they still include Singapore-tagged sessions; the human level is about 3.1 a day.
- **Seasonality:** cannot be assessed with one period of comparison.
- **Benchmarks:** none used. The files hold no benchmark of our own, and borrowed ones would not be ours.

---

## 8. What worked

1. **AI assistants already refer visitors:** 7 sessions, 44% of Organic Search. Hypothesis: the `llms.txt` file and open AI crawler access are doing their job (the AEO report rates `llms.txt` as well-formed and consistent with `brand.md`). Scale by writing answer-first pages for hire-intent questions (R6).
2. **The founder page earns trust:** `/co-founder` had 12 impressions at position 3.3 and the only click of the period (CTR 8.3%, a tiny sample). Hypothesis: people look for who is behind a service. Replicate with founder-led LinkedIn content (the posting plan already publishes from the founder's profile) and a clear link to the founder page.
3. **Open crawl access and a healthy link graph:** `robots.txt`, a 174-URL sitemap, HTTPS redirect, `llms.txt`, 10 AI crawlers allowed, and no non-200 pages or broken internal links among the 40 audited pages.
4. **Content can rank:** 15 of 20 pages average page-one positions (9 of them blog posts). Good raw material for tracked CTAs to the flagship page.
5. **Organic Social shows a pulse without a program:** 7 sessions, 5 engaged, before any post has been published (directional only).

## 9. What needs improvement

1. **No conversion measurement.** Key events are 0. *Fix:* section 4.
2. **Polluted analytics.** 90% of sessions are Singapore-tagged; engagement and Direct figures are unusable. *Fix:* section 3.4.
3. **The flagship page cannot rank as built.** Its canonical points to `/services` and its title and description are the services hub's, shared by 15 pages. *Fix:* R3.
4. **No search or AI-search presence for the offer.** 0 of 189 Google impressions; 0 of 7 AI prompts. Hypothesis: the site's content is how-to material for marketers rather than the cost guides, comparisons and directory profiles that win hire-intent answers. *Fix:* R4 and R6.
5. **Tiny search volume.** 189 impressions and 1 click in 28 days; named-query impressions down 54%. Hypothesis: the topics with volume (social commerce, campus recruitment) are crowded, and our pages sit at positions 34 and 66. *Fix:* do not invest further here (R9).
6. **The forms don't reflect the flagship.** The service dropdown has no "Dedicated experts" option. Hypothesis: the forms predate the move to the dedicated-experts positioning. *Fix:* R1.
7. **Blog quality signals.** Two H1s on every audited post, slow server responses (median 1.3 s), 22.5% engagement on blog landings. Hypothesis: slow pages contribute to the low engagement. *Fix:* R8, then measure with PageSpeed.
8. **Hosts, titles and thin pages.** *Fix:* R8 and R6.

## 10. Insights and observations

- **Wrong buyer in search, right pains.** The topics that rank point to people who want to learn marketing and AI tactics (*inference*). The pains in those posts (agency spend, Ads cost, video budgets) are the pains the transparent-fee model answers. That is a natural bridge, but only with a tracked path to the flagship page.
- **Google and AI search show the same gap.** Neither surfaces the offer. The AEO report adds that AI answers distrust vendor self-claims and that the site publishes no fee figure; a worked fee example would address the "without markup" question directly.
- **Measurement before optimisation.** At about 3 human sessions a day, conversion rate tests cannot reach significance. Month 1 is about proving the tracking and reconciling it with the inbox, not optimising.
- **Brand demand is near zero, and the name is ambiguous.** 1 visible brand-query impression, and AI search returns the Anant Chaturdashi thread and a Buddhist sutra for "AnantaSutra". LinkedIn and founder-led content, plus consistent naming ("AnantaSutra", one word) across profiles, are the likelier near-term fix.
- **Internal activity is leaking into the data:** Japan (12 sessions, 2 users), `/admin` (10 sessions) and Organic Search repeat visits (16 sessions, 7 users).
- **External factors (general, not from the files):** the Indian festive season (Navratri and Dussehra in October, Diwali in early November) usually slows B2B responses in India, so treat the next four weeks as a soft window. Competitor moves in the period: none recorded, because the competitor snapshot has just started.

---

## 11. Recommendations

### 11.1 Priority matrix

| | Low effort | High effort |
|---|---|---|
| **High impact** | **Do first:** R1 GA4 key events and dropdown option; R2 GA4 data hygiene; R3 service-page metadata and canonicals; R4 tracked CTAs on ranking posts; R5 richer data pulls | **Plan for next sprint:** R6 hire-intent search footprint; R7 edge bot protection (only if logs confirm) |
| **Low impact** | **Do if time allows:** R8 on-page and URL hygiene | **Deprioritise:** R9 more campus-recruitment and social-commerce content |

### 11.2 Detail

| ID | What to do | Why (data) | Impact | Effort | Priority |
|---|---|---|---|---|---|
| R1 | Add `generate_lead`, `book_consultation`, `cta_click`, `click_email`; mark the first two as key events; add "Dedicated experts" to both dropdowns; tag LinkedIn links with UTMs; verify with DebugView and one test per form (sections 4.2 to 4.5). | Key events are 0 on all 5 channels. The site has 2 forms and mailto links, no WhatsApp or booking link, and no flagship option in the dropdown. | High | Low (about half a day of development plus 30 minutes in GA4) | Immediate, this week |
| R2 | Confirm the spike in Explore; save a "Human" comparison (Country is not Singapore); define internal IPs and activate the internal-traffic filter; drop the GA tag from `/admin`; add the 3x-median spike rule to reports. | 797 of 885 sessions Singapore; at least 120 Singapore sessions outside 17 Sep; Japan 12 sessions from 2 users; `/admin` 10 sessions. | High | Low | Immediate, this week |
| R3 | Give every service page its own title, meta description and self-referencing canonical, starting with `/services/dedicated-experts`. Example title (53 characters, for `draft-content` and `brand-review` to refine): "Dedicated experts embedded in your team \| AnantaSutra". Add `Service` and `FAQPage` schema on the flagship, then re-request indexing and check URL Inspection. In Next.js, use per-route `generateMetadata` with `alternates.canonical`. | Audit: 14 of 16 audited service pages (flagship included) canonicalize to `/services`; 15 pages share one title and description. Search Console: no service page has a single impression. The flagship is the offer being promoted. | High | Low | Immediate, same release as R1 |
| R4 | Add tracked CTAs from the best-ranking posts to `/services/dedicated-experts`, framed as salary plus one transparent fee vs agency markup. Start with color psychology (17 impressions at 6.5), video production budget (15 at 9.8), AI calling for e-commerce sellers (12 at 11.4), generative AI and agency model (11 at 16.4), Google Ads cost per click (11 at 26.0). | 0 of 189 impressions reach the flagship; these pages already get impressions. | Medium to high | Low | Next 2 weeks (after R1 so clicks are counted) |
| R5 | Extend `scripts/google_data.py` (needs your OK; it is outside `reports/`, so I have not touched it): add average engagement time, new users, source / medium, hostname, city, device and browser, page-path views for `/contact` and the flagship page, date by country, and the previous-period daily, country, landing-page and Search Console page data. Add an optional exclude-country filter. | The cleaning here relied on arithmetic across tables that do not reconcile; the next report should filter directly. | Medium to high | Low | Before the next monthly report |
| R6 | Build the hire-intent footprint in the formats AI and Google answers cite: a cost guide ("cost to hire a dedicated [role] from India"), a "dedicated expert vs freelancer vs agency" comparison, an alternatives page, FAQs, and directory profiles (Clutch, TechBehemoths, G2). Rewrite the flagship page in buyer language and publish 4 to 6 pages for the strongest expert domains, starting by expanding the five thin domain pages. Include a worked fee example with `[ADD: coordination fee, if you are willing to publish it]`, and back the "30-50% agency markup" line with a source or soften it (the AEO report flags it as unverified). | The flagship and every money page have 0 impressions; 0 of 7 AI prompts cite the site; competitors own "hire from India", "offshore team" and cost-guide phrasing. | High | High | Next sprint (plan now, start after R1 to R4) |
| R7 | Add edge protection (challenge or rate-limit the offending ASN or IPs) if host logs show the same source on 17 Sep. | The GA tag fired, so the source runs JavaScript; GA4 cannot block it. | Medium | Medium | After the log check |
| R8 | On-page and URL hygiene: 301 www to the apex and one trailing-slash rule; canonical or noindex for `?tag=` pages; shorten titles (34 of 40 over 60 characters) and descriptions (31 of 40 over 160); one H1 per blog post; an H1 and server-rendered post list on `/blog`; the missing alt text; run PageSpeed on blog posts. | Audit and Search Console data in section 5.4. | Low to medium | Low | When convenient |
| R9 | Do not add campus-recruitment or social-commerce content for now. Revisit if Recruiter AI becomes a campaign focus. | 65 of 189 impressions (34%) on those two posts, at positions 34 and 66, zero clicks, not the flagship buyer. | Low | High | Deprioritise |

---

## 12. Next period focus (Fri 10 Oct to Fri 6 Nov 2026)

### 12.1 Top 3 priorities

1. **Make conversions measurable** (R1). Without it every campaign number in the next report stops at sessions.
2. **Clean the data** (R2, R5, then R7 if logs confirm). So the baseline and the targets mean something.
3. **Make the flagship page findable** (R3 first, then R4, then R6). A page that canonicalizes to `/services` cannot collect impressions however good the content is.

### 12.2 Experiments (directional; volumes are too low for A/B tests)

- **E1. Contextual CTA.** Add the R4 CTA to the 5 listed posts. Success measure, set before launch: `cta_click` count and flagship landing sessions after 4 weeks vs the 3 flagship landing sessions now. Compare before and after, not A/B.
- **E2. WhatsApp click-to-chat** on `/contact` and the flagship page (hypothesis: founders in India prefer WhatsApp; the contact page already asks visitors for a WhatsApp number). Run only after R1 is live, so `click_whatsapp` and form submits can be compared.
- **E3. Flagship page rewrite** for buyer language (with R3). Measure Search Console impressions and distinct queries for that page at 2 and 4 weeks (indexing lags).
- **E4. LinkedIn time slot.** `channels.md` has one 09:30 slot a day and notes that a 12:30 test may be suggested here. No change until there are at least 8 posts of data (per the skill rule); then add a 12:30 test slot on one of the four days and compare. `channels.md` is not edited without your OK.

### 12.3 Proposed targets for the next 4 weeks

**These are proposals based on this baseline, not agreed targets.** They are set above the chance bands in section 2 and assume LinkedIn posting starts and R1 to R4 ship.

| Metric | Baseline (this report) | Proposed target | Basis and confidence |
|---|---|---|---|
| GA4 key events live | 0 key events | `generate_lead` and `book_consultation` firing and marked as key events by Fri 16 Oct; a test of each form seen in DebugView | Binary. High confidence it can be done. |
| Lead reconciliation | no tracked leads; inbox count `[ADD: leads 10 Sep to 7 Oct]` | GA4 key-event count within 1 of the inbox and booking count for the window | Validates the plumbing. High confidence. |
| Service-page metadata | flagship canonical points to `/services`; title and description shared by 15 pages | Flagship has its own title, description and self-canonical, and indexing re-requested, by Fri 16 Oct | Binary. High confidence. |
| Human sessions (Singapore-free) | about 88 (3.1 a day) | at least 115 (+30%, about 4.1 a day) | +30% sits above the ±21% chance band. Low confidence. |
| Marketing-attributed sessions | 31 | at least 45 (+45%) | Above the ±35% band. Mostly Organic Social, 7 to at least 20 (first month of posting). Other channels held. Low confidence. |
| Flagship visibility in Google | 0 impressions on `/services/dedicated-experts` and on all service, contact and portfolio pages | at least 10 impressions on the flagship page and at least 3 distinct hire-intent queries visible | Indexing lag of weeks; depends on R3. Medium-low confidence. |
| Brand search | 1 visible impression | at least 5 impressions on queries containing "anantasutra" or "ananta sutra" | Follow-on from LinkedIn activity. Low confidence. |
| AI search visibility | 0 of 7 buyer prompts cite anantasutra.com; brand prompt returns unrelated meanings; AI Assistant 7 sessions | Re-run the same prompts: at least 1 of 7 cites anantasutra.com, or the brand prompt names the company; AI Assistant sessions at least 7 | AI citations move slowly. Low confidence. |
| Data hygiene | no filter, no human view | Internal-traffic filter Active, "Human" comparison saved, spike rule used in the next report | Binary. High confidence. |

### 12.4 Next review

Re-run `python scripts/google_data.py --days 28` on or after Mon 9 Nov 2026 and compare against this baseline. The automated monthly run on 1 Nov would cover only about 3 weeks of the new period (3 to 30 Oct).

---

## 13. Data missing and inputs needed

| Source | Status | How to fill |
|---|---|---|
| Instagram insights | Not connected (`enabled: false`, Meta verification pending); `social_insights.py` skipped | Set Instagram up once verified. |
| LinkedIn page and post analytics | No CSV or XLSX; `data/manual/` does not exist; nothing posted | Export from LinkedIn analytics into `data/manual/` once posts are live. |
| Email tool exports | None | Add exports when a sequence runs. |
| Posting history | `content/posted/` and `content/queue/` empty | Starts when the first approved posts go out. |
| AEO visibility | Present, first run only (8 prompts, no trend) | Re-run `/aeo-geo` after the fixes to get a trend. |
| PageSpeed | No `data/seo/pagespeed-*.json` | Run `scripts/pagespeed.py` (blog posts first; see R8). |
| Market intel log | `data/intel/log.md` and `gaps.md` do not exist; only the merged first-run snapshot | Run `/market-intel`. |
| Leads and revenue | Not in the stack | `[ADD: leads and any revenue by source from the inbox / booking records]` |
| GA4 detail | Not pulled: average engagement time, new users, pageviews, source / medium, hostname, city, device, page-path views; previous-period daily, country and landing pages; Search Console previous-period pages | R5. |
| Site audit coverage | 40 of 174 URLs; `/portfolio` and `/testimonials` not audited | Extend the `site_audit.py` page list. |

**Needs your input:**
1. Did anyone on the team, or a tool (uptime monitor, SEO crawler, load test), hit the site on 17 Sep? This settles the verdict.
2. Is the canonical on the service pages pointing to `/services` intentional (for example to consolidate thin pages)? If not, R3 fixes it.
3. Team IP addresses (Delhi, Osaka) for the internal-traffic filter, or confirm they are dynamic.
4. Lead counts for both periods from the inbox (`[ADD: ...]` above).
5. OK to extend `scripts/google_data.py` (R5)?
6. Which host or CDN serves the site (Vercel, Cloudflare, other)? It makes R7 specific.
7. Should Recruiter AI get its own campaign? That decides whether the campus-recruitment content is worth reviving.

---

## Appendix A: data notes

- **Pull limits** (`scripts/google_data.py`): channels and daily rows are complete; landing pages are the top 25 by sessions (cut-off row: 2 sessions); countries are the top 15 (cut-off: 10 sessions); Search Console rows are capped at 50 and fewer came back. Search Console is web search only (script default). The previous period has channels and queries only.
- **Totals differ slightly:** channel total 885, daily total 886 (1 session; attribution and processing). Zero-session days (12 Sep, 30 Sep) have no row.
- **Country rows are not additive** (1,150 vs 885). Use them for shares and patterns, not for sums. The Singapore-free count (885 - 797) is valid regardless of how sessions are split: it is all sessions minus all sessions that touched Singapore.
- **Users** in the channel table are summed across channels and may double count; the daily-user sum counts a person once per day.
- **GA4 organic vs Search Console:** 16 organic sessions vs 1 Google click. Different sources and scopes (GA4 includes other search engines; Search Console here is web search only; Search Console days follow Pacific time).
- **Search Console positions** are impression-weighted averages over tiny samples (most rows have 1 to 3 impressions). Read them as ranges, not exact ranks.
- **Site audit:** a raw-HTML crawl without JavaScript, 40 of 174 URLs. Canonical, title and word-count findings describe the HTML as served; rendered pages may differ, which is why URL Inspection is the check.
- **AEO figures** come from another skill's web-search proxy (US-centric, one query per prompt), not from direct checks of ChatGPT, Claude, Perplexity or Gemini. I read the CSV and the first 110 lines of its report only.
- **Live-site facts** come from two WebFetch calls, where a small model summarises the page. Verify in the code before building (form handlers, dropdown options, link targets).
- **Files changed during this run** (by other skills, not by me): the site audit, `data/aeo/visibility.csv`, `reports/aeo/`, the competitor snapshots and `context/channels.md`. Their file times use the PC clock (Japan time), not IST.
- **Computations** were done with a throwaway Python script outside the project; formulas are stated in the text. The only project file I created is this report. No third-party connector or publishing tool was used.

## Appendix B: raw tables

**Countries, top 15 (GA4, 28 days)**

| Country | Sessions | Users | Sessions per user | Engagement |
|---|---|---|---|---|
| Singapore | 797 | 798 | 1.00 | 55.7% |
| Brazil | 88 | 88 | 1.00 | 92.0% |
| India | 49 | 43 | 1.14 | 69.4% |
| Pakistan | 32 | 32 | 1.00 | 87.5% |
| South Africa | 29 | 29 | 1.00 | 93.1% |
| United States | 28 | 28 | 1.00 | 32.1% |
| Argentina | 24 | 24 | 1.00 | 75.0% |
| Vietnam | 21 | 21 | 1.00 | 90.5% |
| Bangladesh | 14 | 14 | 1.00 | 92.9% |
| Mexico | 13 | 13 | 1.00 | 92.3% |
| Iraq | 12 | 12 | 1.00 | 100% |
| Japan | 12 | 2 | 6.00 | 66.7% |
| Russia | 11 | 11 | 1.00 | 81.8% |
| Chile | 10 | 10 | 1.00 | 90.0% |
| Ecuador | 10 | 10 | 1.00 | 100% |

**Search Console pages (all 20 rows, 28 days)**

| Page | Impressions | Clicks | Position |
|---|---|---|---|
| /blog/social-commerce-india-brands-sell-directly-through-social-media | 42 | 0 | 34.1 |
| /blog/ai-campus-recruitment-automate-hiring-indian-colleges | 23 | 0 | 65.7 |
| /blog/color-psychology-marketing-choosing-right-palette-indian-brand | 17 | 0 | 6.5 |
| /blog/video-production-budget-guide-indian-smes-quality-within-budget | 15 | 0 | 9.8 |
| / | 12 | 0 | 3.3 |
| /co-founder/ | 12 | 1 | 3.3 |
| /blog/flipkart-amazon-sellers-ai-calling-boost-repeat-purchases | 12 | 0 | 11.4 |
| /blog/generative-ai-changing-indian-marketing-agency-business-model | 11 | 0 | 16.4 |
| www: /blog/reduce-google-ads-cost-per-click-india-50-percent | 9 | 0 | 29.7 |
| /blog | 9 | 0 | 7.7 |
| www: /blog/gmail-filters-labels-ultimate-organization-system-professionals | 7 | 0 | 4.9 |
| /blog/responsible-ai-practices-define-successful-indian-companies | 3 | 0 | 5.7 |
| www: /blog/ai-marketing-tools-2026-complete-guide-indian-businesses | 3 | 0 | 4.0 |
| ritualist.anantasutra.com/ | 3 | 0 | 5.0 |
| /blog/build-newsletter-people-want-to-read | 2 | 0 | 7.0 |
| /blog/nextjs-vs-wordpress-choosing-right-platform-business-website | 2 | 0 | 9.5 |
| /blog/reduce-google-ads-cost-per-click-india-50-percent | 2 | 0 | 9.5 |
| www: /blog/ai-powered-recruitment-pipeline-job-posting-to-offer | 2 | 0 | 6.0 |
| www: /blog?tag=Deal%20Closure | 2 | 0 | 1.0 |
| /blog/ | 1 | 0 | 1.0 |
