## 2026-07-01 — chargeCard() undercharges on fractional cents
- What changed / what shortcut was taken: `applyDiscount()` in `src/payment.js:6` uses
  `Math.floor` instead of rounding, so `chargeCard()` silently undercharges by up to $0.01.
- Ceiling (when this breaks): any amount with a fractional cent component.
- Upgrade trigger: switch to `Math.round` once finance signs off on the rounding policy change.
- Status: open
