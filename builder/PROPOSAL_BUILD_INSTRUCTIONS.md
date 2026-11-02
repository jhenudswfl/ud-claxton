# How To Build An Utter Declutter Proposal — Step By Step

This is the exact working procedure. Follow it in order for every proposal. The rules layer (money gate, firewall, naming) lives in the `utter-declutter-client-docs` skill and the project CLAUDE.md — this file is the mechanics.

## Step 0 — Environment (once per session)

```bash
cd /tmp && npm install @fontsource/playfair-display @fontsource/montserrat   # template @font-face points at /tmp/node_modules
pip install weasyprint pymupdf --break-system-packages
```

## Step 1 — Gather client data (never invent)

1. Google Calendar: search the client's first AND last name across recent weeks. The consult event carries phone, email, and address (`location` field). Calendar/GHL spelling is authoritative over Jhen's dictation ("Beile" not "Beal").
2. GoHighLevel: `ghl_search_contacts` for city + ZIP and custom fields; `ghl_get_conversation_messages` when Jhen references something the client texted (spouse emails, preferences).
3. If the address lacks city/ZIP: verify by web search of the street name. Never guess.

## Step 2 — Lock the numbers (the gate)

You need, from Jhen or the pricing sheet: total, deposit, balance, scope/spaces, materials list, crew/days, and dates (dates are usually TBD → render "Scheduled Upon Deposit"). Standard deposit = 100% materials + 50% labor, but ASK when unstated — he varies it constantly. Batch every open question into ONE AskUserQuestion round with sensible option defaults. His answers ARE the confirmation gate. Verify deposit + balance = total before proceeding; flag any mismatch instead of fixing it silently.

## Step 3 — Pick the base template

All in `Templates/` and `Templates/Variants/` (all use assets in `Templates/assets/` — repoint the image paths to wherever you copy them):

| Job type | Start from |
|---|---|
| Standard garage declutter+install+organize, materials incl. | `Variants/proposal_saigh.html` (photos, materials table, deposit/balance) |
| Itemized prices requested | `Variants/proposal_clarke.html` (priced line items + allowance + 3-part terms) |
| Install-only (no declutter/organize) | `Variants/proposal_bartolacci.html` (rewritten narrative/guarantee) |
| Two options, sign-today pricing | `Variants/proposal_bourk.html` |
| Three options w/ Best Value badge | `Variants/proposal_anne.html` (also has custom-plan pages inline) |
| Hourly + optional add-on | `Variants/proposal_kahn.html` |
| Shopping/accessory list | `Variants/tavares_list.html` |
| Canonical 6-page reference | `Templates/proposal_template.html` + `TEMPLATE_SPEC.md` |

Photo rules: garage jobs keep the before/after page (jay/jenn pairs); non-garage jobs drop the whole Transformation page; slatwall-focused jobs may use `slat_jay.jpg`/`slat_ksenia.jpg`. Team photo always stays on the closing page.

## Step 4 — Swap client data

Copy the base HTML to a working file and swap with **exact-match string replacement, asserting every match**:

```python
r = [("old exact string", "new string"), ...]
for a, b in r:
    assert a in src, "MISSING: " + a[:60]   # a failed silent swap ships another client's data
    src = src.replace(a, b)
```

Swap: client name + address (cover), quote number (check the Client Proposals folder for the last used number and increment), issued date (today) and valid-through (+30 days), materials table rows, investment total + label, deposit/balance rows and their sub-captions, timeline values, and any scope headline. Everything else — canonical copy, guarantee, next steps, team section — stays verbatim unless the job type demands rewritten language (install-only, organize-only, purge & pack, hourly). Space names follow Jhen's words, not the sheet ("Man Cave"). Discounts get their own gracious italic line under the total (e.g. military discount "with our thanks for your service").

Image prep for any new photo: PIL `ImageOps.exif_transpose` → thumbnail 1600px → JPEG q85. WeasyPrint ignores `object-fit`, so pre-crop paired photos to the same aspect ratio or they render at different heights.

## Step 5 — Render and VERIFY (never skip)

```python
from weasyprint import HTML
HTML("working.html").write_pdf("Out.pdf")
```

Then, every time:
1. **Page count** matches expectation.
2. **Numbers present** — extract text with pymupdf and assert the total, deposit, and balance strings appear. (Letter-spaced uppercase text defeats substring checks — dates, "Best Value", quote numbers in the cover meta must be verified visually instead.)
3. **Leak sweep** — assert the text does NOT contain: the previous client's name/address/amounts from the base template, and never "markup", "commission", "cost" (standalone), internal SKUs, margins.
4. **Visual pass** — render every page to images (`page.get_pixmap(dpi=50)`) and actually look at them: no overflow, no text colliding with the footer, no half-cropped photos, cover renders the alpha logo (not a black box).

Fix, re-render, re-verify until clean.

## Step 6 — Save (two copies, always)

- Client-facing: `Desktop/Utter Declutter/Client Proposals/Project Proposal for (NAME).pdf` (custom plans: `Custom Space Plan for (NAME).pdf`)
- Records: proposals folder root, `LastName_PrimarySpace_YYYY-MM-DD.pdf`

If a revision comes later (photos, scope, prices), refresh EVERY saved copy including any renamed duplicates Jhen made.

## Step 7 — Delivery

Gmail draft (never send unsent): warm and concise — a 3–4 bullet "short version" of the deal, terms in one sentence, the guarantee line, then:

```
Best,
Jhen Watson
Owner & Organizer | Utter Declutter LLC
Naples, FL · (239) 300-3561
```

Always remind Jhen to attach the PDF (the connector can't). Spouses go together on the To line when both contacts were shared. Follow-up texts go through GHL in Jhen's casual voice — show him the exact wording and get a yes before sending anything.

## Worked example (compressed)

> Jhen: "Proposal for Lauren, today's 2:30 appt — full declutter install organize, $3,050 incl. materials, 4-man crew 8 hrs, 77" Husky shelf, 3-panel slatwall, tote rack pairing with hers, bins throughout."

1. Calendar → Lauren Saigh, lesaigh@gmail.com, (239) 322-9662, 1833 Southeast 6th Lane (GHL → Cape Coral 33990).
2. Ask: deposit split? → "half of labor $1,400 + materials $1,650" → deposit $2,350 / balance $700; check 2,350+700=3,050 ✓. Gate satisfied.
3. Base: standard garage variant. Swap cover, quote #, dates, 4-row materials table, $3,050/$2,350/$700, "One Day", "Scheduled Upon Deposit".
4. Render → 6 pages → numbers assert ✓ → no "Laired/Windsor/$2,000" leaks ✓ → eyeball cover + investment page ✓.
5. Save `Project Proposal for Lauren Saigh.pdf` + `Saigh_Garage_2026-08-31.pdf`. Offer the Gmail draft.
