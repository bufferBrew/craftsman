---
name: ui-craft
description: Use before writing or changing any UI — screens, components, styling, layout, theming, transitions — in any framework (Compose, Flutter, React, SwiftUI, web), and when asked to modernize or speed up an existing UI. Framework-adaptive modern-UI craft — design-token discipline, target awareness (desktop web, mobile web, native app), accessibility, keyboard operability and interaction states, responsive layout, text scaling, state-driven UI, purposeful motion and transitions, rendering and startup performance.
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

Never hardcode a color, spacing, font size, radius, duration, or easing curve that a token
already defines. If no design system exists at all, **ask** (or suggest generating one with a
design-intelligence skill) rather than inventing ad-hoc styles — the `smallest-change-first`
ladder applies to visual decisions too.

In a multi-app workspace, check for a shared UI package before the app's own theme. A token that
several apps need (a motion scale, a page transition) belongs in the shared package, so every
app inherits it. Copying it into each app is how the apps drift apart.

## Know the target, not only the framework

The framework says which primitives to write. The target says what the user holds in their
hand, and one codebase often ships to several. A Flutter or React app can run as a desktop web
page, a mobile web page and a native app at once, and each one fails differently. Find the
targets before writing: platform folders (`android/`, `web/`, `ios/`), deploy config, and the
project's `CLAUDE.md`. If the request doesn't say which target matters, check all the project
ships to.

| Target | What it adds to the checklist |
|---|---|
| **Desktop web** (PC/Mac browser) | Pointer and keyboard are primary: hover states, visible focus, keyboard shortcuts for frequent actions, scroll wheel and trackpad. Wide windows: cap the reading measure, use the extra width for a rail or second pane, never stretch a phone layout. Browser back/forward and deep links must work. |
| **Mobile web** (Android/iOS browser) | Touch only: nothing may depend on hover (`@media (hover: hover)` gates hover styles on web). The browser's own bars resize the viewport, so size full-height layouts with `dvh`, not `100vh`. The soft keyboard covers the bottom of the page: keep the focused field and the submit action visible. Respect safe-area insets. Browser back must close an open sheet or dialog before leaving the page. Phones have a fraction of a laptop's GPU and CPU: blur, large shadows and long lists cost far more here. |
| **Native Android app** | System back, including the predictive back gesture, must work on every screen and overlay. Draw edge to edge and pad for system bars and the IME with window insets. Use ripple and haptic feedback from the platform, and Material 3 components. Text and display size settings apply. |
| **Native iOS app** | Edge-swipe back, safe areas, Dynamic Type, and the platform's sheet and navigation behavior. |

A fix verified on one target is unverified on the others. Say which targets you checked.

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

### Motion and transitions

Motion is how a UI explains a change: where a screen came from, what a tap did, which item
moved. A UI with no motion feels abrupt and dated, and one with decorative motion feels slow.
Every animation must answer one of three questions for the user: *where did this come from*,
*did my input register*, or *what just changed*. If it answers none, remove it.

**Motion values are tokens.** Durations, curves and springs come from a named scale in the theme
layer, exactly like colors. If the project has none, add a small one (three or four durations,
enter/exit/standard curves, one or two springs) before writing the first animation. A literal
`300` in a widget is the same defect as a literal hex color.

**Timing.**
- Press, toggle, hover and other direct feedback: 100–150ms. Feedback must start within one
  frame of the input, before any network call returns.
- Elements entering, leaving or changing state: 200–300ms.
- Full-screen and route transitions: 300–400ms, with 500ms as the ceiling. Desktop transitions
  run shorter than mobile ones, because the travelled distance is a smaller share of the view.
- Exits are shorter than entrances. The user has already decided to leave.
- Entering elements decelerate (ease-out), leaving ones accelerate (ease-in), and two-way moves
  use ease-in-out. Linear easing is for progress and opacity only.
- Use springs for things that move or scale, because a spring can be interrupted and redirected
  mid-flight. Keep eased tweens for opacity and color.
- Stagger list entrances by 30–60ms per item and cap the total, so a long list does not crawl in.

**Pick the transition from the navigation relationship.** The relationship decides the pattern,
never taste:

| Relationship | Transition | Primitive |
|---|---|---|
| Peers (tabs, bottom-nav destinations) | Fade-through or a short cross-fade. No slide: peers have no direction. | `PageTransitionsTheme` / `AnimatedSwitcher` (Flutter), `AnimatedContent` (Compose), View Transitions API (web) |
| Parent → child (list → detail) | Shared element: the tapped item grows into the detail screen. Fall back to a forward slide. | `Hero` (Flutter), `SharedTransitionLayout` (Compose), `view-transition-name` (web), `matchedGeometryEffect` (SwiftUI) |
| Step forward/back (wizard, onboarding) | Shared-axis slide in the direction of travel, reversed on back. | Route transitions on the navigator: go_router `CustomTransitionPage`, Navigation Compose `enterTransition`/`exitTransition` |
| Overlay (sheet, dialog, menu) | Grows from its trigger or rises from the edge it is anchored to, over a fading scrim. Dismisses back toward where it came from. | The framework's own sheet and dialog components |
| In-place change (expand, reorder, add, remove) | Animate size and position, so neighbours slide and never jump. | `AnimatedSize`/`AnimatedList` (Flutter), `animateContentSize`/`Modifier.animateItem` (Compose), FLIP or View Transitions (web) |

Set route transitions once, in the theme or router, so every screen gets them. A screen that
navigates by launching a new Activity or doing a full page load gets no shared transition at
all, so prefer in-app navigation where the project's structure allows it.

**Animate cheap properties only.** Transform (translate, scale, rotate) and opacity run on the
compositor. Width, height, padding, top/left, shadows and blur radius re-run layout or paint on
every frame and drop frames on a phone. Express a size change as a scale or a clip where
possible. In Compose, read animated values inside `graphicsLayer { }` or a draw lambda so the
frame skips recomposition. In Flutter, rebuild only the animated subtree (`AnimatedBuilder` with
a `child`), and keep `Opacity` and `BackdropFilter` off large subtrees.

**Animations must be interruptible.** A user who taps back mid-transition gets the reverse from
the current position, never a queue of animations playing out. Never block input while
something animates.

**Reduced motion is a requirement.** Read the setting through the framework:
`MediaQuery.disableAnimationsOf` (Flutter), `prefers-reduced-motion` (web),
`accessibilityReduceMotion` (SwiftUI). Compose scales its animation APIs by the system animator
setting on its own, so the defect there is hand-rolled timing (`delay()` loops, manual frame
clocks) that bypasses it. Under reduced motion, replace movement with a short cross-fade or an
instant change, and stop decorative loops entirely. Do not remove the state change itself. Put
the check in the motion tokens (one helper that returns a zero duration), so no call site can
forget it.

### Performance is part of the design

A slow UI is a broken UI, however good it looks in a screenshot. These are the defects that
make an app feel heavy, in the order they usually matter.

**Respond before the work finishes.**
- Acknowledge every input within 100ms: pressed state, ripple, or the destination's skeleton.
- Update the UI optimistically for actions that almost always succeed (toggle, like, reorder,
  rename), and roll back with a message on failure. A spinner on a checkbox is a design defect.
- Show cached or previous data at once and refresh behind it, with no blank screen between.
- Debounce type-ahead queries. Never debounce the keystroke echo itself.

**Keep frames cheap.**
- Any list that can grow is built lazily: `ListView.builder`/slivers (Flutter),
  `LazyColumn` with stable `key`s (Compose), virtualization or `content-visibility: auto` (web).
  A plain `ListView(children: …)` or `Column` in a scroll view builds every row up front.
- Give list items stable keys, so an insert or reorder moves rows without rebuilding them.
- Decode images at display size (`cacheWidth` in Flutter, `srcset`/`sizes` or the framework's
  image component on web, a sized request in Coil) and reserve their space so nothing shifts
  when they land.
- Keep state reads narrow: a change to one field should rebuild one widget, not the screen.
  Use `const` constructors (Flutter), stable parameters and `derivedStateOf` (Compose),
  memoized selectors (React).
- Blur, large soft shadows and stacked translucent layers are the most expensive paint
  operations. Use them on small surfaces, and provide a flat fallback for mobile web.

**Start fast.**
- **Web (React/Next.js, plain):** ship less JavaScript. Render on the server where the framework
  supports it, split by route, lazy-load below-the-fold and rarely used UI, preload the font and
  the hero image. Targets: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1, measured on a throttled mobile
  profile.
- **Flutter web:** build with `--wasm` when every dependency supports it (it falls back to
  CanvasKit in browsers without WasmGC). Split rarely visited features with deferred imports
  (`import … deferred as`). Show a styled HTML splash in `index.html`, so the user sees the
  brand while the engine loads. Flutter web's first load is its weakest point on a phone, so
  measure it there.
- **Android (Compose or Flutter):** judge performance in a release build, never a debug one.
  Ship a Baseline Profile for startup and the main scroll path in Compose apps. Keep work out of
  `Application.onCreate` and the first frame, and use the platform splash screen API so there is
  no blank window.

**Measure, do not guess.** Use the tool the stack provides: a Lighthouse run and a performance
trace for web (including Flutter web), Flutter DevTools' frame chart or `--profile` mode,
Android Studio's profiler or Macrobenchmark. A performance claim with no measurement goes under
"not verified".

## Modernizing an existing UI

"Make it modern", "make it feel fast" and "add nice transitions" are audit tasks before they
are coding tasks. Restyling screen by screen from taste produces an app with five different
ideas of modern.

1. **Audit first, with counts.** Search the codebase for the signals this skill names: motion
   tokens or literal durations, route-transition configuration, reduced-motion checks, lazy
   versus eager lists, skeletons versus bare spinners, tap handlers on plain containers,
   viewport-based breakpoints, web build flags. Report what you found per target.
2. **Fix the foundations before the screens.** Motion tokens, the route transition and the
   reduced-motion helper go into the theme layer or shared package once. Most screens then
   improve without being touched.
3. **Then the highest-traffic flows.** Launch, the home screen, the main list → detail path.
   Apply the transition table and the performance list there first.
4. **Propose before restyling.** Changing colors, type or layout density is a design decision
   that belongs to the user. Present the audit and the proposed order, and get agreement on
   anything that changes how the app looks. Motion and performance foundations that leave the
   static appearance unchanged are safe to propose as the first step.

"Modern" here means current platform conventions (Material 3 on Android, the platform's own
navigation and back behavior, system light/dark, adaptive layouts, fluid interruptible motion,
skeleton loading) applied consistently. It does not mean a trend the design system never asked
for, such as glass effects, gradients everywhere, or parallax.

## Verify on a rendered surface

A passing build proves the UI compiles. Motion, hover and focus appearance, layout at real
widths, and speed only exist when it runs. When a browser automation or device tool is
available (for example a Chrome DevTools MCP server), use it for any web target, Flutter web
included:

- Load the page at a desktop width and again under mobile emulation with CPU throttling.
- Take a screenshot at each, and check hover, focus and pressed states on what you changed.
- Run a Lighthouse audit or a performance trace when the change touches loading or animation.
- Read the console for errors and layout overflow warnings.

For native targets, use an emulator or device tool if the session has one. Whatever you could
not run, list as unverified. Never report a transition as smooth, or a screen as fast, from
reading the code.

## Never mix framework idioms

One project, one framework's patterns. Do not port a React habit into Compose or a Compose habit
into Flutter — detect what the project uses and write idiomatic code for that framework only.
