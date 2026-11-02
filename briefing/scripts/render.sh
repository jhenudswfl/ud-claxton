#!/usr/bin/env bash
# Render a finished briefing HTML to a Letter PDF with the brand font installed.
# Usage: scripts/render.sh <input.html> <output.pdf>
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
IN="$1"; OUT="$2"
mkdir -p ~/.fonts
cp -n "$HERE"/assets/fonts/PlusJakartaSans-*.ttf ~/.fonts/ 2>/dev/null || true
fc-cache -f >/dev/null 2>&1 || true
if command -v wkhtmltopdf >/dev/null 2>&1; then
  wkhtmltopdf --enable-local-file-access -s Letter -T 16mm -B 16mm -L 16mm -R 16mm --quiet "$IN" "$OUT"
else
  python3 -m pip install -q --break-system-packages weasyprint >/dev/null 2>&1 || true
  python3 - "$IN" "$OUT" <<'PY'
import sys; from weasyprint import HTML, CSS
HTML(sys.argv[1]).write_pdf(sys.argv[2], stylesheets=[CSS(string='@page{size:Letter;margin:16mm}')])
PY
fi
PAGES=$(python3 -c "import sys;from pypdf import PdfReader;print(len(PdfReader(sys.argv[1]).pages))" "$OUT" 2>/dev/null || pdfinfo "$OUT" | awk '/^Pages/{print $2}')
echo "Rendered $OUT — $PAGES page(s)"
if [ "$PAGES" -gt 2 ]; then
  echo "WARNING: over 2 pages. Tighten copy (clock line, context bullets) rather than shrinking type."
fi
for ((p=1; p<PAGES; p++)); do
  LAST=$(pdftotext -f $p -l $p "$OUT" - 2>/dev/null | sed '/^\s*$/d' | tail -1)
  if echo "$LAST" | grep -Eq '^[0-9]+\. |^(Context|Start Of Day|The Plan|End Of Day)$'; then
    echo "WARNING: heading orphaned at bottom of page $p: '$LAST' — wrap that heading and its first block in <div style=\"page-break-inside:avoid\">."
  fi
done
