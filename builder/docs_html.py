#!/usr/bin/env python3
"""
Claxton — renders the UD Service Agreement and invoices as brand-kit v2c PDFs (Plus Jakarta Sans,
cocoa / paper / sand / bronze / palm) from the spec.json that build_deal.py writes.

    python3 docs_html.py spec.json outdir [--fonts /tmp/node_modules/@fontsource] [--logo path]
                        [--deposit-only] [--skip-contract]

Writes:
  UD Service Contract For <Client>.pdf   (2 pages; signatures on page 2)
  UD Invoice <N> For <Client>.pdf        (1 page)
  UD Deposit Invoice <N> For <Client>.pdf (legacy only: spec.depositInvoice is no longer set by build_deal.py — one invoice per deal)
"""
import json, os, sys, html as H

spec_path, out_dir = sys.argv[1], sys.argv[2]
args = sys.argv[3:]
def opt(flag, default=None):
    return args[args.index(flag) + 1] if flag in args else default
FONTS = opt("--fonts", "/tmp/node_modules/@fontsource")
HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = opt("--logo", os.path.join(HERE, "..", "assets", "logo_v2.png"))
S = json.load(open(spec_path))
e = lambda s: H.escape(str(s))
usd = lambda n: "${:,.0f}".format(float(n)) if float(n).is_integer() else "${:,.2f}".format(float(n))
usd2 = lambda n: ("-$" if float(n) < 0 else "$") + "{:,.2f}".format(abs(float(n)))

CSS = f"""
@font-face {{ font-family:'Plus Jakarta Sans'; src:url('{FONTS}/plus-jakarta-sans/files/plus-jakarta-sans-latin-500-normal.woff'); font-weight:500; }}
@font-face {{ font-family:'Plus Jakarta Sans'; src:url('{FONTS}/plus-jakarta-sans/files/plus-jakarta-sans-latin-600-normal.woff'); font-weight:600; }}
@font-face {{ font-family:'Plus Jakarta Sans'; src:url('{FONTS}/plus-jakarta-sans/files/plus-jakarta-sans-latin-700-normal.woff'); font-weight:700; }}
@font-face {{ font-family:'Plus Jakarta Sans'; src:url('{FONTS}/plus-jakarta-sans/files/plus-jakarta-sans-latin-800-normal.woff'); font-weight:800; }}
@page {{ size: letter; margin: 0.7in 0.8in 0.75in; @bottom-left {{ content: "Utter Declutter LLC"; font: 600 7.5pt 'Plus Jakarta Sans'; color: rgba(42,33,24,.5); }} @bottom-right {{ content: counter(page) " / " counter(pages); font: 600 7.5pt 'Plus Jakarta Sans'; color: rgba(42,33,24,.5); }} }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:'Plus Jakarta Sans', sans-serif; color:#2A2118; font-weight:500; font-size:9.6pt; line-height:1.5; }}
.brand {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:0.22in; }}
.brand img {{ height:0.3in; }}
.chip {{ display:inline-block; font-size:8pt; font-weight:600; padding:0.04in 0.13in; border-radius:999px; background:#F3E7D8; color:#5E3506; }}
h1 {{ font-size:24pt; font-weight:800; letter-spacing:-0.02em; line-height:1.05; margin-bottom:0.08in; }}
.sub {{ font-size:9pt; font-weight:600; color:rgba(42,33,24,.62); margin-bottom:0.2in; }}
.meta {{ display:flex; gap:0.25in; background:#EDE3D5; border-radius:14px; padding:0.16in 0.2in; margin-bottom:0.2in; }}
.meta div {{ flex:1; }}
.meta small {{ display:block; font-size:7.5pt; font-weight:600; color:rgba(42,33,24,.6); margin-bottom:0.02in; }}
.meta b {{ font-size:9.5pt; font-weight:700; line-height:1.35; display:block; }}
h2 {{ font-size:8.5pt; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:#814A0A; margin:0.16in 0 0.06in; page-break-after:avoid; }}
h2 .init {{ float:right; font-weight:700; letter-spacing:0; text-transform:none; color:rgba(42,33,24,.62); }}
p {{ margin-bottom:0.07in; color:rgba(42,33,24,.86); }}
ul {{ margin:0 0 0.07in 0.18in; }}
li {{ margin-bottom:0.035in; color:rgba(42,33,24,.86); }}
li.b, p.b {{ font-weight:700; color:#2A2118; }}
.card {{ background:#FFFFFF; border:1px solid rgba(42,33,24,.12); border-radius:14px; padding:0.14in 0.18in; margin-bottom:0.12in; }}
.card.tint {{ background:#F3E7D8; border-color:transparent; }}
.sig {{ display:flex; gap:0.3in; margin-top:0.12in; page-break-inside:avoid; }}
.sig div {{ flex:1; }}
.sig .line {{ border-top:1.2pt solid #2A2118; margin-top:0.42in; padding-top:0.05in; font-size:8pt; font-weight:600; color:rgba(42,33,24,.62); }}
.sig b {{ display:block; font-size:9.5pt; margin-bottom:0.02in; }}
table {{ width:100%; border-collapse:collapse; margin:0.06in 0 0.1in; }}
th {{ text-align:left; font-size:7.5pt; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:rgba(42,33,24,.6); padding:0.06in 0.1in; border-bottom:1.2pt solid #D6C5AB; }}
td {{ padding:0.09in 0.1in; border-bottom:0.6pt solid rgba(42,33,24,.12); vertical-align:top; }}
th.r, td.r {{ text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums; }}
tr.total td {{ border-bottom:0; border-top:1.2pt solid #2A2118; font-weight:800; font-size:11pt; padding-top:0.1in; }}
.sched {{ display:flex; gap:0.15in; margin-top:0.08in; }}
.sched div {{ flex:1; background:#EDE3D5; border-radius:14px; padding:0.14in 0.18in; }}
.sched div.due {{ background:#814A0A; color:#FBF8F3; }}
.sched small {{ display:block; font-size:7.5pt; font-weight:600; opacity:.75; margin-bottom:0.03in; }}
.sched b {{ font-size:15pt; font-weight:800; letter-spacing:-0.02em; }}
.fine {{ font-size:8pt; color:rgba(42,33,24,.62); margin-top:0.12in; }}
.steps {{ display:inline-flex; gap:0.08in; align-items:center; font-weight:800; font-size:8.5pt; }}
.steps i {{ width:0.1in; height:0.1in; border-radius:3px; display:inline-block; }}
.steps .a {{ background:#D6C5AB; }} .steps .b {{ background:#2A2118; }} .steps .c {{ background:#814A0A; }}
.steps span {{ margin-right:0.08in; }}
.pb {{ page-break-before:always; }}
"""

def head(title, chip, sub):
    return f"""<div class="brand"><img src="file://{os.path.abspath(LOGO)}"><span class="chip">{e(chip)}</span></div>
<h1>{e(title)}</h1><div class="sub">{sub}</div>"""

def contract_html():
    c = S
    scope = "".join(f"<li>{e(b)}</li>" for b in c["scopeBullets"])
    pay = f'<li class="b">Total Service Fee: {usd(c["total"])} ({e(c["feeDescription"])})</li>'
    if c.get("materials", 0) > 0:
        pay += f'<li class="b">Materials Budget: {usd(c["materials"])} flat — covers storage solutions and products for the project</li>'
    pay += "".join(f'<li{" class=b" if b.get("bold") else ""}>{e(b["text"])}</li>' for b in c["paymentBullets"])
    limits = c.get("scopeLimits") or (f'The Service Fee covers {c["daysWord"]} {"eight-hour service day" if c["days"] == 1 else "eight-hour service days"} as scoped at the walkthrough. '
              f'Work beyond the agreed scope or service {"day" if c["days"] == 1 else "days"} will be quoted as a written change order and performed only upon written approval by the Client, '
              f'billed at {usd(c["dayRate"])} per additional crew day plus applicable at-cost expenses (such as dump or junk-removal fees, billed at cost, with no markup).')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
{head("Service agreement", "Utter Declutter LLC", f"Date <b>{e(c['date'])}</b> &nbsp;·&nbsp; Invoice <b>#{e(c['invoice'])}</b>")}
<div class="meta">
  <div><small>Business</small><b>Utter Declutter LLC</b>a Florida limited liability company</div>
  <div><small>Client</small><b>{e(c['client'])}</b></div>
  <div><small>Project address</small><b>{e(c['address'])}</b></div>
</div>
<div class="meta" style="margin-top:-0.1in"><div><small>Service date(s)</small><b>{e(c['serviceDatesLong'])}</b></div></div>
<p>This Service Agreement (“Agreement”) is entered into between Utter Declutter LLC and the Client named above. By signing below, the Client agrees to the following terms and conditions.</p>
<h2>Scope of work <span class="init">Initials required: _______</span></h2>
<p>Utter Declutter LLC (the “Service Provider”) agrees to perform the following services:</p>
<ul>{scope}</ul>
<p>{e(c['laborSentence'])}</p>
<h2>Payment terms <span class="init">Initials required: _______</span></h2>
<ul>{pay}</ul>
<h2>Scope limits &amp; additional work</h2>
<p>{e(limits)}</p>
<h2>Business name clarification</h2>
<p>All references in this Agreement to “Utter Declutter” refer to Utter Declutter LLC, a Florida limited liability company. The Client acknowledges that all services, obligations, liabilities, and rights under this Agreement are solely those of Utter Declutter LLC, and not of its owner in an individual capacity.</p>
<h2>Trade name / d.b.a. clause</h2>
<p>Utter Declutter LLC may conduct business under the trade name “Utter Declutter.” Any use of the trade name in this Agreement or associated materials is for branding purposes only and does not alter the legal identity of the contracting party, which is and shall remain Utter Declutter LLC.</p>
<h2>Media rights clause</h2>
<p>The Client grants Utter Declutter LLC permission to photograph, record, and/or film the project space before, during, and after services are performed. Utter Declutter LLC may use such media — including photos, videos, audio, and written descriptions — for marketing, advertising, training, and promotional purposes, including but not limited to social media, websites, digital ads, print materials, and portfolio use. No personally identifying information about the Client will be disclosed without the Client’s explicit permission.</p>
<h2>Client review &amp; cooperation</h2>
<p>The Client agrees to be reasonably available during the project to answer questions, provide feedback, designate item categories, and make timely decisions necessary for the completion of services.</p>
<h2>Modifications</h2>
<p>Any changes to this Agreement must be agreed to in writing by both parties.</p>
<h2>Termination</h2>
<p>If the Agreement is terminated prior to project completion, the Client is responsible for paying for all work and costs incurred up until that date.</p>
<h2>Signatures</h2>
<div class="card tint">
  <div class="sig"><div><b>Client: {e(c['client'])}</b><div class="line">Client signature</div></div><div><b>&nbsp;</b><div class="line">Date</div></div></div>
  <div class="sig"><div><b>Utter Declutter LLC: Jhen Watson, Owner</b><div class="line">Signature</div></div><div><b>&nbsp;</b><div class="line">Date</div></div></div>
</div>
<p class="fine"><span class="steps"><i class="a"></i><span>Declutter</span><i class="b"></i><span>Install</span><i class="c"></i><span>Organize</span></span> &nbsp; Utter Declutter LLC · Naples, FL · (239) 300-3561</p>
</body></html>"""

def invoice_html(inv):
    """inv: dict with title, chip, number, date, lines, total, schedule[{label, amount, due?}], note, bill_to"""
    rows = "".join(f'<tr><td>{e(l["desc"])}</td><td class="r">{usd2(l["rate"])}</td><td class="r">{e(l["qty"])}</td><td class="r">{usd2(l["amount"])}</td></tr>' for l in inv["lines"])
    sched = "".join(f'<div class="{"due" if s.get("due") else ""}"><small>{e(s["label"])}</small><b>{e(s["amount"])}</b></div>' for s in inv["schedule"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
{head(inv["title"], inv["chip"], f"Invoice <b>#{e(inv['number'])}</b> &nbsp;·&nbsp; Date <b>{e(inv['date'])}</b> &nbsp;·&nbsp; Service dates <b>{e(S['serviceDatesShort'])}</b>")}
<div class="meta">
  <div><small>Bill to</small><b>{e(S['client'])}</b>{e(S['addr1'])}<br>{e(S['addr2'])}</div>
  <div><small>From</small><b>Utter Declutter LLC</b>Jhen Watson, Owner<br>(239) 300-3561</div>
</div>
<table><thead><tr><th>Description</th><th class="r">Rate</th><th class="r">Qty</th><th class="r">Amount</th></tr></thead>
<tbody>{rows}<tr class="total"><td></td><td class="r" colspan="2">Total</td><td class="r">{usd2(inv["total"])}</td></tr></tbody></table>
<h2>{e(inv.get("scheduleTitle", "Payment schedule"))}</h2>
<div class="sched">{sched}</div>
<p class="fine">{e(inv["note"])}</p>
<p class="fine"><span class="steps"><i class="a"></i><span>Declutter</span><i class="b"></i><span>Install</span><i class="c"></i><span>Organize</span></span> &nbsp; Pay by card or bank from the link in your text or email. Zelle, check and cash are welcome too.</p>
</body></html>"""

def main():
    from weasyprint import HTML
    os.makedirs(out_dir, exist_ok=True)
    def write(h, name):
        p = os.path.join(out_dir, name); HTML(string=h, base_url=out_dir).write_pdf(p); return p
    c = S
    if "--deposit-only" not in args:
        # total invoice
        sched = []
        for i, s in enumerate(c["schedule"]):
            # one invoice per deal: highlight the first payment actually owed (deposit / paid in full, else the balance)
            first_due = 0 if "None" not in c["schedule"][0]["amount"] else len(c["schedule"]) - 1
            sched.append({"label": s["label"], "amount": s["amount"], "due": i == first_due})
        write(invoice_html({"title": "Invoice", "chip": "Total for the project", "number": c["invoice"], "date": c["date"], "lines": c["invoiceLines"], "total": c["total"], "schedule": sched,
                            "note": c.get("footerNote") or f"Per Service Agreement / Invoice #{c['invoice']}. Thank you for choosing Utter Declutter."}),
              c.get("invoiceFile") or f"UD Invoice {c['invoice']} For {c['client']}.pdf")
    if c.get("depositInvoice"):
        d = c["depositInvoice"]  # {amount, balance, number}
        write(invoice_html({"title": "Deposit invoice", "chip": "Reserves your dates", "number": d.get("number", str(c["invoice"]) + "-D"), "date": c["date"],
                            "lines": [{"desc": f"Deposit toward Invoice #{c['invoice']} — reserves the service date{'s' if c['days'] > 1 else ''}", "rate": d["amount"], "qty": 1, "amount": d["amount"]}],
                            "total": d["amount"], "scheduleTitle": "What's left after this deposit",
                            "schedule": [{"label": "This deposit, due at booking", "amount": usd2(d["amount"]), "due": True}, {"label": "Balance due on the last project day", "amount": usd2(d["balance"])}],
                            "note": f"Non-refundable. Applied in full to Invoice #{c['invoice']}."}),
              f"UD Deposit Invoice {d.get('number', str(c['invoice']) + '-D')} For {c['client']}.pdf")
    if "--skip-contract" not in args and not c.get("skipContract"):
        write(contract_html(), f"UD Service Contract For {c['client']}.pdf")
    print("pdf written")

if __name__ == "__main__":
    main()
