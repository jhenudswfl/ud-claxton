#!/usr/bin/env python3
"""Claxton — turn a built deal's spec.json into the GHL custom-field payload for the
"UD Service Contract" document template (template id 6ad1b288f32855cd122083e2).

Usage: python3 ghl_fields.py out_<slug>/src/spec.json
Prints a JSON object: {"customFields": [{"id": ..., "field_value": ...}, ...]}
Pass it as the `updates` of ghl_update_contact for the client's contact, then send the
template with ghl_request POST /proposals/templates/send
  {"locationId": "pt7v6T9nKP4uDuuEgw8Q", "templateId": "6ad1b288f32855cd122083e2",
   "contactId": <id>, "userId": "A4C78XkGx08iiyP948ut", "medium": "email" | "sms"}
"""
import json, sys

FIELDS = {
    "ud_agreement_date": "SCdg0fQemczbXMyWHqnx",
    "ud_invoice_number": "vijEBDKvjeh5awCTZLkh",
    "ud_project_address": "gsp0xvPUGQZ2wXqtfNBm",
    "ud_service_dates": "AAhyEeq6mf3upYvE8Ggb",
    "ud_total": "qh5q6SGpU89WuHF7XJph",
    "ud_scope_of_work": "mJuo2JHAtcQkkmg4akF9",
    "ud_payment_terms": "l4CaWFjpIS1WHIawjmwM",
    "ud_scope_limits": "5Go2qVwcsBOAFjaBSZUp",
}

def usd(n):
    return "$" + f"{float(n):,.0f}"

S = json.load(open(sys.argv[1]))
days = S.get("days", 1)
scope = "\n".join("• " + b for b in S.get("scopeBullets", []))
if S.get("laborSentence"):
    scope += "\n" + S["laborSentence"]

pay = [f"Total Service Fee: {usd(S['total'])} ({S['feeDescription']})"]
if S.get("materials"):
    pay.append(f"Materials Budget: {usd(S['materials'])} flat — covers storage solutions and products for the project")
pay += [b["text"] for b in S.get("paymentBullets", [])]

limits = S.get("scopeLimits") or (
    f"The Service Fee covers {S.get('daysWord', days)} {'eight-hour service day' if days == 1 else 'eight-hour service days'} "
    f"as scoped at the walkthrough. Work beyond the agreed scope or service {'day' if days == 1 else 'days'} will be quoted as a "
    f"written change order and performed only upon written approval by the Client, billed at {usd(S['dayRate'])} per additional "
    f"crew day plus applicable at-cost expenses (such as dump or junk-removal fees, billed at cost, with no markup)."
)

values = {
    "ud_agreement_date": S["date"],
    "ud_invoice_number": str(S["invoice"]),
    "ud_project_address": S["address"],
    "ud_service_dates": S["serviceDatesLong"],
    "ud_total": usd(S["total"]),
    "ud_scope_of_work": scope,
    "ud_payment_terms": "\n".join(pay),
    "ud_scope_limits": limits,
}
print(json.dumps({"customFields": [{"id": FIELDS[k], "field_value": v} for k, v in values.items()]}, indent=1, ensure_ascii=False))
