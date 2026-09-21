# Tailwind CSS v4 Guide — use when writing utility classes or Tailwind-aware CSS

> Current to **Tailwind CSS v4.3** (v4.2 added the `mauve`/`olive`/`mist`/`taupe` color
> palettes; v4.3 added scrollbar utilities, `@container-size`, `zoom-*`, `tab-*`). General-purpose
> reference + style guide — project-independent. Requires **Chrome 111+, Safari 16.4+, Firefox
> 128+** (v4 depends on native cascade layers, `@property`, and `color-mix()`); there is no IE/old-
> Safari fallback path.

## Files

| File | Read when |
|---|---|
| `modern-syntax.md` | Always at least once — CSS-first config: `@theme`, `@utility`, `@custom-variant`, `@reference`, `@plugin`, the `--spacing()`/`--alpha()` functions, theme namespaces |
| `variants-and-states.md` | Choosing a state/condition selector — full pseudo-class, pseudo-element, media-query, attribute, and `group`/`peer`/`has`/custom-variant reference |
| `patterns.md` | Layout/UI work — container queries, 3D transforms, logical properties, scrollbars, masks, shadows unique to v4 |
| `best-practices.md` | Dark mode strategy, `@apply`/`@reference` in framework SFCs (Vue/Svelte/CSS Modules), safelisting, `@utility` vs `@layer components` |
| `pitfalls.md` | Reviewing or writing any class touching a v3→v4 rename — the classic AI-hallucinates-v3-syntax traps |
| `tooling-and-migration.md` | Install/build setup (Vite/PostCSS/CLI), source detection (`@source`), the `npx @tailwindcss/upgrade` path, `@config`/`@plugin` compatibility |

## The five rules that outrank everything

1. **CSS-first, no config file.** Do not create or edit `tailwind.config.js` unless a project
   explicitly still needs one for incremental migration (`tooling-and-migration.md`'s `@config`
   escape hatch). All configuration — theme tokens, breakpoints, custom utilities, custom variants
   — lives in CSS via `@theme`, `@utility`, `@custom-variant` (`modern-syntax.md`).
2. **Never construct class strings dynamically.** Tailwind scans source files as plain text, not
   as code — `` `bg-${color}-500` `` and `` `text-{{color}}-600` `` produce nothing. Map props to
   complete, statically-written class strings; safelist anything else with `@source inline()`
   (`tooling-and-migration.md`).
3. **Check `pitfalls.md` before writing any utility that might be a v3 holdover** — `outline-none`
   → `outline-hidden`, the `shadow`/`blur`/`rounded`/`drop-shadow` `-sm`→`-xs` scale shift, bare
   `ring` → `ring-3`, `bg-opacity-50` → `bg-black/50`. This is the single biggest source of
   hallucinated Tailwind code from any model, including this one.
4. **New composable utility → `@utility`. Reusable component class → `@layer components` is still
   correct.** `@utility` is for classes that need variant support (`hover:`, `md:`, …) or parsed
   values (`--value()`/`--modifier()`); a plain `.card`/`.btn` class with no variant composition
   still belongs in `@layer components` — v4 did not deprecate it (`best-practices.md`).
5. **The important modifier is a suffix now:** `bg-red-500!`, not `!bg-red-500`. Stacked variants
   apply strictly **left-to-right** (`*:first:pt-0`, not `first:*:pt-0`).
