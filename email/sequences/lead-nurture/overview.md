---
sequence: lead-nurture
type: "Lead nurture (inbound)"
status: draft
created: 2026-10-09
emails: 5
duration: "21 days (Day 0 to Day 21)"
sender: "Bhavya Duneja, founder; first person; plain-text style"
goal: "Book or confirm the free 30-minute consultation"
cta_url: https://anantasutra.com/contact
audience: "Founders and team leads who submitted the /contact form or asked for the free consultation and have not started an engagement"
sources: "context/brand.md (voice, proof points, claims that need care); reports/competitive-brief-2026-10-09.md (differentiators, objections)"
---

# Lead nurture: inbound founders and team leads

Folder: `email/sequences/lead-nurture/` · drafted 2026-10-09 (IST) · nothing has been sent and every email is `status: draft`.
Files: `email-01.md` to `email-05.md` (paste-ready bodies, plus notes that must not be pasted) and `setup-checklist.md` (tool setup, compliance basics, testing).

## 1. Strategy

**Narrative arc.** You asked for a conversation. Email 1 says exactly what it involves. Email 2 helps you work out which kind of help you need. Email 3 answers what it costs and who employs the expert. Email 4 shows one real result. Email 5 makes an honest last ask and offers an easy "not now". Each email removes one reason a warm lead stalls.

**Journey map**

| Email | Stage | Barrier it removes |
|---|---|---|
| 1 | Decision (logistics) | "I don't know what happens next" |
| 2 | Consideration | "Do I need an agency, a freelancer or a dedicated expert?" |
| 3 | Consideration to decision | "What does it cost, who employs them, and what if it goes wrong?" |
| 4 | Decision | "Does this work for a business like mine?" |
| 5 | Decision | "Busy, undecided or not now" |

**Escalation logic.** Information first, then proof, then a direct ask. The CTA is the same in every email and only the framing changes. There is no fake urgency, deadline or scarcity (brand voice: honest, not salesy). The gaps taper (3, 5, 6, 7 days) because interest is highest right after the form.

**Success definition.** Primary: the lead books or confirms the free consultation. Secondary: any reply, including "later", which moves the lead to a personal follow-up. An unsubscribe is a valid, honest outcome.

**Format.** Plain-text style: first person from Bhavya, no images, no buttons, one link per email (the CTA), a short signature. The only merge tag is `{{first_name}}` (fallback "there"). The email tool adds the unsubscribe link and postal address in the footer (setup-checklist.md, step 3).

## 2. Sequence overview

| # | Subject line (option A) | Purpose | Timing | Primary CTA | Condition |
|---|---|---|---|---|---|
| 1 | Your free consultation: what happens next | Confirm the enquiry, set out the four steps, get the call confirmed | Day 0, within 1 hour of the form | Confirm your free 30-minute consultation: /contact | New real-buyer enquiry, not suppressed |
| 2 | Agency, freelancer or dedicated expert? | Handle the "which kind of help" objection honestly | Day 3 (+3 days) | Book your free 30-minute consultation: /contact | Still in sequence |
| 3 | What it costs, and who employs the expert | Handle cost, employer, lock-in and replacement | Day 8 (+5 days) | Book your free 30-minute consultation: /contact | Still in sequence |
| 4 | What a Delhi clinic did in 60 days | Proof (Awish Clinic); soft CTA by reply | Day 14 (+6 days) | Book your free consultation: /contact (soft: reply) | Still in sequence |
| 5 | The last email in this series | One direct ask, easy "not now", graceful close | Day 21 (+7 days) | Book your free consultation: /contact | Still in sequence |

"Still in sequence" means: has not booked or confirmed, has not replied, has not unsubscribed, is not a client. Every `/contact` link is `https://anantasutra.com/contact`.

**Timing rules.** Email 1 sends immediately. For Emails 2 to 5 use weekdays only if your tool allows it, around 10:00 IST by default; if most of your leads are overseas, pick a time that lands in their morning. A drift of a day or two is fine; do not shorten the gaps or add emails.

**Subject lines.** Each email has three options in its frontmatter (clear, curious or personal). On phones, inboxes show roughly the first 30 to 40 characters of a subject (it varies by device), so every option puts the key words first. Preview text (40 to 90 characters) fills the rest of the line and adds context instead of repeating the subject.

## 3. Flow diagram

```
[TRIGGER] Real buyer submits the /contact form or asks for the free consultation
    |
    v
Email 1   Day 0, within 1 hour     "what happens next", confirm the call
    |
    |   at any point: books | replies | becomes a client | unsubscribes
    |        --> [EXIT] stop the automation; you handle them personally
    |
    |   clicked the CTA but no booking after 2 days
    |        --> [TASK] send the personal nudge (automation continues)
    v
  wait 3 days
    v
Email 2   Day 3                    agency vs freelancer vs dedicated expert
    v
  wait 5 days
    v
Email 3   Day 8                    what it costs, who employs the expert
    v
  wait 6 days
    v
Email 4   Day 14                   Awish Clinic story + soft CTA (reply)
    v
  wait 7 days
    v
Email 5   Day 21                   one direct ask, easy "not now"
    |
    +--> replied "later"  --> [FOLLOW-UP SHEET] with the month they gave
    |
    +--> no action        --> [EXIT: sequence complete]
                              tag nurture-complete, move to "Dormant leads"
                              (a re-engagement sequence can pick them up later)
```

## 4. Branching, exit, re-entry and suppression

**Exit conditions (leave the sequence at once)**
- Books or confirms the consultation: tag `consult-booked`, then follow your pre-call routine.
- Replies to any email: pause the automation, tag `replied`, answer personally.
- Becomes a client: tag `client` (use onboarding instead).
- Unsubscribes, bounces or marks an email as spam: suppress permanently.

**Branches (kept few on purpose, because the list will be small)**
- Clicked the CTA but did not book within 2 days: you get a task to send the personal nudge below. The automation continues.
- Replied "later" at any point: add the lead to your follow-up sheet with the month they gave. No more automated emails from this sequence.
- Do not branch on opens. Apple Mail privacy features and image proxies inflate them, so treat opens as directional and branch on clicks and replies.
- No opens or clicks across Emails 1 to 3: keep Emails 4 and 5, but check the address for typos and test where your emails land (inbox, promotions or spam).

Personal nudge (send by hand): "Hi {{first_name}}, did the booking link work for you? If it is easier, reply with a couple of times and I will confirm one. Bhavya"

**Re-entry**
- Finished the sequence without booking: may enter once more if they submit the form again, but not within 90 days of finishing (a suggested figure; adjust to taste).
- Submits the form again while still in the sequence: do not restart it; reply personally.
- Booked earlier and asks again: handle personally.

**Suppression (do not enrol, or pause, if the person)**
- is already a client or in an active proposal or onboarding conversation (one sequence at a time);
- replied to you or spoke to you in the last 48 hours (pause until you decide);
- unsubscribed, bounced, complained, or is on your do-not-email list;
- is not a buyer: vendor pitches, recruiters, job-seekers, spam, test entries;
- is asking about the apps (Ritualist, Granthas: a separate consumer voice) or the AI tools (voice agents, Recruiter AI: a different offer). Answer these personally;
- has no recorded consent to receive these emails (setup-checklist.md, step 3).

## 5. Objections, facts used and what is left out

**Objections handled** (from the competitive brief, section 7.7)

| Objection | Handled in | Answer used | Status |
|---|---|---|---|
| Which kind of help do I need? | Email 2 | Honest three-way comparison, including when we are not the answer | Ready |
| Is this really cheaper than an agency? | Email 3 | Salary and fee as separate lines plus a worked example; no "cheaper" claim | Needs the fee and the worked example |
| Who employs the expert, and who handles payroll, PF and TDS? | Email 3 | The employment model | Needs the employment model |
| Am I locked in? | Emails 1 and 3 | No lock-in, scale up or pause anytime; some providers set a 6-month minimum | Needs the pause terms |
| What if the person is a bad fit? | Email 3 | 48-hour replacement guarantee | Needs the replacement terms |
| Will they understand my domain? | Emails 1 and 4 | 2-3 hand-picked experts, you interview and choose; Awish Clinic | Needs the Awish details |
| Who is accountable? | Emails 1 and 2 | One accountable point of contact, weekly reviews, monthly reports | Ready |

**Facts used and where they come from**

| Fact in the emails | Emails | Source |
|---|---|---|
| 30-minute call, then 2-3 hand-picked and vetted experts; you interview and choose | 1, 4, 5 | brand.md (How it works) |
| Expert joins your team (Slack, WhatsApp, stand-ups); "live in about 7 days" | 1, 5 | brand.md; the site's own wording, with no start-date promise |
| Weekly reviews, monthly reports, one accountable point of contact | 1, 2, 4 | brand.md |
| Actual salary plus one transparent fee; no recruitment fee; no lock-in; scale up or pause anytime | 1, 3 | brand.md (Model) |
| 48-hour replacement guarantee (the phrase only; terms are a placeholder) | 3 | brand.md |
| 12+ domains, from engineering and AI to legal and healthcare | 2 | brand.md |
| Clients across 4 continents | 4 | brand.md, marked safe to quote |
| Awish Clinic, dermatology, Delhi: ₹25 lakh to ₹40 lakh a month in 60 days | 4 | brand.md, marked safe to quote (what it measures is a placeholder) |
| An agency may bill ₹1.5 lakh for an expert it pays ₹1 lakh | 3 | brand.md, "Claims that need care": an illustration, never a statistic |
| Some providers set a 6-month minimum | 3 | Competitive brief 2026-10-09 (one rival's contract terms, left unnamed). Re-check before sending |

**Left out on purpose**
- The Zoom Wheels, Royal Properties and BotWot figures and the homepage "Numbers That Speak" stats (brand.md marks them unconfirmed).
- "30-50% agency markup" as a statistic.
- The word "small" for the fee, and any claim of being cheaper or "the best".
- A trial or free-trial offer (undecided; brief section 12.8).
- Competitor names and prices in the email copy (they appear only in the notes).
- Any start-date promise beyond "live in about 7 days".

## 6. Placeholders to fill before activating

Search the email files for `[ADD:`. None may remain in the five email files when you switch the automation on.

| # | Placeholder | Where | What to supply |
|---|---|---|---|
| 1 | `[ADD: fee]` | email-03 | The fee: flat amount or percentage, in ₹ or $, and what it covers. Do not guess (brief, section 12.1) |
| 2 | `[ADD: worked example …]` | email-03 | A salary-plus-fee example using the real fee |
| 3 | `[ADD: employment model …]` | email-03 | Who employs the expert, and who handles payroll, PF/TDS and the contract (brief, section 12.3) |
| 4 | `[ADD: pause terms …]` | email-03 | Notice period, if any, and what happens to billing |
| 5 | `[ADD: replacement terms …]` | email-03 | How long after the start the 48-hour guarantee applies, and any conditions (brief, section 12.2) |
| 6 | `[ADD: what the number measures …]` | email-04 | What ₹25 lakh to ₹40 lakh a month measures, for example monthly revenue |
| 7 | `[ADD: Awish story …]` | email-04 | 2-3 factual sentences: the need, the expert role placed, what they did |
| 8 | `[ADD: sender address]` | setup-checklist | The From and Reply-To mailbox on your own domain |
| 9 | `[ADD: postal address]` | setup-checklist | The postal address for the email footer |

Decisions that are not placeholders: what a lead sees at /contact (can they pick or request a time?), how form submissions reach the email tool, and who manages DNS for anantasutra.com.

## 7. A/B tests

Change one thing at a time and run one test at a time. With fewer than about 100 recipients per variant, treat the result as a hint, and adopt a winner only if it also wins on clicks or replies, not just opens.

| # | Email | What to test | Variants | Split | Winner measured by |
|---|---|---|---|---|---|
| 1 | Email 1 | Subject line | A "Your free consultation: what happens next" vs B "A quick note from Bhavya at AnantaSutra" | 50/50, alternating by enrolment order or the tool's A/B feature | Clicks on the CTA within 48 hours, then replies; opens only as a tie-breaker |
| 2 | Email 3 | CTA wording | A "Book your free 30-minute consultation" vs B "Bring your role and budget to a free call" | 50/50 | Click rate, then bookings |
| 3 | Emails 2 to 4 | Send time | Morning (10:00) vs late afternoon (17:00) in the lead's time zone, or in IST if you cannot segment | 50/50 | Click rate. Run it only after tests 1 and 2 are done and volume allows |

## 8. Metrics and benchmarks

Primary conversion: consultations booked or confirmed, as a share of leads who entered the sequence.

| Metric | How to calculate | Reference range (lead nurture) | Note |
|---|---|---|---|
| Open rate | Unique opens / delivered | 20-30% | Directional only; privacy features inflate opens |
| Click-through rate | Unique clicks on the CTA / delivered | 3-7% | The main engagement signal |
| Conversion | Consultations booked / leads entered | 2-5% | Generic nurture range. Your leads asked for a consultation, so aim materially higher and set your own baseline after the first 30 leads or so |
| Unsubscribe rate | Unsubscribes / delivered | Below 0.5% | |
| Spam complaints | Complaints / delivered | As close to zero as possible | If more than one or two people complain, pause and review who you enrol |
| Replies | Replies / delivered | No benchmark | In plain-text founder emails, replies are often the best signal |
| Time to book | Days from the form to the booking | n/a | |
| Drop-off point | The last email a lead engaged with before exiting | n/a | Shows which email to rewrite first |
| Downstream | Show-up rate; consultations that become engagements | n/a | The real goal |

The reference ranges come from the email-sequence skill's lead-nurture benchmarks. They are rules of thumb, not AnantaSutra data, and a small list will swing wildly week to week.

**Review cadence.** Every Friday for the first 4 weeks (15 minutes), then monthly. Log one row per week: leads entered, Email 1 sent within 1 hour (yes/no count), delivered, unique opens, unique clicks, replies, booked, unsubscribes, complaints. Save the tool's export in `data/manual/` (create the folder) so `/performance-report` can include it.

## 9. After this sequence

Natural companions: a pre-call prep email for leads who book (what to bring: the role, a budget range, a timeline; it can reuse the answers from Email 3), a proposal follow-up, a dormant-lead re-engagement sequence (it receives everyone who finishes Email 5 without booking), and new-client onboarding.

Possible next requests: revise any email's tone, add a branch for a specific scenario, write a variant for a segment (for example clinics or real-estate firms), or draft the B and C subject-line variants as full test cells.
