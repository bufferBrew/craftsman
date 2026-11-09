---
name: ui-craft
description: Use when building, changing, or reviewing UI. Guides visual direction, design-system reuse, accessibility, responsive layout, interaction states, and UI performance for the project's framework.
---

# UI Craft

## Match the work to the request

- **Targeted fix or polish.** Match the surrounding UI and verify the behavior the change touches.
- **New surface or redesign.** Establish a visual direction before implementation, then review the rendered result against it.
- **Review.** Inspect the requested surface and its shared components. Report findings with the affected user interaction, severity, and file and line where available. Separate issues reproduced in the running UI from findings based on code inspection.

## Start with the design system

Read the brief and any supplied references. Check `design-system/MASTER.md` and page overrides for
design intent, the active theme for token values, and nearby components for implementation patterns.
Reuse existing controls and tokens for type, color, spacing, and shape. If sources conflict,
resolve the choice using the brief and current product conventions.

For a new surface, start with the audience, primary task, and real content. Choose a focal point
and make the typography, density, palette, and composition support it. Use structural devices such
as cards, dividers, and numbering where they clarify the content. Before building, check whether
the same treatment would fit an unrelated product unchanged. If so, use the subject matter or the
product's interaction to make the design more specific. Follow the brief when it specifies a look.

For greenfield work without a theme, define the few reusable tokens the surface needs in the
framework's existing styling layer. For an existing product without formal tokens, use nearby
conventions. For new visual directions and substantial redesigns, use the installed
`frontend-design` skill if available. See [Anthropic's Frontend Design guide](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md).

## Build for the platform

### Semantics and interaction

- Start with native controls or the project's accessible primitives. Use a button for actions
  and a link for navigation on the web. Preserve accessible names, roles, values, and states.
  Label inputs and icon-only controls. Expose meaningful imagery and hide purely decorative
  elements from assistive technology.
- On platforms with keyboard navigation, check reachability, logical focus order, visible focus,
  and activation with the keys appropriate to each control. On the web, buttons support Enter
  and Space, links use Enter, and composite widgets may use arrow keys. Check dialog focus
  entry and restoration when applicable. Use [WAI-ARIA patterns](https://www.w3.org/WAI/ARIA/apg/patterns/)
  for custom web widgets.
- Keep hover, keyboard focus, pressed, and disabled states distinguishable where the input
  supports them. Check hover feedback beyond the cursor on ghost and filled variants.
  Make the focus indicator visible against adjacent colors without changing layout, and
  check that sticky UI does not obscure it.
  Use native disabled behavior by default. If a disabled control intentionally remains
  focusable, expose its state and suppress activation.
- Check text and control contrast. Aim for at least 4.5:1 for body text and pair color
  cues with text, icons, or shape. Aim for touch targets of at least 48 dp on Android and
  44 pt on iOS. On the web, check the
  [WCAG 2.2 target size criterion](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html),
  including its spacing and other exceptions. Prefer larger targets for primary touch controls.

### Layout, state, and motion

- Size reusable layouts from their container. A wide window can still contain a narrow panel
  or split view. Use local constraints such as Flutter's `LayoutBuilder`, Compose's
  `BoxWithConstraints`, or CSS container queries. Use viewport breakpoints for page-level changes.
- Let text-bearing containers grow and wrap. Check narrow widths, long labels, and 200% zoom
  or the platform's larger text settings. Fixed row heights and aspect ratios around text
  deserve particular scrutiny.
- Keep a single source of truth for UI state. Cover loading, empty, error, and success
  states where they occur. If the layout is known, use a shape-matched skeleton or reserve
  space for content to limit layout shifts. Separate transport problems from server responses.
  Use offline copy when connectivity is known to
  be unavailable, and give actionable recovery guidance for validation or permission errors.
- Use motion to clarify what changed and respect the platform's reduced-motion setting.
  Keep essential feedback available with motion reduced. Prefer the framework's established
  animation primitives and keep interactions responsive during transitions.

## Use specialist guidance selectively

Prefer the matching installed skill when available. Otherwise consult the linked upstream guide
for the relevant topic. The core workflow above works independently of these references.

- **Web UI or accessibility review.** Use [Vercel's Web Design Guidelines skill](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md)
  for scoped reviews. In the affected UI, check semantics, keyboard flow, form labels and
  recovery, zoom and overflow, reduced motion, and loading feedback as applicable. Consult the
  current checklist for a full review. Report actual findings with file and line references.
- **React DOM or Next.js performance.** Use [Vercel's React Best Practices](https://github.com/vercel-labs/agent-skills/blob/main/skills/react-best-practices/SKILL.md)
  when work affects data fetching, bundles, rendering, or client/server boundaries. Start
  by looking for serial waits on independent data and unnecessary client code. Check render churn
  where the affected interaction warrants it. Use Next.js-specific rules only for the
  router and version in use.
- **React Native or Expo performance.** Use [Vercel's React Native skill](https://github.com/vercel-labs/agent-skills/blob/main/skills/react-native-skills/SKILL.md)
  for native targets. Focus on the affected behavior, such as list virtualization, row cost,
  scroll and animation responsiveness, image sizing, or safe-area handling. Start with
  the project's existing libraries and profile performance on a representative device when possible.

## Verify the result

Run the project's relevant checks. When a preview is available, open the changed screen in a
browser, simulator, or device and exercise the affected flow. Check representative narrow and wide
layouts, the applicable input modes, and alternate states. For visual work, inspect the rendered
hierarchy and spacing. For shared controls, use an existing interaction test or add focused coverage
when a keyboard or focus regression would otherwise go undetected. For performance work, compare
the relevant trace or measurement before and after when available. Report which checks ran and
which required a runtime or device you could not access.
