---
name: ud-crew-briefing
description: "Build the branded 2-page Utter Declutter crew briefing PDF for a project from Jhen's verbal brief, using the skill's HTML template and render script. Use when Jhen briefs a job or asks for a crew briefing."
---

# UD crew briefing

A crew briefing is an **actual document**: a branded, 2-page-max Letter PDF built from `assets/template.html`, in the house style shown in `references/example-donohue.html` (Karen Donohue, Sept 2026). Jhen briefs you on the job by voice (expect transcription noise — "Fabi" = Favi, "Marzy" = Marzi, "cycling" = the declutter/sort pass); you turn it into the PDF the crew reads on their phone before they walk in. Dispatch (`sarah-dispatch`) says who, where and when; the briefing says what, how, and what not to touch.

## Files in this skill

- `assets/template.html` — the page shell and all CSS (brand kit v2b: Paper #FBF8F3, Sand #EDE3D5, Cocoa #2A2118, Bronze #814A0A, Palm tint; Plus Jakarta Sans). Placeholders: `{{LOGO}}` (auto), `{{CLIENT_NAME}}`, `{{DATE}}`, `{{START}}`, `{{ADDRESS}}`, `{{PHONE}}`, `{{CREW}}`, `{{SCOPE}}`, `{{CLOCK}}`, `{{CONTEXT}}`, `{{START_OF_DAY}}`, `{{PLAN}}`, `{{END_OF_DAY}}`.
- `assets/logo.svg`, `assets/fonts/PlusJakartaSans-*.ttf` — don't substitute.
- `scripts/fill_template.py <fields.json> <out.html>` — fills the template from a JSON of raw-HTML strings.
- `scripts/render.sh <in.html> <out.pdf>` — installs the font, renders with wkhtmltopdf (Letter, 16 mm margins), warns if over 2 pages or if a heading is orphaned at a page bottom.
- `references/example-donohue.html` — the reference for tone, density and which CSS classes to use. Read it before writing a new one.

## Before you write

1. Pull what exists: crew, dates and vehicle plan from the dispatch board / GHL `UD Jobs` calendar; client address and phone from the GHL contact on the Won opportunity; consult times from Google Calendar.
2. Missing something you can't infer? Ask **one** tight question, draft with what you have, and mark the gap in the doc.
3. Never invent scope. "He'll clarify on site" goes in verbatim.

## Document structure (always this order)

| Slot | What goes in it | Classes to use |
|---|---|---|
| Meta grid | Date(s), start time(s), address, client phone, crew by name, scope line (`2 days · 8 hours each · Declutter + Organize · No install`) | template `.meta` |
| **The clock** | Hours block: how many working hours, lunch separate, when the finish lands, whether runs are inside the hours. Banked hours owed go here. | `.clock8` |
| **Context** | Who the client is, the situation, how to handle them. Internal candor is fine but nothing you'd be embarrassed for the client to read — these get forwarded. Trouble-client jobs: name who owns the relationship on site and the script for pushback ("Let me check with Jhen"). | `h2.first` + `.alert` |
| **Big bombs** | Fragile / high-value / do-not-move items, hazards, anything that ends the job if it goes wrong. Blunt and physical, in Jhen's words ("treat them like glass"). Never omitted — if Jhen named none, write "None called out — ask the client at kickoff what we must not touch." | `.rule` (black bar) right under Context |
| **Start Of Day** | Checklist: client briefing by the lead, before photos, confirmations (donation destination, dump arrangement, what's untouchable), staging. | `ul.checks` |
| **The Plan** | Numbered `h3` sections: zones (`.zones` pills), the cycling / install / organizing approach (`.two` cards for buckets or standards), a **Where everything goes** table (`table.out`), special handling (hazardous, `.quote` for a client-facing script), runs (`.note`), supplies. Wrap any heading + first block that could split across pages in `<div style="page-break-inside:avoid">`. | as listed |
| **End Of Day** | Checklist: client walkthrough, after photos (same angles), runs done, what goes to Jhen same day. Multi-day jobs get a Day 1 line and a final-day line. | `ul.checks` |

Footer (Declutter · Install · Organize dots, `Utter Declutter LLC · 239-249-7700 · Questions on site → Jhen`) is in the template — leave it.

## Rules

- **2 pages, hard limit.** Tighten copy (clock line, context bullets, plan prose) before shrinking anything. One briefing per project, not per day.
- **Plain crew language.** Short lines, 12-hour am/pm times, no brand voice, no exclamation points.
- **Scope respects the sale.** A 2-person job is John + Kevin, full stop. "Open to installs" means the crew *recommends* and Jhen quotes — the crew never adds paid work on site.
- **Every day has a plan for trash, donate, sell, keep, hazardous.** Default runs: junk to Collier County landfill, donations to Goodwill unless the client prefers otherwise; hazardous never goes in bags, to the curb, or in a client's dump trailer.
- **Photos before and after, same angles** — always in Start and End of Day.

## Build steps

```bash
SK=<this skill's folder>
# 1. write fields.json (raw HTML per slot; see example-donohue.html for markup)
python3 $SK/scripts/fill_template.py fields.json briefing.html
bash $SK/scripts/render.sh briefing.html "Crew Briefing — <Client>.pdf"
# 2. Read the PDF pages once; fix any orphan/overflow warning; re-render.
```

## Delivery

1. Show Jhen the rendered PDF (SendUserFile) — draft-and-approve is the standing mode.
2. Save the PDF (only the PDF, never a .docx) to `Desktop/Utter Declutter/Client Documents/<Client Full Name>/Crew Briefing — <Client>.pdf`, creating the client folder if it doesn't exist.
3. Jhen distributes the PDF to the crew himself (iMessage group). Only text a crew summary from the UD number if he asks.
4. Log the durable facts (scope, big bombs, client read) in memory under the client so Re-Set visits and future jobs inherit them.