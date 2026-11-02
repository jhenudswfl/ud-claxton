# Claxton builder

One command builds the full UD client document set (proposal, service agreement, invoice) as PDFs:

    python3 build_deal.py deal.json --out ./out --assets "../assets"

deal.json shape and all rules are documented at the top of build_deal.py. The script installs its own
dependencies (fonts, weasyprint, pymupdf) if missing, needs `node` with the `docx` package and LibreOffice
for the PDF conversion, and exits non-zero with a JSON `problems` list if any QA check fails
(page counts, previous-client leaks, internal-cost words, missing totals, install language on a
no-install job, signatures not on the final contract page).

Copy variants live in `copy_for()` — edit wording there, never in the templates.
`proposal_base.html` is the canonical 6-page layout (photo page auto-drops for non-garage jobs).
`docs_html.py` renders the service agreement, invoice and deposit invoice in brand kit v2c (weasyprint). `legacy/docs.js` is the old Times New Roman docx version, kept for reference only.
