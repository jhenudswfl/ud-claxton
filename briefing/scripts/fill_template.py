#!/usr/bin/env python3
"""Fill assets/template.html from a JSON file of section HTML.
Usage: fill_template.py <fields.json> <out.html>
fields.json keys: CLIENT_NAME, DATE, START, ADDRESS, PHONE, CREW, SCOPE,
                  CLOCK, CONTEXT, START_OF_DAY, PLAN, END_OF_DAY  (all raw HTML strings)
LOGO is inserted automatically from assets/logo.svg.
"""
import json, sys, pathlib
here = pathlib.Path(__file__).resolve().parent.parent
fields = json.load(open(sys.argv[1]))
fields['LOGO'] = (here/'assets/logo.svg').read_text()
t = (here/'assets/template.html').read_text()
for k, v in fields.items():
    t = t.replace('{{'+k+'}}', v)
missing = [l for l in t.splitlines() if '{{' in l]
if missing:
    sys.exit('Unfilled placeholders: ' + ', '.join(missing))
pathlib.Path(sys.argv[2]).write_text(t)
print('wrote', sys.argv[2])
