"""Build a compact on-screen form schema for all 43 inventory forms.

Sources (read-only):
  rules/forms/<id>/fields.json   fields, controls, types, items, pages
  html-frozen/<slug>/index.html  printed item labels and Part headings
  crates/bir-core/src/forms/registry.rs  titles and filing frequency
"""
import html, json, re, sys
from pathlib import Path

REPO = Path(sys.argv[1])
OUT = Path(sys.argv[2])

inv = json.loads((REPO / "html-frozen/inventory.json").read_text())

# --- registry titles ---------------------------------------------------
reg = (REPO / "crates/bir-core/src/forms/registry.rs").read_text()
REG = {}
for m in re.finditer(r'code:\s*"([^"]+)",\s*title:\s*"([^"]+)",(.*?)frequency:\s*FilingFrequency::(\w+)', reg, re.S):
    REG.setdefault(m.group(1).upper(), (m.group(2), m.group(4)))

FREQ = {"Monthly": "Monthly", "Quarterly": "Quarterly", "Annual": "Annual", "Annually": "Annual",
        "OpenEnded": "As needed", "OneTime": "As needed"}

# --- frozen paper text -------------------------------------------------
RUN = re.compile(r'<div class="t" id="p(\d+)t\d+" style="left:([\d.]+)pt;top:([\d.]+)pt;[^"]*?font-size:([\d.]+)pt;font-weight:(\d+)[^"]*">(.*?)</div>', re.S)
TAG = re.compile(r"<[^>]+>")


def paper_lines(slug):
    p = REPO / "html-frozen" / slug / "index.html"
    s = p.read_text(errors="replace")
    runs = []
    for m in RUN.finditer(s):
        txt = html.unescape(TAG.sub("", m.group(6))).replace("\xa0", " ").strip()
        if txt:
            runs.append((int(m.group(1)), float(m.group(3)), float(m.group(2)), txt, int(m.group(5))))
    pages = len(re.findall(r'class="page page-\d+"', s))
    runs.sort()
    lines = []
    for r in runs:
        if lines and lines[-1][0] == r[0] and abs(lines[-1][1] - r[1]) <= 2.0:
            lines[-1][2].append(r)
        else:
            lines.append([r[0], r[1], [r]])
    for ln in lines:
        ln[2].sort(key=lambda r: r[2])
    return lines, pages


PART = re.compile(r"^(Part\s+[IVX]+[A-Z]?|PART\s+[IVX]+[A-Z]?|Schedule\s+[0-9IVX]+[A-Z]?|SCHEDULE\s+[0-9IVX]+[A-Z]?)\b\s*[-–—:.]?\s*(.*)$")


def clean(t):
    t = re.sub(r"\s+", " ", t).strip(" :.-–—")
    t = re.sub(r"\b([B-HJ-Z]) ([a-z]{2,})", r"\1\2", t)
    t = re.sub(r"(?:\s+(?:Yes|No))+$", "", t)
    t = re.sub(r"(?:\s+[/0-9])+$", "", t)
    t = re.sub(r"\s+\)", ")", t).replace("( ", "(")
    t = re.sub(r"\s*\(?\s*(?:To be filled up by BIR|Continuation)\s*\)?$", "", t, flags=re.I)
    return t.strip()


def title_case_heading(t):
    if t.isupper() and len(t) > 4:
        small = {"of", "and", "or", "the", "for", "to", "in", "on", "a", "an", "per", "by", "from", "with"}
        words = t.lower().split()
        return " ".join(w if (i and w in small) else (w.upper() if w in {"vat", "atc", "tin", "rdo", "bir", "zip"} else w.capitalize()) for i, w in enumerate(words))
    return t


def paper_index(slug, item_numbers):
    lines, pages = paper_lines(slug)
    parts, items = [], {}
    for page, top, runs in lines:
        joined = clean(" ".join(r[3] for r in runs))
        pm = PART.match(joined)
        if pm and len(joined) < 140:
            name = clean(pm.group(1).title().replace("Iv", "IV").replace("Iii", "III").replace("Ii", "II").replace("Vi", "VI"))
            name = re.sub(r"\b([IVX]+)\b", lambda m: m.group(1).upper(), name)
            rest = title_case_heading(clean(pm.group(2)))
            parts.append((page, top, f"{name} · {rest}" if rest else name))
            continue
        # item numbers: a run that is exactly a known item number, or starts with one
        i = 0
        while i < len(runs):
            txt = runs[i][3]
            m = re.match(r"^(\d{1,3}[A-Z]?)(?:\s+(.*))?$", txt)
            if m and m.group(1) in item_numbers and (page, m.group(1)) not in items:
                label_parts = [m.group(2)] if m.group(2) else []
                j = i + 1
                while j < len(runs):
                    nm = re.match(r"^(\d{1,3}[A-Z]?)(?:\s|$)", runs[j][3])
                    if nm and nm.group(1) in item_numbers and nm.group(1) != m.group(1):
                        break
                    label_parts.append(runs[j][3])
                    j += 1
                items[(page, m.group(1))] = (top, [clean(x) for x in label_parts if clean(x)])
                i = j
            else:
                i += 1
    return parts, items, pages


# --- field helpers ------------------------------------------------------
PREFIX = re.compile(r"^(txt|rtn|opt|chk|sel|cbo|rdo|drp|lst|hdn|frm|cb|op|rb|ch|txa|num|amt|dt|lbl)(?=[A-Z_0-9])")


def human_key(key):
    k = key.split(":", 1)[-1]
    k = PREFIX.sub("", k)
    k = re.sub(r"([a-z])([A-Z])", r"\1 \2", k)
    k = re.sub(r"[_\-]+", " ", k)
    k = re.sub(r"\s+", " ", k).strip()
    return (k[:1].upper() + k[1:]) if k else "Value"


def ev_label(v):
    if isinstance(v, dict):
        for k in ("label", "choice_meaning", "html_value", "value", "control_value", "stored_value"):
            if v.get(k) not in (None, ""):
                return str(v[k])
        return ""
    return str(v)


def kind(f):
    ck, lt = f["control_kind"], f["logical_type"]
    if "select" in ck:
        return "sel"
    if "checkbox" in ck and "radio" not in ck:
        return "chk"
    if "radio" in ck:
        return "radio"
    if lt in ("decimal-amount", "whole-peso-amount", "money", "decimal-money", "decimal"):
        return "money"
    if lt in ("percentage", "decimal-rate"):
        return "pct"
    if lt.startswith("date") or lt == "date":
        return "date"
    if lt in ("integer", "integer-year", "year", "year-string", "integer-string", "digit-string", "two-digit-tax-year"):
        return "int"
    if "email" in lt:
        return "email"
    if "phone" in lt:
        return "phone"
    return "text"


IDENTITY = re.compile(r"\b(TIN|RDO|registered name|taxpayer'?s? name|withholding agent'?s? name|registered address|zip|telephone|contact number|email)\b", re.I)

forms = []
for b in inv["bundles"]:
    fid, slug = b["form_id"], b["frozen_slug"]
    fj = json.loads((REPO / "rules/forms" / fid / "fields.json").read_text())
    code = fid.split("-v")[0].upper()
    rev = re.sub(r"^v", "", fid.split("-v", 1)[1])
    DROP_CK = ("hidden", "runtime-injected", "serialized-runtime", "final-copy", "negative")
    fields = [f for f in fj["fields"]
              if not any(f["control_kind"].startswith(d) or d in f["control_kind"] for d in DROP_CK)
              and f["required"] != "hidden"
              and not (re.search(r"Pg[2-9]\w*?(TIN|Tin|Name|Branch)", f["field_key"]) and (f["computed"] or f["required"] == "computed"))
              and not re.search(r"driveSelect|(^|:)hdn", f["field_key"])]
    item_numbers = {str(f["item_number"]) for f in fields if f["item_number"] not in (None, "")}
    parts, paper_items, pages = paper_index(slug, item_numbers)

    reg_key = code.replace("-", "")
    title, freq = REG.get(reg_key, REG.get(code, (None, None)))
    if not title:
        title = code

    # group consecutive fields by (page, item)
    groups = []
    for f in fields:
        item = str(f["item_number"]) if f["item_number"] not in (None, "") else ""
        key = (f["page"] or 1, item)
        if groups and groups[-1]["key"] == key:
            groups[-1]["fields"].append(f)
        elif item and any(g["key"] == key for g in groups):
            next(g for g in groups if g["key"] == key)["fields"].append(f)
        else:
            groups.append({"key": key, "fields": [f]})

    def paper_pos(page, item):
        if (page, item) in paper_items:
            return page, paper_items[(page, item)][0], paper_items[(page, item)][1]
        for (p, it), v in paper_items.items():
            if it == item:
                return p, v[0], v[1]
        return None

    out_parts = []
    current = None
    stats = {"items": 0, "paper_labels": 0}
    for g in groups:
        page, item = g["key"]
        pos = paper_pos(page, item) if item else None
        part_name = None
        if pos:
            cands = [p for p in parts if (p[0], p[1]) <= (pos[0], pos[1])]
            if cands:
                part_name = cands[-1][2]
        if part_name is None:
            part_name = current["n"] if current else ("Page %s" % (page or 1))
        if not current or current["n"] != part_name:
            current = next((p for p in out_parts if p["n"] == part_name), None)
            if not current:
                current = {"n": part_name, "items": []}
                out_parts.append(current)

        fs = g["fields"]
        human = [f["label"] for f in fs if f["label"] != f["field_key"]]
        paper_label_runs = pos[2] if pos else []
        radios_raw = [f for f in fs if kind(f) == "radio" and f["label"] == f["field_key"]]
        opt_names = []
        if radios_raw and len(paper_label_runs) > len(radios_raw):
            opt_names = paper_label_runs[-len(radios_raw):]
            paper_label_runs = paper_label_runs[:-len(radios_raw)]
        label = clean(" ".join(paper_label_runs))[:160]
        hl = [h for h in human if not re.fullmatch(r"[A-Za-z0-9_]+", h)]
        if len(fs) == 1 and hl:
            label = hl[0]
        elif len(hl) >= 2 and len({re.split(r"\s[-–:]\s|:", h)[0].strip() for h in hl}) == 1 and not label:
            label = re.split(r"\s[-–:]\s|:", hl[0])[0].strip()
        if label:
            stats["paper_labels"] += 1
        elif human:
            pre = human[0].split(":")[0]
            label = pre if all(h.startswith(pre) for h in human) else human[0]
        elif item:
            label = "Item %s" % item
        else:
            label = "Additional details"
        stats["items"] += 1

        if len(radios_raw) == 2 and not opt_names and pos and any(r in ("Yes", "No") for r in " ".join(pos[2]).split()) or (len(radios_raw) == 2 and not opt_names and label.endswith("?")):
            opt_names = ["Yes", "No"]
        out_fields = []
        ri = 0
        for f in fs:
            k = kind(f)
            if f["label"] != f["field_key"] and re.fullmatch(r"[A-Za-z0-9_]+", f["label"]) and not re.fullmatch(r"\d+[A-Z]?", f["label"]):
                fl = human_key(f["label"])
            elif f["label"] != f["field_key"]:
                fl = f["label"]
                if ":" in fl and fl.split(":")[0].strip() == label:
                    fl = fl.split(":", 1)[1].strip()
            elif k == "radio" and opt_names:
                fl = opt_names[ri] if ri < len(opt_names) else "Option %d" % (ri + 1)
                ri += 1
            else:
                fl = human_key(f["field_key"])
            o = {"l": fl[:120], "t": k}
            req = f["required"]
            if req == "required":
                o["r"] = 1
            if f["computed"] or req == "computed":
                o["c"] = 1
            ml = (f.get("constraints") or {}).get("max_length")
            if ml:
                o["m"] = ml
            if k == "radio":
                cm = [v.get("choice_meaning") for v in (f.get("enum_values") or []) if isinstance(v, dict) and v.get("choice_meaning")]
                if cm and (fl == label or re.fullmatch(r"(?i)(option \d+|yes|no|.*\d)", fl) or fl.startswith(label[:12])):
                    o["l"] = cm[0][:60]
            ev = [ev_label(v) for v in (f.get("enum_values") or []) if ev_label(v) not in ("true", "false", "")]
            if ev and k == "sel":
                o["o"] = ev[:40]
            if IDENTITY.search(fl) or IDENTITY.search(label if item in {"1", "2", "3", "4", "5", "6", "7", "8", "9", "9A", "10", "11", "12"} else ""):
                if k in ("text", "email", "phone", "int", "sel") and not o.get("c"):
                    o["a"] = 1
            out_fields.append(o)
        rl = [o for o in out_fields if o["t"] == "radio"]
        generic = len(rl) >= 2 and (len({o["l"] for o in rl}) == 1 or all(re.fullmatch(r"(?i)(option \d+|yes|no|.*\d)", o["l"]) for o in rl))
        if generic and pos and len(pos[2]) > len(rl) and not opt_names:
            runs_ = [clean(x) for x in pos[2] if clean(x)]
            if len(runs_) > len(rl) and all(len(x) <= 40 for x in runs_[-len(rl):]):
                for o, nm in zip(rl, runs_[-len(rl):]):
                    o["l"] = nm
                head = clean(" ".join(runs_[:-len(rl)]))
                if head and len(fs) == len(rl):
                    label = head
                generic = False
        if generic and len({o["l"] for o in rl}) == 1:
            names = (["Yes", "No"] if len(rl) == 2 else
                     ["1st", "2nd", "3rd", "4th"] if len(rl) == 4 and re.search(r"quarter", label, re.I) else
                     ["Option %d" % (n + 1) for n in range(len(rl))])
            for o, nm in zip(rl, names):
                o["l"] = nm
        if re.search(r"quarter", label, re.I) and len(rl) == 4 and all(re.fullmatch(r"(?i)qtr ?\d", o["l"]) for o in rl):
            for o, nm in zip(rl, ["1st", "2nd", "3rd", "4th"]):
                o["l"] = nm
        current["items"].append({"no": item, "l": label, "p": page, "f": out_fields})

    # merge unnumbered companions (Tra1 next to "row 1") into the row before them
    for part in out_parts:
        merged = []
        for it in part["items"]:
            if not it["no"] and merged:
                tail = {re.search(r"(\d+)$", x["l"]).group(1) for x in it["f"] if re.search(r"(\d+)$", x["l"])}
                prev = merged[-1]
                ptoks = set(re.findall(r"\b\d+\b", prev["no"] + " " + " ".join(x["l"] for x in prev["f"])))
                if tail and len(tail) == 1 and tail <= ptoks and re.search(r"row|\d$", prev["no"] + prev["f"][0]["l"], re.I):
                    prev["f"].extend(it["f"])
                    continue
            merged.append(it)
        part["items"] = merged

    # collapse runs of repeated rows into one table item
    def rowsig(it):
        labs = tuple(re.sub(r"\s+", " ", re.sub(r"\b(?:row\s*)?\d+\b|\d+$", "#", x["l"], flags=re.I)).strip() for x in it["f"])
        kinds = tuple(x["t"] for x in it["f"])
        return (labs, kinds)

    def colname(lbl, prefix):
        s = re.sub(r"(?i)^.*?\brow\s*\d+\s*", "", lbl)
        s = re.sub(r"\s*\d+$", "", s).strip(" -:_")
        s = re.sub(r"(?i)\s*-\s*item\s*#?$", "", s).strip()
        return human_key(s) if re.fullmatch(r"[A-Za-z0-9_]+", s) and s else (s or "Value")

    for part in out_parts:
        items, out, i = part["items"], [], 0
        while i < len(items):
            j = i + 1
            sig = rowsig(items[i])
            while j < len(items) and rowsig(items[j]) == sig and len(items[j]["f"]) == len(items[i]["f"]):
                j += 1
            run = items[i:j]
            if len(run) >= 3 and len(run[0]["f"]) >= 2 and not all(re.fullmatch(r"(?i)yes|no|option \d+", x["l"]) for x in run[0]["f"]):
                first = run[0]
                base = re.sub(r"(?i)\s*row\s*\d+$", "", first["no"]).strip()
                lbl = first["l"]
                if re.search(r"(?i)row\s*\d+", lbl) or re.search(r"(?i)row\s*\d+", first["no"]) or not first["no"]:
                    lbl = re.sub(r"(?i)\s*row\s*\d+.*$", "", lbl).strip() or base or "Schedule rows"
                out.append({"no": "" if re.search(r"(?i)row", first["no"]) else first["no"], "l": lbl, "p": first["p"],
                            "cols": [{"l": colname(x["l"], base), "t": x["t"], **({"c": 1} if x.get("c") else {})} for x in first["f"]],
                            "rows": len(run)})
                i = j
            else:
                out.append(items[i])
                i += 1
        part["items"] = out

    forms.append({
        "c": code, "id": fid, "s": slug, "g": 1 if (REPO / "html-frozen" / slug / "guide.html").exists() else 0, "t": title, "rev": rev, "freq": FREQ.get(freq or "", freq or "As needed"),
        "pages": pages, "n": len(fields), "parts": out_parts, "stats": stats,
        "q": round(1 - sum(len(it.get("f", [])) for pt in out_parts for it in pt["items"] if it["l"] == "Additional details") / max(1, len(fields)), 2),
    })

order = {"Monthly": 0, "Quarterly": 1, "Annual": 2, "As needed": 3}
forms.sort(key=lambda f: f["c"])
OUT.write_text(json.dumps(forms, separators=(",", ":"), ensure_ascii=False))
tot = sum(f["n"] for f in forms)
print(len(forms), "forms", tot, "fields", OUT.stat().st_size // 1024, "KB")
for f in forms:
    s = f["stats"]
    print(f"{f['c']:8} {f['freq']:10} p{f['pages']} parts={len(f['parts']):2} items={s['items']:3} paperlabels={s['paper_labels']:3} {f['t'][:60]}")
