# AGENTS.md — buwiz UI redesign

This repo is the **design reference** for the eBIRForms desktop app redesign.
The product code lives in [hexuria/buwiz-forms](https://github.com/hexuria/buwiz-forms)
(`crates/bir-desktop`, Rust + GPUI). Nothing here ships; everything here is the
spec that product code must match.

Sources of truth, one meaning each:

- `DESIGN_SYSTEM.md`: every token, size, component and layout rule. Read it
  in full before any UI work, whatever the task.
- `prototype/shell-prototype.html`: what the result looks and behaves like.
  It has three tabs: App, Components, Forms.
- `forms/forms-schema.json`: the shape of every on-screen form (43 forms).

Pick the task below that matches the request, follow its steps in order, and
stop only when its **Done** line holds.

## Task: build or restyle UI in buwiz-forms

1. Read `DESIGN_SYSTEM.md` end to end, then buwiz-forms' own `CLAUDE.md`.
   Its rules govern work in that repo.
2. Open the prototype. Find the screen you are building in the App tab, and
   its parts in the Components tab. Note every size, spacing, state and
   theme value you see there. Each one has a token in `DESIGN_SYSTEM.md`.
3. Make sure the wrapper components from `DESIGN_SYSTEM.md` exist in
   `crates/bir-desktop/src/components/ui/` (IconButton, AppButton, NavRow,
   ContextPill, Avatar, Disclosure, Field, StatusChip, SidePanel,
   Segmented), and build any missing ones first. Screens call the wrappers.
   Sizes and colors come from the wrappers and tokens.
4. Port one screen at a time with the porting checklist at the end of
   `DESIGN_SYSTEM.md`.
5. For form pages, render from the schema shape: parts, then items, then
   fields or tables. Use the "Form page" section of `DESIGN_SYSTEM.md`. The
   `html-frozen/` sheets in buwiz-forms are the print output; they stay
   exactly as they are.

**Done:** every checklist item holds for the screen, in light and dark, on
Windows and macOS, at full width and at 800 px. Every new control has a
stable gpui-agent id.

## Task: change the prototype

1. Edit `prototype/shell-prototype.src.html`. The built
   `prototype/shell-prototype.html` is generated, so leave it to the build.
2. Rebuild: `python3 scripts/build_prototype.py`.
3. Open the built page and click through what you changed in Light, Dark
   and System, at desktop width and at ~420 px. Watch the console.
4. If a value changed (a size, a color, a rule), update `DESIGN_SYSTEM.md`
   in the same change, so the spec and the prototype say the same thing.

**Done:** the built page is regenerated, works in both themes and at phone
width with an empty console, and `DESIGN_SYSTEM.md` matches it.

## Task: regenerate the form schema

1. Run against a current buwiz-forms checkout:
   `python3 -I forms/forms_extract.py /path/to/buwiz-forms forms/forms-schema.json`.
   The extractor only reads that checkout.
2. Compare the printed counts with the last run: 43 forms and 9,185 fields
   as of 2026-10-14. Account for every change in counts and in the "Draft
   layout" list (forms where `q < 0.8`). Each one traces to a change in
   `rules/forms/*/fields.json` or `html-frozen/`.
3. Rebuild the prototype and open three forms in the Forms tab: one simple
   (0619E), one with schedule tables (1601EQ) and one large one (1702MX).

**Done:** every count change is explained, and the three forms render with
real labels.

When a form looks wrong, fix the source data in buwiz-forms (rules corpus or
frozen sheet) or the extractor's grouping, and record why. The renderer shows
what the data says.

## Task: change the design rules

`DESIGN_SYSTEM.md` is the single source. Edit it, then carry the change
into the prototype's Components tab (Task: change the prototype) and into the
canvas screens it affects.

**Done:** the spec, the Components tab and the canvas agree.

## Task: use the design canvas

`design-canvas/tax-profile-screens/` holds the source of the "Tax Profile
Screens" canvas: `canvas.json` (layout) and one `.dc.html` per screen. It runs
inside the claude.ai Design canvas, not as a plain page. Read the `.dc.html`
markup as the exact layout and copy spec for the tax-profile screens:
Profile, branch editing with "Same as head office", Forms, Templates, and dark
mode.

## Facts that are easy to lose

- gpui-component 0.6.1 sizes `.small()` buttons at 24 px and `.medium()` at
  32 px. The design needs 28 and 32, which is why the wrappers exist.
- TINs, branch codes and form codes use the UI font with tabular digits.
  Monospace makes them look letter-spaced.
- Print preview finds the official sheets by a relative path: by default
  `../../html-frozen/`, which works when the page sits in buwiz-forms at
  `docs/ui-redesign/`. To use another layout, rebuild with
  `--frozen-base`.
- 1601EQ's frozen paper is the 2019 revision and its rules are the 2018
  runtime. Labels follow the rules corpus.
- All taxpayer data here is made up. Keep examples fictional.
