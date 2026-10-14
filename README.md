# buwiz UI redesign

Design reference for the eBIRForms desktop app redesign (2026-10-14): one design
system, an interactive shell prototype, on-screen form pages for all 43 BIR
forms, and the tax-profile screen designs. Use it to brief agents when building
the real UI in [hexuria/buwiz-forms](https://github.com/hexuria/buwiz-forms)
(`crates/bir-desktop`, GPUI).

All taxpayers, TINs, addresses and emails in here are made-up sample data.

Agents: read [`AGENTS.md`](AGENTS.md) first. It says how to use each file for each kind of task.

## What's here

| Path | What it is |
| --- | --- |
| [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md) | **Start here.** The rules agents follow: tokens (light and dark), type, sizes, the wrapper components to build first, shell layout, the disclosure that replaces the old collapsible, the empty state, the tax-profile flows (tax years per branch, the Forms edit mode with starter packs, TIN editing, templates), the form-page rules, and a porting checklist. |
| [`prototype/shell-prototype.html`](prototype/shell-prototype.html) | The interactive prototype, and the current one: the published claude.ai version 4 predates the tax-profile flows. Open it in a browser. Tabs: **App** (the redesigned shell), **Components** (the design system rendered live), **Forms** (all 43 forms as screen form pages). |
| `prototype/shell-prototype.src.html` | The editable source of the prototype. It has a `__FORMS_JSON__` placeholder where the form data goes. Edit this, then rebuild. |
| `forms/forms_extract.py` | Builds the form schema from a buwiz-forms checkout. It only reads: `rules/forms/*/fields.json`, the `html-frozen/*/index.html` text layer, and `crates/bir-core/src/forms/registry.rs`. |
| `forms/forms-schema.json` | Its output: 43 forms, 9,185 visible fields, grouped into Parts, numbered items and schedule tables. Each field has `k`, its rules-corpus `field_key`; each table has `keys`, one per cell. |
| `design-canvas/tax-profile-screens/` | Source of the "Tax Profile Screens" design canvas: Profile with the panel open, branch address editing, Forms tab, Templates tab, and a dark-mode panel edit. `canvas.json` is the layout; each `.dc.html` is one screen. |
| `scripts/build_prototype.py` | Inlines the schema into the source page. |

## Using the prototype

```sh
open prototype/shell-prototype.html          # macOS; or double-click it
```

**Print preview** opens the official frozen BIR sheet beside the screen form,
for checking one against the other. It loads the sheets from buwiz-forms'
`html-frozen/` by a relative path, so the page needs to sit where it can reach
that folder:

- Inside a buwiz-forms checkout at `docs/ui-redesign/` (the default,
  `../../html-frozen/`).
- Or clone this repo next to buwiz-forms and rebuild with
  `python3 scripts/build_prototype.py --frozen-base ../../buwiz-forms/html-frozen/`.

If the drawer's page height looks wrong when opened from `file://`, serve the
folder instead: `python3 -m http.server` and open it via `localhost`.

## Rebuilding

```sh
# 1. regenerate the form schema from a buwiz-forms checkout
python3 -I forms/forms_extract.py /path/to/buwiz-forms forms/forms-schema.json

# 2. rebuild the prototype page
python3 scripts/build_prototype.py
```

## Known gaps

- **8 forms show a "Draft layout" chip:** 2550Q, 2551Q, 1701A, 1701, 2200S,
  1700, 1701MS and 2200M. Under 80 % of their fields sit under a numbered item
  or table in the rules corpus. The leftovers appear in a collapsed "more
  fields" block rather than being hidden. Fix the source data rather than the
  renderer.
- **1601EQ:** the frozen paper is the 2019 revision while the rules corpus
  describes the 2018 runtime, so Part II numbering differs by one item. The
  page uses the rules corpus labels.
- The screen form does no tax computation yet. Computed fields are shown
  locked at 0.00.

## Briefing an agent

> Build the redesigned shell and form pages in `crates/bir-desktop` following
> `DESIGN_SYSTEM.md` from hexuria/buwiz-ui-redesign. Build the wrapper
> components first (IconButton, AppButton, NavRow, ContextPill, Avatar,
> Disclosure, Field, StatusChip, SidePanel, Segmented). Never call
> gpui-component `.small()` or `Icon::size()` directly. Match
> `prototype/shell-prototype.html`. Render forms from the schema shape in
> `forms/forms-schema.json`; the printed `html-frozen` sheets stay the print
> output and must not be restyled.
