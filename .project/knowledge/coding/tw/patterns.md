# Layout and UI Patterns

Features in this file exist as native utilities in v4 with no plugin — if you're reaching for a
plugin or hand-written CSS for one of these, check here first.

- **Container queries.** Built into core (no `@tailwindcss/container-queries` plugin needed). Mark
  the parent `@container`, condition children on `@sm:`…`@7xl:`. `@container` only tracks
  inline-size; use `@container-size` (v4.3) for a size container that also tracks block-size,
  unlocking `cqb`/`cqh` arbitrary-value units (`h-[50cqb]`). Full variant syntax — ranges, named
  containers, custom sizes via `@theme { --container-* }` — in `variants-and-states.md`.
- **3D transforms.** Opt an element's children into 3D space with `transform-3d`
  (`transform-style: preserve-3d`; `transform-flat` is the explicit 2D default). Then compose
  `rotate-x-*`/`rotate-y-*`/`rotate-z-*`, `scale-z-*`, and `translate-z-*` (and their negative
  forms, `-rotate-x-*` etc.) on the children — without `transform-3d` on the parent, these still
  apply but collapse to a flat 2D result.
- **Layered shadows and rings.** `inset-shadow-*` and `inset-ring-*` are separate CSS-variable
  slots from `shadow-*`/`ring-*`, so an element can carry an outer shadow, an outer ring, an inset
  shadow, and an inset ring simultaneously without one clobbering another — compose them directly
  on the same element: `shadow-md ring-1 ring-black/5 inset-shadow-xs`.
- **`text-shadow-*`.** Sizes `2xs xs sm md lg` plus `none`. Colored via
  `text-shadow-{color}-{shade}` and opacity via a slash modifier on the size:
  `text-shadow-lg/30`, or combine both: `text-shadow-2xs text-shadow-sky-300/50`.
- **Masking.** Full `mask-*` family — `mask-image`, `mask-clip`, `mask-composite`, `mask-mode`,
  `mask-origin`, `mask-position`, `mask-repeat`, `mask-size`, `mask-type` — for CSS masking without
  reaching for SVG `<clipPath>` or a background-image hack.
- **New standalone CSS properties as utilities:** `field-sizing-content` (auto-growing `<textarea>`
  that tracks its content — `field-sizing-fixed` is the explicit opt-out), `scheme-light` /
  `scheme-dark` (sets `color-scheme`, so native form controls and scrollbars match the page theme
  without a `dark:` override on every one of them), `zoom-*` (v4.3 — CSS `zoom`, e.g. `zoom-75`,
  arbitrary `zoom-[1.1]`, variable `zoom-(--preview-zoom)`), `tab-*` (v4.3 — CSS `tab-size` for
  `<pre>` content, `tab-2`…`tab-8`, arbitrary/variable forms same as `zoom-*`).
- **Logical properties.** The expanded set — `ps-*`/`pe-*` (inline start/end padding),
  `ms-*`/`me-*` (margin), `border-s-*`/`border-e-*`, plus block-axis forms `pbs-*`/`pbe-*` for full
  bidirectional (`rtl:`-safe) layouts without a single `ltr:`/`rtl:` pair anywhere in the markup.
- **Scrollbars (v4.3).** `scrollbar-thin` / `scrollbar-none` / `scrollbar-auto` (width),
  `scrollbar-thumb-*` / `scrollbar-track-*` (color, opacity-modifier-aware:
  `scrollbar-thumb-slate-900/60`), `scrollbar-gutter-stable` (reserve scrollbar space up front to
  stop layout shift when content grows past the viewport — prefer this over a manual
  `overflow-y: scroll`). All native `scrollbar-width`/`scrollbar-color`/`scrollbar-gutter`, no
  `::-webkit-scrollbar` hackery required.
