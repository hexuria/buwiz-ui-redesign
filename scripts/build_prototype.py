"""Build prototype/shell-prototype.html from its source and the form schema.

    python3 scripts/build_prototype.py
    python3 scripts/build_prototype.py --frozen-base ../../buwiz-forms/html-frozen/

The source page carries a __FORMS_JSON__ placeholder; this inlines
forms/forms-schema.json there. --frozen-base changes where Print preview looks
for the official html-frozen sheets when the page is opened locally (the path
is relative to the built page).
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ap = argparse.ArgumentParser()
ap.add_argument("--schema", default=ROOT / "forms/forms-schema.json", type=Path)
ap.add_argument("--src", default=ROOT / "prototype/shell-prototype.src.html", type=Path)
ap.add_argument("--out", default=ROOT / "prototype/shell-prototype.html", type=Path)
ap.add_argument("--frozen-base", default=None, help="e.g. ../../html-frozen/ (default: keep the source's value)")
args = ap.parse_args()

src = args.src.read_text()
if src.count("__FORMS_JSON__") != 1:
    raise SystemExit("source must contain exactly one __FORMS_JSON__ placeholder")
if args.frozen_base:
    src, n = re.subn(r"const SHEET_BASE='[^']*';", f"const SHEET_BASE='{args.frozen_base}';", src)
    if n != 1:
        raise SystemExit("could not find SHEET_BASE in the source")
data = args.schema.read_text().replace("</", "<\\/")
args.out.write_text(src.replace("__FORMS_JSON__", data))
print(f"wrote {args.out} ({args.out.stat().st_size // 1024} KB)")
