# UD Service Agreement — GHL document template

Paste this into a new **Documents & Contracts → Templates** entry in GoHighLevel named exactly `UD Service Agreement`. Every `{{contact.…}}` tag is a merge field that Claxton fills on the client's contact record before sending. The UD logo goes in the header block the same way you add it today.

Place these fillable elements once, at the bottom (Signatures section): **Signature** and **Date** fields for the client (Recipient 1 = the contact), then **Signature** and **Date** fields for you (Recipient 2 = Jhen Watson, user). Nothing else needs a field.

---

**SERVICE AGREEMENT**

Utter Declutter

Date: **{{contact.ud_agreement_date}}**
Invoice #: **{{contact.ud_invoice_number}}**

This Service Agreement ("Agreement") is entered into between:

Business: Utter Declutter LLC, a Florida limited liability company
Client: **{{contact.first_name}} {{contact.last_name}}**
Project Address: **{{contact.ud_project_address}}**
Service Date(s): **{{contact.ud_service_dates}}**

By signing below, the Client agrees to the following terms and conditions.

**SCOPE OF WORK • INITIALS REQUIRED: _______**

Utter Declutter LLC (the "Service Provider") agrees to perform the following services:

{{contact.ud_scope_of_work}}

**PAYMENT TERMS • INITIALS REQUIRED: _______**

{{contact.ud_payment_terms}}

**SCOPE LIMITS & ADDITIONAL WORK**

{{contact.ud_scope_limits}}

**BUSINESS NAME CLARIFICATION**

All references in this Agreement to "Utter Declutter" refer to Utter Declutter LLC, a Florida limited liability company. The Client acknowledges that all services, obligations, liabilities, and rights under this Agreement are solely those of Utter Declutter LLC, and not of its owner in an individual capacity.

**TRADE NAME / D.B.A. CLAUSE**

Utter Declutter LLC may conduct business under the trade name "Utter Declutter." Any use of the trade name in this Agreement or associated materials is for branding purposes only and does not alter the legal identity of the contracting party, which is and shall remain Utter Declutter LLC.

**MEDIA RIGHTS CLAUSE**

The Client grants Utter Declutter LLC permission to photograph, record, and/or film the project space before, during, and after services are performed. Utter Declutter LLC may use such media — including photos, videos, audio, and written descriptions — for marketing, advertising, training, and promotional purposes, including but not limited to social media, websites, digital ads, print materials, and portfolio use. No personally identifying information about the Client will be disclosed without the Client's explicit permission.

**CLIENT REVIEW & COOPERATION**

The Client agrees to be reasonably available during the project to answer questions, provide feedback, designate item categories, and make timely decisions necessary for the completion of services.

**MODIFICATIONS**

Any changes to this Agreement must be agreed to in writing by both parties.

**TERMINATION**

If the Agreement is terminated prior to project completion, the Client is responsible for paying for all work and costs incurred up until that date.

**SIGNATURES**

Client Name: **{{contact.first_name}} {{contact.last_name}}**
Client Signature: [Signature field — Recipient 1]
Date: [Date field — Recipient 1]

Utter Declutter LLC Representative: **Jhen Watson, Owner**
Signature: [Signature field — Recipient 2]
Date: [Date field — Recipient 2]

---

## The merge fields (already created on your contacts)

| Field | Key | What Claxton writes |
|---|---|---|
| UD Agreement Date | `contact.ud_agreement_date` | October 16, 2026 |
| UD Invoice Number | `contact.ud_invoice_number` | 144 |
| UD Project Address | `contact.ud_project_address` | 16411 Barclay Court, Naples, FL 34110 |
| UD Service Dates | `contact.ud_service_dates` | Monday, October 19, 2026 (one 8-hour service day) |
| UD Total | `contact.ud_total` | $1,000 |
| UD Scope Of Work | `contact.ud_scope_of_work` | the scope bullets, one per line, then the labor sentence |
| UD Payment Terms | `contact.ud_payment_terms` | Total Service Fee / materials / deposit / balance lines |
| UD Scope Limits | `contact.ud_scope_limits` | the full scope-limits paragraph (day count and day rate vary) |

Yvonne Bourk's contact already has all eight filled in from her move contract, so you can use her to preview the template while you build it.
