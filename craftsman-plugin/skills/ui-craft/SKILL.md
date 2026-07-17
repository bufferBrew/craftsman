---
name: ui-craft
description: Use before writing or changing any UI — screens, components, styling, layout, theming — in any framework (Compose, Flutter, React, SwiftUI, web). Framework-adaptive modern-UI craft — design-token discipline, accessibility, responsive layout, state-driven UI, motion restraint.
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

### Responsive and adaptive layout
- No hardcoded screen dimensions.
- Use the framework's adaptive primitive: `WindowSizeClass` (Compose), `LayoutBuilder`/
  `MediaQuery` (Flutter), CSS grid/flexbox with breakpoints (web), size classes (SwiftUI).

### State-driven UI
- UI is a function of state: hoist state out of the view, pass data down and events up.
- Model loading, empty, and error states explicitly — a screen that only renders the happy path
  is unfinished.
- No imperative view mutation in a declarative framework.

### Motion restraint
- Animation serves orientation (where did this come from, where did it go) — never decoration
  for its own sake.
- Keep durations short and respect the platform's reduced-motion setting.

## Never mix framework idioms

One project, one framework's patterns. Do not port a React habit into Compose or a Compose habit
into Flutter — detect what the project uses and write idiomatic code for that framework only.
