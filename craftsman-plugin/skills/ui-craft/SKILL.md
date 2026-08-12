---
name: ui-craft
description: Use before writing or changing any UI — screens, components, styling, layout, theming — in any framework (Compose, Flutter, React, SwiftUI, web). Framework-adaptive modern-UI craft — design-token discipline, accessibility, keyboard operability and interaction states, responsive layout, text scaling, state-driven UI, motion restraint.
---

# UI Craft

## Overview

UI code is judged by users, not compilers. A build that passes says nothing about contrast,
touch targets, or how a screen behaves on a narrow window. These rules hold across frameworks —
what changes per framework is only the primitive used to satisfy them.

**Core principle:** the design system decides; the code obeys.

## Design system first

Before writing any UI, locate the project's token source. Check in this priority order and use
the first one that exists:

1. **`design-system/MASTER.md`** (plus any page-specific override files) — produced by
   design-intelligence skills such as ui-ux-pro-max. If present, it is the authoritative
   specification: colors, typography, spacing, and anti-patterns come from it, not from taste.
2. **The framework's theme layer** — Compose `MaterialTheme`/`Theme.kt`, Flutter `ThemeData`,
   Tailwind config, CSS custom properties, SwiftUI environment values.
3. **Existing component conventions** — how the project's current screens and components already
   do it. Reuse those components before writing new ones.

Never hardcode a color, spacing, font size, or radius that a token already defines. If no design
system exists at all, **ask** (or suggest generating one with a design-intelligence skill) rather
than inventing ad-hoc styles — the `smallest-change-first` ladder applies to visual decisions too.

## The craft checklist

Apply to every surface you touch. Framework primitives are named where they differ.

### Spacing, typography, color
- Stick to a consistent spacing scale (typically 4/8pt multiples) — no arbitrary one-off values.
- Type sizes come from the theme's type ramp, not inline numbers.
- No one-off hex values — every color resolves to a token.

### Accessibility
- Body-text contrast ≥ 4.5:1 against its background.
- Touch/click targets ≥ 48dp (Android) / 44pt (iOS) / 24px (CSS, WCAG 2.2).
- Every interactive or informative element has a semantic label: `contentDescription` (Compose),
  `Semantics` (Flutter), `aria-*` (web), `accessibilityLabel` (SwiftUI).
- Keyboard/focus order follows visual order.
- Never convey state by color alone — pair it with text, an icon, or a shape change.

### Every control is keyboard-operable

Focus *order* is the easy half. The half that actually breaks is whether a control is a control
at all. A tap handler bolted onto a plain container — `GestureDetector` (Flutter),
`Modifier.pointerInput` (Compose), `onClick` on a `<div>` (web) — behaves correctly under a
mouse and is **completely invisible to keyboard traversal**: Tab never lands on it, Enter never
fires it. Ship that pattern in your shared button component and the whole app becomes unusable
without a pointer. It is a WCAG 2.1.1 failure, and no amount of visual review catches it,
because it looks perfect in a screenshot.

For every interactive element, verify all four:

1. **Reachable** — Tab lands on it. Use the framework's focusable primitive:
   `FocusableActionDetector`/`InkWell` (Flutter), `Modifier.clickable` or a real `Button`
   (Compose), a real `<button>`/`<a>` (web), `Button` (SwiftUI).
2. **Operable** — Enter and Space activate it, firing the same callback a tap does.
3. **Visibly focused** — a focus indicator appears, and it is *not* the same treatment as hover.
   Draw it as an overlay at a small outset so toggling it cannot reflow the control, and pick a
   color that stays visible on a filled accent surface — a brand-colored ring on a
   brand-colored button is invisible.
4. **Correctly excluded when disabled** — a disabled control is skipped by traversal entirely,
   not merely dimmed.

Prefer the framework's native control. Hand-roll only when the design genuinely cannot be
expressed through it, and then owe all four properties explicitly. Assert this in a test: focus
and activation are behavioral properties, so a widget/DOM test that sends Tab then Enter is the
only thing that keeps them from silently regressing.

### The four interaction states are one set

`hover`, `focus`, `pressed`, `disabled`. Any interactive component that defines one owes all
four. Hover and focus are distinct states with distinct triggers — a control focused by a click
should not paint a focus ring, and a hover treatment is not a substitute for a focus one.

Hover is not optional on web/desktop targets: a cursor change alone is not feedback. Transparent
variants (ghost/text buttons) have no fill to darken, so they need their own hover treatment
rather than inheriting the filled variant's.

### Responsive and adaptive layout
- No hardcoded screen dimensions.
- Use the framework's adaptive primitive: `WindowSizeClass` (Compose), `LayoutBuilder`/
  `MediaQuery` (Flutter), CSS grid/flexbox with breakpoints (web), size classes (SwiftUI).

**Measure the slot, not the window.** Breakpoint logic must be fed the width of the container
the component actually occupies, never the viewport's. The two diverge as soon as anything caps
the content measure, adds a rail, or opens a split pane — a 1440px window whose content column
is capped at 1080 picks the wrong column count if it asks the viewport. Mixing the two is worse
than either alone: sizing cells from the local constraint while counting columns from the
viewport is exactly what produces overflow and dead columns. In Flutter that means
`LayoutBuilder`'s `constraints.maxWidth`, not `MediaQuery.sizeOf`; on web, container queries or
the element's own width, not `window.innerWidth`.

**Fixed extents and scaled text do not mix.** Users enlarge text independently of layout —
Android's font-size slider, iOS Dynamic Type, browser text zoom — commonly to 1.5–2×. Any
hardcoded height, grid row extent, or aspect ratio wrapping text overflows there. Either let the
container size to its content, or grow the extent by the text scale factor
(`MediaQuery.textScalerOf` in Flutter, `rem`/`em` on web). Check at 200%: it is a real setting,
not a theoretical one.

### State-driven UI
- UI is a function of state: hoist state out of the view, pass data down and events up.
- Model loading, empty, and error states explicitly — a screen that only renders the happy path
  is unfinished.
- No imperative view mutation in a declarative framework.
- **Distinguish offline from server failure.** "Check your connection" is the wrong advice for a
  request the server rejected, and sends the user off to debug their wifi instead of the actual
  problem. Classify the error and change the glyph, headline and advice accordingly. Be
  conservative: only transport-level failures (socket, DNS, timeout, failed fetch) are offline;
  an auth or permission rejection arrived over a working connection. An unreachable server is
  also a *warning*, not an error — nothing is broken and nothing was lost — so painting it in the
  same red as a real failure just trains people to ignore red.
- Prefer a shape-matched skeleton over a bare spinner when the incoming layout is known, and give
  the skeleton the same extents the real content will take, so landing data does not jolt the
  page.

### Motion restraint
- Animation serves orientation (where did this come from, where did it go) — never decoration
  for its own sake.
- Keep durations short and respect the platform's reduced-motion setting.

## Never mix framework idioms

One project, one framework's patterns. Do not port a React habit into Compose or a Compose habit
into Flutter — detect what the project uses and write idiomatic code for that framework only.
