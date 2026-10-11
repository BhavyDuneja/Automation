---
sequence: lead-nurture
doc: setup-checklist
status: draft
created: 2026-10-09
---

# Setup checklist: lead nurture sequence

Use this in any email tool. Nothing in this folder sends email by itself: you, or your email tool, do the sending. Tick items as you go.

## 0. Fill the blanks first

- [ ] Fill every placeholder in the email files (full list in overview.md, section 6): the fee, the worked example, the employment model, the pause terms, the replacement terms, what the Awish number measures, and the Awish story.
- [ ] Check none are left. From the project folder, in PowerShell: `Select-String -Path email\sequences\lead-nurture\email-0*.md -Pattern "\[ADD:"`. It should print nothing.
- [ ] Two more blanks live in this checklist: `[ADD: sender address]` (step 2) and `[ADD: postal address]` (step 3).

## 1. Choose your tool (all have a free option)

| Option | Good when | Watch out for |
|---|---|---|
| Brevo free tier | You want a trigger plus wait steps (an automation) at no cost, and expect more than a few leads a week | Free-plan limits and the automation features included change over time, so check the current pricing page first. Free plans often add the tool's branding to the footer |
| MailerLite free tier | You prefer a simple editor and an easy automation builder | The same checks: confirm the free plan still includes multi-step automation with waits, and enough contacts and monthly sends for your volume |
| Gmail plus a simple sheet (Google Sheets, or a local Excel or CSV file) | You get only a few leads a week and want every email to feel fully personal | You send by hand: Email 1 within the hour, then reminders for Days 3, 8, 14 and 21. There is no automatic unsubscribe, so add the line yourself (step 3) |

Rule of thumb: start with Gmail and a sheet if you cannot imagine more than a handful of leads a week. Move to Brevo or MailerLite when you can no longer send Email 1 within the hour by hand.

## 2. Sender setup (the sender-address requirements)

- [ ] From name: "Bhavya from AnantaSutra" (a real person plus the brand). Plain, no emoji.
- [ ] From address: a real mailbox on your own domain, `[ADD: sender address]`. Do not use a free webmail address such as @gmail.com for tool-sent mail. Most tools, including Brevo and MailerLite, now expect a domain you can authenticate, and mail sent through a third-party tool from a free webmail address is likely to be rejected or land in spam.
- [ ] Authenticate the domain: add the SPF and DKIM records the tool shows you to your domain's DNS, add a DMARC record if you have none (a monitoring-only policy is a safe start), and wait until the tool shows the domain as verified. Gmail and Yahoo expect senders to authenticate their mail. Decide who manages DNS for anantasutra.com before you start.
- [ ] Reply-To: the same mailbox, read by a human every working day. Never use a no-reply address, because Emails 1, 4 and 5 invite replies.
- [ ] Send yourself a test from the tool and confirm the From name and address look right on your phone.

## 3. Compliance basics (unsubscribe, address, consent)

- [ ] Unsubscribe: every email must carry a working unsubscribe link. The tool adds it in the footer; do not remove or hide it. Gmail route: add this line to your signature instead: "If you would rather not hear from me, reply with 'unsubscribe' and I will remove you."
- [ ] Postal address: every commercial email needs a physical postal address in the footer, `[ADD: postal address]`. Tools ask for one in the account or sender settings and print it automatically, and laws such as CAN-SPAM expect it.
- [ ] Honour opt-outs straight away. Never re-import someone who unsubscribed; keep a suppression or do-not-email list.
- [ ] Keep the From name and subject lines honest (no fake "Re:" or "Fwd:").
- [ ] Consent: collect and record each lead's consent to receive these emails when they fill the form (India's DPDP Act; GDPR/CAN-SPAM for overseas leads).
- [ ] Footer text to set once in the tool (the unsubscribe link is inserted by the tool):

```
Bhavya Duneja · AnantaSutra · [ADD: postal address]
You are receiving this because you asked about a free consultation at anantasutra.com.
Unsubscribe: {the tool's unsubscribe link}
```

## 4. Audience and trigger

- [ ] Create a group, list or audience named "Lead nurture - contact form". Only people who contacted you go in. Never import bought or scraped lists.
- [ ] Fields to keep: email, first name, company (optional), source, date submitted, consent (yes or no, and the date).
- [ ] Decide how a form submission reaches the tool. Three options: (a) add each lead by hand within working hours (fine at low volume); (b) use the tool's own signup form, or have a developer send submissions to the tool through its API or a webhook; (c) forward the form's notification email into the tool if it supports that. Note what happens out of hours: auto-send needs auto-add, otherwise Email 1 goes out the next morning (IST).
- [ ] Decide what a lead sees at /contact. It must let them pick or request a time. If it is only the enquiry form, add a free booking page (for example Cal.com or Calendly's free plan; check current limits) or change the Email 1 CTA to "reply with two or three times".
- [ ] Add the filter from overview.md, section 4: do not enrol vendors, recruiters, job-seekers, spam, test entries, app enquiries or AI-tool enquiries.
- [ ] Create these groups or tags for exits: `consult-booked`, `replied`, `client`, `nurture-complete`, `dormant-leads`, `do-not-email`.

## 5. Build the automation

1. Create an automation or workflow named "Lead nurture".
2. Trigger: a contact joins the group "Lead nurture - contact form".
3. Send Email 1 immediately (no delay).
4. Wait 3 days, then send Email 2.
5. Wait 5 days, then send Email 3.
6. Wait 6 days, then send Email 4.
7. Wait 7 days, then send Email 5.
8. Final step: add the tag `nurture-complete`, add the contact to `dormant-leads`, and remove them from the active group.
9. Exit rule: stop the automation when a contact is added to `consult-booked`, `replied`, `client` or `do-not-email`. If your tool has no exit setting, add a "still in the active group?" check before every email.
10. Optional: a weekday-only send window, around 10:00 IST.
11. Confirm the tool suppresses unsubscribes, bounces and spam complaints automatically (most do).

## 6. Paste the emails

- [ ] Open each `email-0N.md`. Copy only the "Body (copy from here)" section, never the notes.
- [ ] Use the simplest editor your tool has (rich text or plain text, not the drag-and-drop designer). No images, buttons or banners.
- [ ] Subject: option A. Preview text: from the frontmatter. Keep B and C for the A/B tests.
- [ ] Merge tag: map `{{first_name}}` to your tool's syntax (for example Brevo `{{ contact.FIRSTNAME }}`, MailerLite `{$name}`; check in the editor) and set the fallback to "there" if the tool offers one.
- [ ] CTA link: paste the raw URL or hyperlink the anchor text, and add tracking: `?utm_source=email&utm_medium=nurture&utm_campaign=lead-nurture&utm_content=email-0N` (replace N with the email number).
- [ ] Signature: keep the two-line signature as written. Do not add images or a logo.
- [ ] Turn on open and click tracking so you can see the metrics in overview.md, section 8.

## 7. Test before going live

- [ ] Add two test contacts: one on your own Gmail and one on another provider.
- [ ] Temporarily shorten the waits to a few minutes and run the whole flow. Check: arrival in the inbox (not spam or promotions), the mobile view, merge tags, every link, and that the unsubscribe link works.
- [ ] Reply from a test contact to confirm replies reach your inbox.
- [ ] Restore the real waits (3, 5, 6, 7 days) and double-check them.
- [ ] Search the five email files for the placeholder marker once more (step 0).

## 8. Run it day to day

- [ ] Daily (5 minutes): make sure new submissions are in the tool within the hour, read replies, and move anyone who booked or replied into the exit group.
- [ ] If a lead clicked the CTA but has not booked in 2 days, send the personal nudge (overview.md, section 4).
- [ ] Keep a follow-up sheet for "later" replies: name, the month they gave, the date you promised to follow up.
- [ ] Every Friday for 4 weeks, then monthly: fill in the metrics row (overview.md, section 8) and save the tool's export in `data/manual/`.
- [ ] If more than one or two people mark an email as spam, pause the automation and review who you are enrolling.

## 9. Gmail plus sheet variant (low volume)

- [ ] Sheet columns: name, email, company, date submitted, consent, Email 1 sent, Email 2 due, Email 3 due, Email 4 due, Email 5 due, status (active, booked, replied, client, stopped), notes.
- [ ] Due dates from the date submitted: Email 2 = +3 days, Email 3 = +8, Email 4 = +14, Email 5 = +21.
- [ ] Save each email as a Gmail template (turn on Templates in Gmail's settings, Advanced tab). Use Schedule send for Emails 2 to 5, with a calendar reminder on each due date.
- [ ] Send to one lead per message, never as a Bcc blast. Add the unsubscribe line and your postal address to your signature (step 3).
- [ ] Change the status to booked, replied or stopped the moment it happens, and stop sending to that person.

## Go-live gate

- [ ] No placeholders left in the five email files.
- [ ] Sender domain verified; From and Reply-To mailbox working and monitored.
- [ ] Unsubscribe link and postal address in the footer.
- [ ] Consent recorded for every contact in the group.
- [ ] The test run passed end to end, with the real waits restored.
- [ ] You can answer a reply or a booking within one working day.
