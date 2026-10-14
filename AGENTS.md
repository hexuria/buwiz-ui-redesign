# AGENTS.md — buwiz UI redesign

This repo is the **design reference** for the eBIRForms desktop app redesign.
The product code lives in [hexuria/buwiz-forms](https://github.com/hexuria/buwiz-forms).
Nothing here ships; everything here is the spec that product code must match.

The UI there is moving to **gpui-shell**: JavaScript views in `app/`
(`app/main.js`, `app/shell/*.js`) on a thin Rust host, `crates/bir-shell`,
which exposes bir-core through the `bir` host module. Its plan and cutover gate
are in buwiz-forms `docs/plans/gpui-shell-migration.md` (issue #135). The
painted Rust UI in `crates/bir-desktop` stays the reference until that gate
passes. Build new screens in whichever layer the request names; the design is
the same in both.

[hexuria/ebirforms PR #8](https://github.com/hexuria/ebirforms/pull/8) built
this design end to end in another GPUI binding (gpuix, React): the shell, all
43 form pages, and the tax-profile flows in `DESIGN_SYSTEM.md` (tax years,
the Forms edit mode, TIN editing, templates, empty state). Read it for
behaviour and data rules (`apps/desktop/src/app.tsx`,
`packages/core/src/store.ts`). Leave its gpuix workarounds behind; the
lessons section below says which those are.

Sources of truth, one meaning each:

- `DESIGN_SYSTEM.md`: every token, size, component and layout rule. Read it
  in full before any UI work, whatever the task.
- `prototype/shell-prototype.html`: what the result looks and behaves like.
  It has three tabs: App, Components, Forms.
- `forms/forms-schema.json`: the shape of every on-screen form (43 forms),
  with each field's rules-corpus key in `k`.

Pick the task below that matches the request, follow its steps in order, and
stop only when its **Done** line holds.

## Task: build or restyle UI in buwiz-forms

1. Read `DESIGN_SYSTEM.md` end to end, then buwiz-forms' own `CLAUDE.md`.
   Its rules govern work in that repo.
2. Open the prototype. Find the screen you are building in the App tab, and
   its parts in the Components tab. Note every size, spacing, state and
   theme value you see there. Each one has a token in `DESIGN_SYSTEM.md`.
3. Make sure the wrapper components from `DESIGN_SYSTEM.md` exist
   (IconButton, AppButton, NavRow, ContextPill, Avatar, Disclosure, Field,
   StatusChip, SidePanel, Segmented), and build any missing ones first: in
   gpui-shell as one shared module under `app/shell/`, in the painted UI in
   `crates/bir-desktop/src/components/ui/`. Screens call the wrappers.
   Sizes and colors come from the wrappers and tokens.
4. Port one screen at a time with the porting checklist at the end of
   `DESIGN_SYSTEM.md`.
5. For form pages, render from the schema shape: parts, then items, then
   fields or tables. Use the "Form page" section of `DESIGN_SYSTEM.md`. The
   `html-frozen/` sheets in buwiz-forms are the print output; they stay
   exactly as they are.

6. For the tax-profile screens, follow "Empty state" and "Tax profile: tax
   years, forms, TIN and templates" in `DESIGN_SYSTEM.md`. The year bound
   (2010 to next year) and the one-transaction TIN move belong in bir-core,
   not only in the view, so no other caller can get past them.

**Done:** every checklist item holds for the screen, in light and dark, on
Windows and macOS, at full width and at 800 px. Every new control has a
stable gpui-agent id. For a scrolling screen, a sideways trackpad swipe
moves nothing sideways.

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
mode. The canvas predates tax years per branch and the Forms edit mode: its
Forms screen shows the old fixed year control and an always-on checklist.
Where it and `DESIGN_SYSTEM.md` differ, `DESIGN_SYSTEM.md` and the prototype
win.

## Lessons from the ebirforms build (2026-10-15)

Measured in hexuria/ebirforms PR #8. gpuix lays out with Taffy, as GPUI does,
so the layout lessons carry over; the last group does not.

- **Scroll one axis.** Give pages and side panels vertical-only scrolling
  (`overflow_y_scroll()` in gpui-shell, never `overflow_scroll()`). Both-axis
  scrollers let every page drift sideways under a trackpad. With y only, GPUI
  turns a perfectly sideways wheel event into a vertical scroll; that is
  expected.
- **Give the content column a definite width.** An auto-width column
  stretched by a flex-grow parent, and flex-grown text cells in a field grid,
  made the layout engine re-measure every text on every frame: Profile
  frames went from about 230 ms to 6 ms once the column and grid cells got
  pixel widths computed from the window size. Centre the column with computed
  side padding.
- **Keep reads out of render.** Synchronous database reads on every render
  cost more than the drawing. Cache them, invalidated by a data version that
  every write bumps. Click to page change was about 65 ms after that.
- **Never block the UI on form work.** Opening a form and its first
  validation took 3 s (1601C) to 20 s (2550Q) and froze the window. Run them
  in the background (`cx.spawn`, or the `bir` host module's async functions)
  and apply edits optimistically; see "Form page" in `DESIGN_SYSTEM.md`.
- **Use a virtual list** for long lists (the 43-form library, Filings).
- **gpuix-only, leave behind:** the `once()` click de-duplicator (gpuix
  delivered each click twice), the custom Dropdown (gpuix's select showed
  the raw value), the single-scroller page (gpuix has no nested scrolling;
  GPUI does), and the `fontVariantNumeric` removal.

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
