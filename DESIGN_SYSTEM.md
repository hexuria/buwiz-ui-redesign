# eBIRForms desktop design system (shell redesign, 2026-10-14)

Read this before you build or restyle any desktop screen in
`crates/bir-desktop`. The interactive prototype at
`docs/ui-redesign/shell-prototype.html` (published copy:
https://claude.ai/artifact/UdGGALWrSBg2ipnYZS9VfW) shows the visual source of
truth. Its **Components** tab renders every part listed here, in light and
dark.

This document is about app chrome and screens. It does not apply to the
printed BIR form renderers (`packages/form-renderer`), which follow the
official-fidelity rules in `CLAUDE.md`.

## Why this exists

The current UI picks sizes by eye. `sidebar.rs` and `top_bar.rs` alone use
icons at 14, 16, 18, 20, 24 and 28 px. gpui-component 0.6.1 sizes buttons at
24 px for `.small()` and 32 px for `.medium()`, with nothing in between, and
`.small()` is used about 125 times. The fix has two parts: one fixed set of
numbers, and wrapper components that apply them, so screens never call
`.small()` or `Icon::size()` directly.

## Hard rules

1. **Icons are 16 px**, Lucide, everywhere in chrome, nav rows, buttons and
   fields. The only exceptions are 12 px inside chips and 14 px for the
   context-pill chevron and segmented-control icons. Never use 18, 20, 24
   or 28.
2. **Spacing is on a 4 px grid:** 4, 8, 12, 16, 20, 24, 32. Icon buttons
   that sit in a row are 4 px apart.
3. **There are two control heights:** 28 px for chrome and dense rows (icon
   buttons, small buttons) and 32 px for inputs, nav rows and default
   buttons.
4. **The title bar and the panels have no separators.** Spacing does the
   grouping. Hairlines (1 px `border`) appear only between list rows and
   between disclosure sections.
5. **There is one accent color.** Use it for focus, Draft status, the
   unread dot and the "on" state of a switch. The primary button is
   inverted ink (`primary`), not accent blue.
6. **A panel closes from its own trigger.** The right panel has no close
   button. The pill or the bell that opened it closes it again, and Esc
   closes it too.
7. **Never use a literal color.** Every color comes from a token below, and
   each token has a light value and a dark value.

## Tokens

### Color

| Token | Light | Dark | Use | gpui-component `ThemeColor` field |
| --- | --- | --- | --- | --- |
| bg | `#f4f4f6` | `#0e0e10` | window ground, sidebars, right panel | `background`, `sidebar`, `title_bar` |
| surface | `#ffffff` | `#161619` | main content, inputs, dialogs | `popover` for dialogs; main surface needs an app token |
| raised | `#ffffff` | `#232328` | menus, selected segment | `popover` |
| hover | `#ebebee` | `#1f1f23` | hover fill, chip and segment track | `list_hover`, `secondary_hover` |
| selected | `#e2e2e7` | `#29292f` | current nav row, pressed icon button | `list_active`, `sidebar_accent` |
| border | `#e2e2e6` | `#25252a` | hairlines, card and list borders | `border`, `sidebar_border` (set equal to `border`) |
| border-strong | `#cdcdd3` | `#38383f` | inputs, secondary buttons | `input` |
| fg | `#18181b` | `#f3f3f5` | primary text and icons | `foreground` |
| fg-2 | `#54545d` | `#a7a7b1` | secondary text, resting icons | `muted_foreground` |
| fg-3 | `#71717a` | `#8b8b95` | labels, hints, placeholders (darkened from `#8a8a93` / `#73737d` to reach 4.5:1 on surface) | app token |
| primary | `#18181b` | `#f3f3f5` | primary button fill | `primary`, `button_primary` |
| accent | `#2557d6` | `#7ea2ff` | focus, Draft, unread, switch on | `ring`, `link`, `switch` (checked) |
| success | `#157a3c` | `#5bd68a` | Filed, Running | `success` |
| warning | `#a5520a` | `#f3b44a` | due within 14 days | `warning` |
| danger | `#c0262d` | `#ff7b7b` | overdue, destructive | `danger` |

Each semantic color also has a soft tint for chip and icon backgrounds:
10–14 % alpha of the same hue (`accent-soft`, `success-soft`, and so on).
`theme.rs` already has `*_on_tint` helpers for text on these tints. Keep
using them.

Where a `ThemeColor` field exists, set it from the table in one place (a
`apply_brand_tokens(theme)` in `theme.rs`, called after every theme change).
Where none exists (surface, fg-3), add an app-level `Tokens` struct in
`theme.rs` that is resolved from the current mode. Screens read
`cx.theme()` or `tokens(cx)` and never construct an `hsla(...)`.

### Type

The UI uses native faces: Segoe UI Variable on Windows and the system font
on macOS. TINs, branch codes and form codes use the **UI face with tabular
figures** (`font-variant-numeric: tabular-nums`; in GPUI, the UI font with
the `tnum` feature), **never a monospace face**. Monospace gives every
letter the same width, so `2551Q`, `1601EQ` and `009-123-456-00000` look
widely letter-spaced, especially where Menlo is the fallback. Monospace is
only for shell commands and code.

| Token | Size / weight | Use |
| --- | --- | --- |
| page | 20 / 600 | page title, one per view |
| title | 16 / 600 | section heading, dialog title, taxpayer name in the panel |
| emph | 14 / 600 | panel header, palette input |
| body | 13 / 400, 500 for controls | body text, buttons, nav rows, field values |
| meta | 12 / 400–500 | field labels, secondary lines, group labels |
| cap | 11 / 500 | chips, counts, keyboard hints |
| num | 12 / 600, tabular digits (UI face, not monospace) | `009-123-456-00000`, `2550Q` |

### Size, space, radius

| Thing | Value |
| --- | --- |
| Title bar | 40 px. Windows caption buttons 46 × 40. macOS traffic lights 12 px, 8 px apart |
| Left sidebar | 248 px wide, padding 4 / 8 / 8 |
| Right panel | 320 px wide |
| Main surface | radius 12, inset 8 px from the window edge and from the panels, 1 px `border` |
| Content column | max 880 px, padding 28 × 32 (20 × 16 below 640 px) |
| Icon button | 28 × 28, radius 6 |
| Button | 32 (md) or 28 (sm), horizontal padding 12 or 10, icon gap 6, radius 6 |
| Nav row | 32 tall, padding 0 8, gap 10, radius 8, 2 px between rows |
| Input | 32 tall, padding 0 10, radius 8 |
| List row | at least 52 tall, padding 8 × 16 |
| Avatar | 20 (rows, pill), 28 (account), 40 (page header), 56 (panel) |
| Radius scale | 6 controls · 8 rows and inputs · 12 cards and lists · 14 dialogs · full for pills, chips, avatars |

## Wrapper components (build these first)

Put them in `crates/bir-desktop/src/components/ui/` and export them from
`components/mod.rs`. Every screen uses these. Calling raw `Button` sizing or
`Icon::size` from a screen is a review finding.

| Wrapper | Builds on | Fixed values |
| --- | --- | --- |
| `IconButton::new(id, IconName)` | `Button::new(id).ghost().icon(..).with_size(px(28.))` | icon 16, fg-2 at rest, `selected` fill when `.pressed(true)`, `.tooltip(..)` required |
| `AppButton::primary / secondary / ghost / danger` | `Button` + explicit `.h(px(32.))` or `.h(px(28.))` via `.sm()` | label 13/500, leading icon 16, gap 6. `.small()` (24 px) is not allowed |
| `NavRow::new(id, IconName, label)` | `h_flex` | 32 tall, `.current(bool)`, optional `.count(n)`, label truncates |
| `ContextPill` | `h_flex` + `Avatar` | 30 tall, full radius, avatar 20, name 13/600, TIN mono 12, chevron 14 |
| `Avatar::initials(name, size)` | `div` | initials are the first and last capitalised words, hue derived from the taxpayer id |
| `Disclosure` / `DisclosureGroup` | `v_flex` | see below |
| `Field` | `v_flex` | label 12 fg-2, value 13; edit mode swaps in a 32 px input |
| `StatusChip::{NotStarted, Draft, Filed, DueSoon(days), Overdue}` | `div` | 20 tall, 11/500, soft tint, optional 12 px icon |
| `SidePanel` | `v_flex` | 320 wide on `bg`, 40 px header with a 14/600 title and at most one ghost action, no close button |
| `Segmented` | gpui-component tab bar (segmented) or `h_flex` | 2 px track padding, 24 px segments, 12/500 |

Give every wrapper a stable `gpui-agent` id parameter, as the tax-profile
spec requires for new controls.

## Shell layout

```
┌ title bar 40 ─────────────────────────────────────────────────────────────┐
│ [●●●] [⊟] [←] [→] [🔍][+]*      ( GC Goldcoders Corp 009-123-456-00000 ⌄ )   [🔔] [☀] [— ☐ ✕] │
├──────────────┬──────────────────────────────────────────────┬─────────────┤
│ [Search ⌃K][+]│  main surface (radius 12, inset 8)            │ right panel │
│ Home         │                                              │ 320, either │
│ Calendar     │                                              │ tax profile │
│ Filings      │                                              │ or          │
│ Recent       │                                              │ notifications│
│  2550Q Q3 …  │                                              │             │
│              │                                              │             │
│ Settings     │                                              │             │
│ (JD) Juan …⇅ │                                              │             │
└──────────────┴──────────────────────────────────────────────┴─────────────┘
* [🔍][+] in the title bar show only while the sidebar is hidden.
```

- **Title bar, left side:** macOS traffic lights, the sidebar toggle, back
  and forward, then search and new-return. Search and new-return appear only
  while the sidebar is hidden. Icon buttons are 4 px apart, with no
  separators.
- **Title bar, center:** the context pill (taxpayer avatar, name, full TIN
  with branch code). It replaces the window title. Clicking it toggles the
  tax-profile panel. The old "eBIRForms" sidebar title and the chevron-left
  collapse button are removed.
- **Title bar, right side:** notifications (with a 6 px accent dot when
  something is unread), the theme toggle, and on Windows the caption
  buttons. The close button hovers to `#c42b1c` (the system value; this is
  the only allowed literal color).
- **Left sidebar:** a search field and a `+` (new return) at the top, then
  Home, Calendar, Filings and a "Recent" list. At the bottom are Settings
  and the app account row (avatar, name, email, up-down chevron). The
  account row opens a menu with Lock app, Account settings and Log out. The
  app account is separate from tax profiles. The Taxpayers list is removed
  from the sidebar and lives in the tax-profile panel.
- **Right panel, tax profile:** avatar 56, name, TIN, and a pencil button
  that edits name, branch code and location in place (branch code must be 5
  digits; head office `00000` cannot change). Then come the facts (branch,
  location, RDO) and three groups: **Open** (Profile, Forms, Templates,
  which open in the main area), **Branches** (from D1) and **Switch
  taxpayer**, plus New taxpayer.
- **Right panel, notifications:** a header with "Mark all read" and the
  list. No close button.
- **Main area for a taxpayer:** a page header (avatar 40, name, TIN · branch
  · type, with Copy TIN and New return buttons) and tabs for Profile,
  Forms and Templates. These are the tax-profile spec's Details, Forms and
  Templates tabs.
- **Below 860 px** the sidebar and the panel become overlays. **Below
  600 px** the pill shows only the avatar and branch code, and back and
  forward are hidden.

## Disclosure (replaces the tax-profile collapsible)

- All sections share **one** bordered group (radius 12), divided by
  hairlines. Sections do not get their own card, shadow or colored header
  band.
- Header: 44 px tall. A 16 px `ChevronRight` rotates 90° when open, then the
  title (13/600), a meta line (12, fg-3, for example "2 of 4 from head
  office"), and a trailing ghost **Edit** button. Edit shows only while the
  section is open.
- Body padding is 4 / 20 / 20 / 36, so the content lines up with the title
  text. Fields sit in a two-column grid with 16 × 32 gaps, and one column
  below 640 px.
- Edit mode replaces values with inputs in place. Cancel (ghost) and
  "Save changes" (primary) sit at the bottom right of the section.
- Inheritance (D2): an inherited value is shown in fg-2 with a "Head office"
  chip. In edit mode the chip becomes a "Same as head office" switch, and
  the input is disabled while the switch is on.
- The sections are Taxpayer (shared by every branch), Branch, Address and
  contact (inheritable), and Email, security and export (D12, set once per
  taxpayer).

## Form page (the on-screen return, all 43 forms)

The screen form and the printed form are two different things. The
`html-frozen/` sheets are pixel-placed copies of the BIR paper and stay the
print and preview output. Do not restyle them, and do not apply anything in
this section to them. The screen form is drawn by **one renderer** from data,
so every form gets the same parts, themes and responsive behaviour.

- **Data:** `docs/ui-redesign/forms_extract.py <repo> <out.json>` builds
  `forms-schema.json` (43 forms, 9,185 visible fields). It reads only from:
  - `rules/forms/*/fields.json` for fields, control kinds, value types,
    required and computed flags, and choices;
  - the `html-frozen/*/index.html` text layer for printed item labels and
    Part and Schedule headings;
  - `crates/bir-core/src/forms/registry.rs` for titles and filing frequency.

  It writes nothing into the repo tree.
- **Layout:** the page header shows the BIR form code and revision, the
  title, and chips for frequency, page count and field count. A context bar
  shows the taxpayer, TIN and branch, the period, and a Guided mode switch.
  Below that are a Part navigator (sticky, 208 px; it becomes a horizontal
  chip row below 760 px) and one collapsible card per Part.
- **Item row:** the item number in a mono chip, the printed label (13/500),
  a red `*` when any field is required, then the controls in a wrapping row.
  An item where every field is computed gets the `bg` fill and a "Computed"
  chip.
- **Controls:**
  - Amounts: right-aligned, tabular figures, `₱` prefix, formatted on blur.
  - Percentages: `%` suffix.
  - Choices: pill radio groups.
  - Dropdowns: the native select.
  - TIN: four locked mono boxes (3-3-3-5).
  - Repeated schedule rows: one table with a row-number column, scrolling
    sideways inside its own box.
- **Identity fields** (TIN, RDO, name, address, ZIP, phone, email) are locked
  and filled from the tax profile, with a "From tax profile" chip (D18).
  Computed fields are locked.
- **Draft layout:** when under 80 % of a form's fields sit under a numbered
  item or table, the form shows a warning chip, and the leftovers go in a
  collapsed "N more fields not yet placed on the paper layout" block. This
  happens on 2550Q, 2551Q, 1701A, 1701, 2200S, 1700, 1701MS and 2200M today.
  Fix the source data rather than hiding the chip.
- **Revision mismatch:** where a field's own label in the rules corpus
  disagrees with the frozen paper (1601EQ Part II: the paper is the 2019
  revision, the rules describe the 2018 runtime), the renderer shows the
  rules-corpus label. It never edits either source.

## Copy

- Buttons say what happens: "Open form", "Save changes", "Use as template".
  Never use "OK" or "Submit".
- Errors say what to type: "Branch code is 5 digits, like 00001."
- Use sentence case everywhere. Do not use uppercase group labels, except
  the small group headings inside the command palette.

## Porting checklist (one screen at a time)

1. Replace every `Icon::size(..)` with the wrapper's fixed size.
2. Replace `.small()`, `.xsmall()` and `.large()` on buttons with
   `AppButton` / `IconButton`.
3. Replace ad-hoc `px(..)` gaps with the 4 px scale.
4. Remove separators and dividers from chrome and panels.
5. Remove literal colors and route them through tokens.
6. Check the screen in light **and** dark, on Windows **and** macOS, at
   full width and at 800 px wide.
