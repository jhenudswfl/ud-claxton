# ud-claxton

The document toolbox for Utter Declutter's Claxton run: builds the branded proposal, service agreement
and invoice PDFs from one `deal.json`, plus the brand assets the proposal uses.

No client data lives here. Deals, PDFs and invoices live in Claxton (the claude.ai app), GoHighLevel and Google Drive.

```
python3 builder/build_deal.py deal.json --out ./out --assets ./assets --skip-view --leaks "Previous,Client,Names"
```

See the top of `builder/build_deal.py` for the `deal.json` shape and `builder/README.md` for the QA rules.
Brand: Utter Declutter brand kit v2c (Plus Jakarta Sans, cocoa / paper / sand / bronze / palm).
