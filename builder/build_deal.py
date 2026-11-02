#!/usr/bin/env python3
"""
Claxton — one-shot builder for the Utter Declutter client document set.

    python3 build_deal.py deal.json --out ./out

deal.json (everything the worker knows after GHL lookup):
{
  "client": "Karen Donohue",             # display name as it should print
  "addr1": "465 Desoto Blvd S",
  "addr2": "Naples, FL 34117",           # city, state ZIP — verified, never guessed
  "price": 1000,                          # labor, flat
  "materials": 0,                         # materials budget (0 = labor only)
  "materialsList": [{"item": "Husky 77\" shelving", "qty": 2, "cost": 450}],   # cost never printed
  "services": ["Declutter", "Organize"],  # subset of Declutter / Install / Organize
  "crew": 2, "days": 1,
  "dates": ["2026-09-20"],                # ISO; [] => TBD wording
  "deposit": "none" | "std" | "half" | "custom",
  "depositAmount": 500,                   # required when deposit == "custom"
  "depositTerms": "...",                  # custom wording (optional)
  "scope": "Garage",                      # space name in Jhen's words
  "discount": {"label": "military discount", "amount": 200},   # optional, shown as its own line
  "itemized": false,                      # true => materials list shows prices (Jhen must say so)
  "notes": "...",                         # free text, NOT printed
  "invoice": 125, "quote": 94,
  "date": "2026-09-10"                    # issue date (defaults to today)
}

Outputs (PDF only, plus the working sources in out/src):
  UD Proposal For <Client>.pdf · UD Service Contract For <Client>.pdf · UD Invoice <N> For <Client>.pdf
Exit code 0 only when every QA check passes. Prints a JSON summary on the last line.
"""
import json, os, re, shutil, subprocess, sys, html
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = "/tmp/node_modules/@fontsource"
LEAKS = ["markup", "Markup", "commission", "Commission", "margin", " cost", "ptimization", "friction", "white-glove", "elevated", "curated", "bespoke", "chaos", "disaster"]  # previous-client names are added at runtime via --leaks

def usd(n):  return "${:,.0f}".format(n) if float(n).is_integer() else "${:,.2f}".format(n)
def usd2(n): return "${:,.2f}".format(n)
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
def w(n): return WORDS.get(n, str(n))

def long_dates(iso_list, days):
    if not iso_list:
        return f"To be determined — {w(days)} ({days}) 8-hour service day{'s' if days > 1 else ''}, to be mutually scheduled", "To be scheduled", "Scheduled Upon Confirmation"
    ds = [datetime.strptime(d, "%Y-%m-%d").date() for d in iso_list]
    def fmt(d, year=True): return d.strftime("%A, %B ") + str(d.day) + (f", {d.year}" if year else "")
    if len(ds) == 1:
        longs = fmt(ds[0]) + f" ({w(days)} 8-hour service day{'s' if days > 1 else ''})"
        short = ds[0].strftime("%B ") + str(ds[0].day) + f", {ds[0].year}"
        tl = ds[0].strftime("%b ") + str(ds[0].day)
    else:
        same_year = all(d.year == ds[0].year for d in ds)
        parts = [fmt(d, year=not same_year) for d in ds]
        longs = (", ".join(parts[:-1]) + " and " + parts[-1] + (f", {ds[0].year}" if same_year else "")) + f" ({w(len(ds))} 8-hour service days)"
        short = ", ".join(d.strftime("%b ") + str(d.day) for d in ds) + f", {ds[-1].year}"
        tl = ds[0].strftime("%b ") + str(ds[0].day) + "–" + (ds[-1].strftime("%b ") if ds[-1].month != ds[0].month else "") + str(ds[-1].day)
    return longs, short, tl

def li(items): return "\n".join(f"<li>{html.escape(i)}</li>" for i in items)
def dv(items): return "\n".join(f"<div>{html.escape(i)}</div>" for i in items)
def para(*ps): return "\n".join(f'<p class="body">{p}</p>' for p in ps)

def copy_for(services, scope, crew, days, materials, items, client_first):
    """Every client-facing sentence for the proposal (Brand Kit v2d voice: plain words, sentence case, no shame, no 'optimization')."""
    S = set(services); full = S == {"Declutter", "Install", "Organize"}
    organize_only = "Install" not in S and S & {"Declutter", "Organize"}
    install_only = S == {"Install"}
    sp = scope.lower(); crew_w = f"{w(crew)}-person crew"
    day_w = "one full day" if days == 1 else f"{w(days)} full days"
    G_NOTE = "On-time guarantee assumes you're available for the sort, keep-or-toss decisions are made the same day, and materials are approved before we start."
    if full:
        p2 = dict(K="How it works", H="Most companies do one of these. We do all three.",
            B=para("Shelving companies install. Junk haulers remove. Organizers sort bins. Most homeowners end up managing three vendors, or doing two-thirds of the work themselves.",
                   f"Utter Declutter is one crew that does all three, start to finish. We clear it out, install the storage, and put every last thing where it belongs. Your {sp} is done in {day_w}."),
            K2="", H2=f"What {day_w} with us looks like",
            B2=para(f"We start with a guided sort: you make the keep-or-toss calls, we move everything. Donations and trash leave on our truck. Then the {crew_w} installs the storage and puts everything that stays in a clear, labeled home. We walk it with you before we leave."),
            L=["A guided sort of everything in the garage", "Haul-off and donation drop-off, handled for you", "Installation of the storage systems", "Organizing and labels for everything that stays", "A final walk-through before we leave"],
            R=["A floor you can see again", "Storage built around how you actually use the space", "Everyday gear where you can reach it", "Seasonal and holiday items up and out of the way", "A garage you'll leave the door open on"])
        p4 = dict(K="Systems and materials", H=f"Everything your {sp} needs, supplied and installed.",
            INC=[f"Decluttering, installing and organizing of the {sp}", "All materials and storage systems listed above", "Project planning, on-site coordination and a final walk-through", "Haul-off and donation drop-off"],
            G=G_NOTE)
        label = f"{scope} · declutter, install and organize"
        scope_bullets = [f"Complete decluttering, sorting, and organization of the {sp}", "Sorting of items into categories: Keep, Donate, Trash, and Sell, per the direction of the Client", "Installation of storage solutions", "Placement of kept items into appropriately labeled storage solutions", "Donation drop-off (if applicable) and removal of trash"]
    elif organize_only:
        p2 = dict(K="How it works", H="A decisive edit, then a reset around how you actually use the space.",
            B=para(f"A {sp} rarely needs more stuff to get organized. It needs a clear sort and a reset. We work through every item with you, get the donations and trash out the door the same day, and give everything that stays a clear, labeled home."),
            K2="", H2=f"What {day_w} with us looks like",
            B2=para(f"A {crew_w}, {day_w}. You make the keep-or-toss calls, we move everything, and we organize what stays using the storage you already own. We walk it with you before we leave."),
            L=["A guided sort of everything in the garage", "Haul-off and donation drop-off, handled for you", "Organizing and labels for everything that stays", "Smart use of the storage you already have", "A final walk-through before we leave"],
            R=["A floor you can see again", "Zones built around how you use the space", "Everyday gear where you can reach it", "A garage you'll leave the door open on"])
        p4 = dict(K=f"Your {sp}, reset", H=f"{day_w.capitalize()}. A {crew_w}. A {sp} that finally works.",
            INC=[f"Decluttering and organizing of the {sp}", "Keep, donate, trash and sell, every decision made with you", "Labels and placement using your existing storage", "Haul-off and donation drop-off", f"{day_w.capitalize()} with a dedicated {crew_w}"],
            G=G_NOTE)
        label = f"{scope} · declutter and organize" if "Declutter" in S else f"{scope} · organize"
        scope_bullets = [f"Complete decluttering, sorting, and organization of the {sp}", "Sorting of items into categories: Keep, Donate, Trash, and Sell, per the direction of the Client", "Placement of kept items into appropriately labeled storage solutions, using the Client's existing storage", "Donation drop-off (if applicable) and removal of trash"]
        if "Declutter" not in S:
            scope_bullets = [f"Organization of the {sp} as scoped at the walkthrough", "Placement of kept items into appropriately labeled storage solutions, using the Client's existing storage", "Final walkthrough and handoff"]
    elif install_only:
        p2 = dict(K="How it works", H="Storage, installed right the first time.",
            B=para("A shelf that isn't anchored to studs or a panel that isn't level is the reason a system sags a year later. We measure, level, anchor to studs and finish clean, so every run of shelving and every panel is ready to carry a full load from day one."),
            K2="", H2=f"What {day_w} with us looks like",
            B2=para(f"A {crew_w}, {day_w}. We confirm the layout with you on site, install the systems, and leave the {sp} clean: packaging hauled out, floor swept, systems ready to load."),
            L=["Layout confirmed with you before anything is mounted", "Stud-anchored, level installation throughout", "All hardware and mounting", "Packaging hauled out, floor swept", "A final walk-through before we leave"],
            R=["Storage that holds a full load", "Systems installed where you'll actually use them", "A clean, ready-to-load space at handoff"])
        p4 = dict(K="Systems and materials", H=f"{day_w.capitalize()}. Ready to load.",
            INC=[f"Installation of the listed systems by a {crew_w}", "All installation labor, hardware and mounting", "Layout confirmation, coordination and a final walk-through", "Packaging disposal and a swept space at handoff"],
            G=G_NOTE)
        label = f"{scope} · installation"
        scope_bullets = [f"Professional installation of the storage systems listed for the {sp}", "On-site layout confirmation before mounting; stud-anchored, level installation", "Removal of packaging and cleanup of the work area"]
    else:
        names = [s for s in ["Declutter", "Install", "Organize"] if s in S]
        p2 = dict(K="How it works", H=" and ".join(n.lower() for n in names).capitalize() + f", one crew, {day_w}.",
            B=para(f"This engagement covers {' and '.join(n.lower() for n in names)} for your {sp}. One {crew_w}, {day_w}, one timeline."),
            K2="", H2=f"What {day_w} with us looks like",
            B2=para("You make the keep-or-toss calls where they apply, we do everything else, and we walk it with you before we leave."),
            L=(["A guided sort of everything in the garage", "Haul-off and donation drop-off, handled for you"] if "Declutter" in S else ["Layout confirmed with you before anything is mounted"]) + (["Installation of the storage systems"] if "Install" in S else []) + (["Organizing and labels for everything that stays"] if "Organize" in S else []),
            R=["A floor you can see again", "Storage built around how you actually use the space", "A garage you'll leave the door open on"])
        p4 = dict(K="Systems and materials" if materials else f"Your {sp}", H=f"{day_w.capitalize()}. A {crew_w}.",
            INC=[f"{' and '.join(n.lower() for n in names).capitalize()} of the {sp}"] + (["All materials and storage systems listed above"] if materials else []) + ["Project planning, coordination and a final walk-through"] + (["Haul-off and donation drop-off"] if "Declutter" in S else []),
            G=G_NOTE)
        label = f"{scope} · " + " and ".join(n.lower() for n in names)
        scope_bullets = ([f"Decluttering and sorting of the {sp}", "Sorting of items into categories: Keep, Donate, Trash, and Sell, per the direction of the Client", "Donation drop-off (if applicable) and removal of trash"] if "Declutter" in S else []) + \
                        (["Installation of storage solutions"] if "Install" in S else []) + \
                        (["Placement of kept items into appropriately labeled storage solutions"] if "Organize" in S else [])
    return p2, p4, label, scope_bullets

def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("deal"); ap.add_argument("--out", default="out"); ap.add_argument("--assets", default=None)
    ap.add_argument("--skip-view", action="store_true", help="don't render page images")
    a = ap.parse_args()
    D = json.load(open(a.deal))
    assets = os.path.abspath(a.assets or os.path.join(HERE, "assets"))
    out = os.path.abspath(a.out); src = os.path.join(out, "src"); os.makedirs(src, exist_ok=True)

    # ---- env ----
    if not os.path.isdir(FONTS):
        subprocess.run("cd /tmp && npm install @fontsource/playfair-display @fontsource/montserrat", shell=True, check=True, capture_output=True)
    try:
        import weasyprint, pymupdf  # noqa
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "weasyprint", "pymupdf", "--break-system-packages"], check=True)
    import pymupdf
    from weasyprint import HTML

    # ---- numbers ----
    client = D["client"].strip(); first, last = client.split(" ")[0], client.split(" ")[-1]
    price = float(D["price"]); materials = float(D.get("materials") or 0); crew = int(D["crew"]); days = int(D["days"])
    disc = D.get("discount") or None; disc_amt = float(disc["amount"]) if disc else 0
    total = price + materials - disc_amt
    dep = D.get("deposit", "none")
    if dep == "none": deposit = 0
    elif dep == "std": deposit = materials + (price - disc_amt) / 2
    elif dep == "half": deposit = total / 2
    elif dep == "custom":
        if D.get("depositAmount") is None: sys.exit("ERROR: deposit=custom needs depositAmount")
        deposit = float(D["depositAmount"])
    else: sys.exit(f"ERROR: unknown deposit {dep}")
    balance = total - deposit
    assert abs(deposit + balance - total) < 0.005, "deposit + balance != total"
    day_rate = round(price / days)
    issued = datetime.strptime(D.get("date") or date.today().isoformat(), "%Y-%m-%d").date()
    issued_s = issued.strftime("%B ") + str(issued.day) + f", {issued.year}"
    valid = issued + timedelta(days=30); valid_s = valid.strftime("%B ") + str(valid.day) + f", {valid.year}"
    longs, shorts, tl = long_dates(D.get("dates") or [], days)
    services = D.get("services") or ["Declutter", "Organize"]
    scope = D.get("scope") or "Garage"
    items = [m for m in (D.get("materialsList") or []) if m.get("item")]
    itemized = bool(D.get("itemized"))

    # ---- proposal ----
    p2, p4, label, scope_bullets = copy_for(services, scope, crew, days, materials, items, first)
    if materials > 0:
        rows = "".join(f"<tr><td>{html.escape(m['item'])}</td><td class=\"qty\">{m.get('qty', 1)}" + (f" · {usd(m['cost'])}" if itemized and m.get('cost') else "") + "</td></tr>" for m in items) \
               or f"<tr><td>Storage solutions and products for the {scope.lower()}</td><td class=\"qty\">Project batch</td></tr>"
        p4_body = f'<table class="materials">{rows}</table>\n<div class="small">' + ("Soft quote: the systems above are our starting recommendation. Final products, sizes and finishes are chosen with you, and the final price follows those selections. You're welcome to purchase materials directly, or we can source them for you at cost." if D.get("softQuote") else "Materials are included in your price, along with haul-off, donation drop-off and the small supplies a project like this needs.") + '</div>'
    else:
        sp = scope.lower()
        p4_body = para(f"We start by pulling everything out into the open and sorting it with you: keep, donate, trash or sell, one decision at a time. Then we reset the space around how you actually use it, with a clear, labeled home for everything that stays.",
                       f"By the end of the {'day' if days == 1 else 'last day'}, the donations are gone, the trash is gone, and you're walking into a {sp} that's easy to keep.") \
                  if "Declutter" in services else para(f"A {w(crew)}-person crew, {'one full day' if days == 1 else w(days) + ' full days'}. We confirm the layout with you on site, do the work, and leave the {sp} clean and ready to use.")
    if dep == "none":
        terms = '<tr><td>Deposit<span class="sub">No deposit. Nothing is due up front.</span></td><td class="amt">$0.00</td></tr>' \
                f'<tr><td>Due on completion<span class="sub">Paid in full at your final walk-through</span></td><td class="amt">{usd2(balance)}</td></tr>'
        step1 = "<div>Reply to confirm and we'll lock in your day on our calendar. No deposit needed.</div>\n<div>The full price is due when the job is done, at your final walk-through.</div>"
        dates_tl = tl if D.get("dates") else "On confirmation"
    else:
        sub = {"std": "Covers all project materials and holds your dates" if materials else "Holds your dates on our calendar", "half": "Holds your dates on our calendar", "custom": html.escape(D.get("depositTerms") or "Holds your dates on our calendar")}[dep]
        terms = f'<tr><td>Deposit to reserve your dates<span class="sub">{sub}</span></td><td class="amt">{usd2(deposit)}</td></tr>' \
                f'<tr><td>Due on completion<span class="sub">Paid at your final walk-through</span></td><td class="amt">{usd2(balance)}</td></tr>'
        step1 = f"<div>The deposit holds your dates on our calendar{' and covers all project materials, so everything is ready on day one' if (materials and dep == 'std') else ''}.</div>\n<div>The balance is due when the job is done, at your final walk-through.</div>"
        dates_tl = tl if D.get("dates") else "On deposit"
    photo = ""
    if "garage" in scope.lower():
        photo = f'''<!-- PAGE 3 · BEFORE AND AFTER -->
<div class="page">
  <div class="eyebrow">Real projects</div>
  <h2>The same four walls, working the way they should.</h2>
  <div class="pair"><div class="shot"><img src="{assets}/jenn_before.jpg"><div class="cap">Before</div></div><div class="shot"><img src="{assets}/jenn_after.jpg"><div class="cap after">After</div></div></div>
  <div class="pair" style="margin-top:0.16in;"><div class="shot"><img src="{assets}/jay_before.jpg"><div class="cap">Before</div></div><div class="shot"><img src="{assets}/jay_after.jpg"><div class="cap after">After · floor finish updated by the homeowner between photos</div></div></div>
  <div class="small" style="margin-top:0.1in;">Our own projects, our own crew. Nothing staged.</div>
  <div class="pagefoot"><span>Utter Declutter</span><span>The Done-For-You Garage</span></div>
</div>'''
    # Client's own Polycam scan + 3D rendering (Clients/<Name>/Before|After For <Name>.png) => "Your Garage" page before the reference photos.
    client_page = ""
    if D.get("clientBefore") and D.get("clientAfter"):
        def _trim(src, dst):
            try:
                from PIL import Image, ImageChops
                im = Image.open(src).convert("RGB"); bg = Image.new("RGB", im.size, im.getpixel((2, 2)))
                bbox = ImageChops.difference(im, bg).point(lambda v: 255 if v > 24 else 0).getbbox()
                if bbox:
                    pad = 24; bbox = (max(0, bbox[0]-pad), max(0, bbox[1]-pad), min(im.width, bbox[2]+pad), min(im.height, bbox[3]+pad))
                    im = im.crop(bbox)
                im.save(dst); return dst
            except Exception: return src
        os.makedirs(src, exist_ok=True)
        cb = os.path.abspath(_trim(D["clientBefore"], os.path.join(src, "client_before.png")))
        ca = os.path.abspath(_trim(D["clientAfter"], os.path.join(src, "client_after.png")))
        client_page = f'''<!-- PAGE 3a · YOUR GARAGE -->
<div class="page">
  <div class="eyebrow">Your {html.escape(scope.lower())}</div>
  <h2>Your space today, and the plan we built for it.</h2>
  <div class="pair"><div class="shot"><img src="file://{cb}" style="height:3.45in; object-fit:cover;"><div class="cap">Today · 3D scan of your {html.escape(scope.lower())}</div></div></div>
  <div class="pair" style="margin-top:0.16in;"><div class="shot"><img src="file://{ca}" style="height:3.45in; object-fit:cover;"><div class="cap after">The plan · rendered to your measurements</div></div></div>
  <div class="small" style="margin-top:0.1in;">Built from the scan we took at your walkthrough. Products, sizes and finishes are confirmed with you before anything is ordered.</div>
  <div class="pagefoot"><span>Utter Declutter</span><span>The Done-For-You Garage</span></div>
</div>'''
    photo = client_page + photo
    if D.get("renderUrl"):
        _ru = html.escape(D["renderUrl"])
        step1 = f'<div><b>See your garage in 3D.</b> We built an interactive render of your {html.escape(scope.lower())} with the plan from your walkthrough: <a href="{_ru}" style="color:#814A0A;">{_ru}</a></div>\n' + step1
    if D.get("softQuote"):
        step1 = "<div><b>Soft quote.</b> We finalize the design and your product selections together, then confirm the final price in your Service Agreement. The figure in this proposal may move up or down with those choices.</div>\n" + step1
    disc_line = f'<div class="disc">Includes a {usd(disc_amt)} {html.escape(disc["label"])}' + (", with our thanks for your service" if "military" in disc["label"].lower() else "") + "</div>" if disc else ""
    soft = bool(D.get("softQuote"))
    soft_note = '<div class="card tint" style="margin-bottom:0.22in; padding:0.22in 0.28in;"><div class="chip" style="background:#814A0A; color:#FBF8F3; margin-bottom:0.1in;">Soft quote</div><p class="body" style="margin-bottom:0.06in;"><b>This is a soft quote, not a final price.</b> The number below is our working estimate for the scope we walked through. Your final quote is set once we lock the exact design and your product selections, and it may come in above or below this figure.</p><div class="small">Nothing is scheduled and nothing is owed until the final quote is confirmed in your Service Agreement.</div></div>' if soft else ""
    sub_map = {"{{FONTS}}": FONTS, "{{ASSETS}}": assets, "{{CLIENT}}": html.escape(client), "{{ADDR1}}": html.escape(D["addr1"]), "{{ADDR2}}": html.escape(D["addr2"]),
               "{{QUOTE}}": str(D["quote"]), "{{ISSUED}}": issued_s, "{{VALID}}": valid_s, "{{COVER_CHIP}}": "Soft quote · not a final price" if soft else "Project proposal", "{{SOFT_NOTE}}": soft_note, "{{INVEST_H2}}": "Where the number stands today." if soft else "One flat price. Everything included.", "{{CREW}}": f"{w(crew).capitalize()} people", "{{GUARANTEE_NOTE}}": p4["G"],
               "{{P2_KICKER}}": p2["K"], "{{P2_H2}}": p2["H"], "{{P2_BODY}}": p2["B"], "{{P2_KICKER2}}": p2["K2"], "{{P2_H2B}}": p2["H2"], "{{P2_BODY2}}": p2["B2"],
               "{{SCOPE_L}}": li(p2["L"]), "{{SCOPE_R}}": li(p2["R"]), "{{PHOTO_PAGE}}": photo,
               "{{P4_KICKER}}": p4["K"], "{{P4_H2}}": p4["H"], "{{P4_BODY}}": p4_body, "{{INCLUDED}}": li(p4["INC"]),
               "{{TOTAL}}": usd2(total), "{{TOTAL_LABEL}}": ("Soft quote estimate · " if soft else ("All-in, materials included · " if materials else "Flat price · ")) + label, "{{DISCOUNT_LINE}}": disc_line,
               "{{TERMS_ROWS}}": terms, "{{DATES}}": dates_tl, "{{DURATION}}": {1: "One day", 2: "Two days", 3: "Three days", 4: "Four days"}.get(days, f"{days} days"), "{{STEP1}}": step1}
    h = open(os.path.join(HERE, "proposal_base.html")).read()
    for k, v in sub_map.items(): h = h.replace(k, v)
    assert "{{" not in h, "unfilled placeholder: " + re.findall(r"\{\{[A-Z_0-9]+\}\}", h)[0]
    ph = os.path.join(src, "proposal.html"); open(ph, "w").write(h)
    prop_pdf = os.path.join(out, f"UD Proposal For {client}.pdf"); HTML(ph).write_pdf(prop_pdf)

    # ---- contract + invoice ----
    fee_desc = f"flat fee for {w(days)} 8-hour service day{'s' if days > 1 else ''}" + (f" at {usd(day_rate)} per day" if days > 1 else "") + f", {w(crew)}-person crew"
    pay = []
    if disc: pay.append({"text": f"Labor: {usd(price)}, less a {usd(disc_amt)} {disc['label']} = {usd(price - disc_amt)}", "bold": False})
    if dep == "none":
        pay += [{"text": "No deposit required", "bold": False}, {"text": f"The full balance of {usd(total)} is due upon project completion", "bold": False}]
    else:
        why = " and allow all materials to be purchased and ready for day one" if (dep == "std" and materials) else ""
        pct = f" ({round(deposit / total * 100)}%)" if dep != "custom" else ""
        pay += [{"text": f"A non-refundable deposit of {usd(deposit)}{pct} is due at the time of booking to reserve the service date{'s' if days > 1 else ''}{why}" + (f" — {D['depositTerms']}" if dep == "custom" and D.get("depositTerms") else ""), "bold": False},
                {"text": f"The remaining balance of {usd(balance)} is due upon project completion", "bold": False}]
    # Jhen's rule (Oct 2026): installation labor is carried in the materials allocation, not the labor line.
    # With a materials budget, the labor line names only decluttering/organizing and the materials line says it includes installation.
    inv_services = [s for s in ["Declutter", "Install", "Organize"] if s in services and not (materials and s == "Install")] or list(services)
    lines = [{"desc": f"{scope} {' and '.join(s.lower() for s in inv_services).replace('declutter', 'decluttering').replace('install', 'installation').replace('organize', 'organization')} — full service day, {w(crew)}-person crew (8 hours)", "rate": day_rate, "qty": days, "amount": price}]
    if materials: lines.append({"desc": "Materials budget — storage solutions and products for the project" + (", including installation labor" if "Install" in services else ""), "rate": materials, "qty": 1, "amount": materials})
    if disc: lines.append({"desc": disc["label"].capitalize(), "rate": -disc_amt, "qty": 1, "amount": -disc_amt})
    sched = [{"label": "Deposit", "amount": "None required"}, {"label": "Full balance due upon project completion", "amount": usd2(total)}] if dep == "none" else \
            [{"label": "Deposit due at booking (non-refundable, reserves service date" + ("s" if days > 1 else "") + ")", "amount": usd2(deposit)}, {"label": "Balance due upon project completion", "amount": usd2(balance)}]
    spec = dict(client=client, addr1=D["addr1"], addr2=D["addr2"], address=f"{D['addr1']}, {D['addr2']}", date=issued_s, invoice=D["invoice"],
                serviceDatesLong=longs, serviceDatesShort=shorts, scopeBullets=scope_bullets, total=total, materials=materials, feeDescription=fee_desc,
                laborSentence=f"All labor for the {w(days)} ({days}) service day{'s' if days > 1 else ''} of eight (8) hours{' each' if days > 1 else ''}, performed by a {w(crew)}-person crew, is included in the {usd(total)} total.",
                paymentBullets=pay, days=days, daysWord=f"{w(days)} ({days})", dayRate=day_rate, invoiceLines=lines, schedule=sched)
    if dep != "none" and deposit > 0:
        spec["depositInvoice"] = {"amount": deposit, "balance": balance, "number": f"{D['invoice']}-D"}
    sp_path = os.path.join(src, "spec.json"); json.dump(spec, open(sp_path, "w"), indent=1)
    # Brand-kit renderer (Plus Jakarta Sans, weasyprint). docs.js / LibreOffice are no longer used.
    r = subprocess.run([sys.executable, os.path.join(HERE, "docs_html.py"), sp_path, out, "--fonts", FONTS, "--logo", os.path.join(assets, "logo_v2.png")], capture_output=True, text=True)
    assert r.returncode == 0, "docs_html failed: " + r.stderr[-600:]

    # ---- QA ----
    problems = []; pages = {}
    checks = {prop_pdf: (5 + bool(client_page) + bool("garage" in scope.lower())), os.path.join(out, f"UD Service Contract For {client}.pdf"): 2, os.path.join(out, f"UD Invoice {D['invoice']} For {client}.pdf"): 1}
    for pdf, want in checks.items():
        d = pymupdf.open(pdf); txt = "".join(pg.get_text() for pg in d); n = len(d); pages[os.path.basename(pdf)] = n
        if n != want: problems.append(f"{os.path.basename(pdf)}: {n} pages, expected {want}")
        own = json.dumps(D)  # tokens that legitimately belong to this deal are not leaks
        scrub = re.sub(r"\s+", " ", txt)
        for ok_phrase in ["at cost, with no markup", "costs a little time", "billed at actual cost", "at-cost expenses", "work and costs incurred"]:
            scrub = scrub.replace(ok_phrase, "")  # owner-approved wording, not an internal-number leak
        for bad in LEAKS:
            if bad in scrub and bad not in own and not (itemized and bad == " cost"): problems.append(f"{os.path.basename(pdf)}: leak '{bad.strip()}'")
        for must in [client, usd2(total) if "Proposal" in pdf or "Invoice" in pdf else usd(total)]:
            if must not in txt: problems.append(f"{os.path.basename(pdf)}: missing '{must}'")
        if "Contract" in pdf:
            last_pg = d[-1].get_text()
            if "signatures" not in last_pg.lower() or "termination" not in last_pg.lower(): problems.append("contract: signatures not under Termination on final page")
        if "Install" not in services and "install" in txt.lower() and "Proposal" in pdf: problems.append("proposal: 'install' language on a no-install job")
        if not a.skip_view:
            for i, pg in enumerate(d): pg.get_pixmap(dpi=40).save(os.path.join(src, f"{os.path.basename(pdf)[:-4]}-{i+1}.jpg"))
    summary = dict(ok=not problems, problems=problems, pages=pages, total=total, deposit=deposit, balance=balance, dayRate=day_rate,
                   files=[os.path.basename(x) for x in checks], records_name=f"{last}_{scope.replace(' ', '')}_{issued.isoformat()}.pdf")
    print(json.dumps(summary))
    sys.exit(0 if not problems else 1)

if __name__ == "__main__":
    main()
