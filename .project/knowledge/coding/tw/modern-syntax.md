# Modern Tailwind v4 Syntax

Tailwind v4 is CSS-first: there is no `tailwind.config.js` by default. Every directive below runs
inside the CSS file that does `@import "tailwindcss";` — usually the app's entry stylesheet.

## `@theme` — design tokens that generate utilities

A theme variable is a CSS custom property in a recognized namespace. Defining one both stores the
value **and** tells Tailwind to generate the matching utility class — this is the difference from
a plain `:root { --x: ... }` variable, which only stores a value.

```css
@import "tailwindcss";

@theme {
  --color-mint-500: oklch(0.72 0.11 178);   /* → bg-mint-500, text-mint-500, fill-mint-500, ... */
  --breakpoint-3xl: 120rem;                  /* → 3xl: variant */
  --font-display: "Satoshi", "sans-serif";   /* → font-display */
  --ease-fluid: cubic-bezier(0.3, 0, 0, 1);  /* → ease-fluid */
}
```

**Namespaces → what they generate:**

| Namespace | Generates | Example |
|---|---|---|
| `--color-*` | color utilities across every color-accepting property | `bg-red-500`, `text-sky-300`, `fill-mint-500` |
| `--font-*` | font-family utilities | `font-sans`, `font-display` |
| `--text-*` | font-size utilities (each can carry a paired `--text-*--line-height`) | `text-xl` |
| `--font-weight-*` | `font-bold`, `font-semibold` |
| `--tracking-*` | letter-spacing | `tracking-wide` |
| `--leading-*` | line-height | `leading-tight` |
| `--breakpoint-*` | responsive variants | `sm:`, `md:`, `3xl:` |
| `--container-*` | container-query variants and `max-w-*` container sizes | `@md:`, `max-w-8xl` |
| `--spacing` (singular, one value) | the entire dynamic spacing scale | `p-4`, `gap-6`, `max-h-16` |
| `--radius-*` | `rounded-lg` |
| `--shadow-*` / `--inset-shadow-*` / `--drop-shadow-*` | `shadow-md`, `inset-shadow-xs`, `drop-shadow-lg` |
| `--blur-*` / `--perspective-*` | `blur-md`, `perspective-near` |
| `--aspect-*` | `aspect-video` |
| `--ease-*` / `--animate-*` | `ease-out`, `animate-spin` (pair `--animate-*` with a `@keyframes` block) |

**Editing an existing namespace, not just adding to it:**

```css
@theme {
  --breakpoint-sm: 30rem;        /* override one value */
  --color-*: initial;            /* clear the whole default color namespace, then redefine it */
  --color-white: #fff;
  --color-brand: #3f3cbb;
}

@theme {
  --*: initial;                  /* nuclear option: discard every default token, start blank */
  --spacing: 4px;
  --font-body: Inter, sans-serif;
}
```

**Keyframes belong inside `@theme`**, next to the `--animate-*` variable that references them:

```css
@theme {
  --animate-fade-in-scale: fade-in-scale 0.3s ease-out;

  @keyframes fade-in-scale {
    0%   { opacity: 0; transform: scale(0.95); }
    100% { opacity: 1; transform: scale(1); }
  }
}
```

**`inline` and `static` modifiers** (rare, know they exist):
- `@theme inline { --font-sans: var(--font-inter); }` — use when a theme variable's value is
  *itself* another CSS variable (e.g. one supplied by `next/font`); without `inline`, the utility
  can resolve the wrong value depending on cascade order, because the plain form keeps a
  `var()` reference instead of embedding the resolved value.
- `@theme static { ... }` — force Tailwind to always emit every variable in that theme block as a
  real CSS custom property, even if no utility in the source references it (default behavior only
  emits variables actually used by generated utilities).

## The single spacing scale

There is one `--spacing` value (default `0.25rem`), and every spacing/sizing utility is a multiple
of it, computed on demand — `mt-21`, `p-37` etc. work without declaring them, because
`--spacing(<n>)` is `calc(var(--spacing) * <n>)`. Changing `--spacing` rescales the entire
padding/margin/width/height/gap system at once.

## Functions

- **`--spacing(n)`** — `margin: --spacing(4);` compiles to `calc(var(--spacing) * 4)`. Usable
  inside arbitrary values too: `py-[calc(--spacing(4)-1px)]`.
- **`--alpha(color / pct)`** — `color: --alpha(var(--color-lime-300) / 50%);` compiles to
  `color-mix(in oklab, var(--color-lime-300) 50%, transparent)`. Use this instead of hand-rolling
  `color-mix()` for opacity adjustments in custom CSS.
- **`theme()`** (dot-notation, e.g. `theme(spacing.12)`) is the deprecated v3 compatibility
  function — new code uses the CSS variable directly (`var(--spacing-12)`) or `--spacing()`.

## Arbitrary values — brackets vs parentheses

- **`[...]`** — a literal one-off value: `top-[117px]`, `bg-[#316ff6]`, `grid-cols-[24rem_2.5rem]`.
  Spaces become underscores (`grid-cols-[1fr_500px_2fr]`); escape a literal underscore with `\_`.
- **`(...)`** — shorthand for referencing a CSS variable, equivalent to `[var(--x)]` but shorter:
  `bg-(--brand-color)` ≡ `bg-[var(--brand-color)]`. Also resolves ambiguous properties by data
  type: `text-(length:--my-var)` vs `text-(color:--my-var)`.
- Arbitrary properties for one-off CSS with no matching utility at all:
  `[mask-type:luminance]`, `[--scroll-offset:56px]` — these compose with variants normally:
  `hover:[mask-type:alpha]`.

## Custom directives

- **`@utility`** — the v4 way to register a new utility class that needs variant support
  (`hover:`, `md:`, …) or parsed values. Plain form:
  ```css
  @utility content-auto { content-visibility: auto; }
  ```
  Functional form (accepts a value/modifier) via `--value()` / `--modifier()`:
  ```css
  @theme { --tab-size-github: 8; }
  @utility tab-* {
    tab-size: --value(--tab-size-*, integer, [integer]);   /* theme lookup, bare int, or arbitrary */
  }
  @utility -inset-* {                                       /* negative-value variant, needs its own rule */
    inset: calc(--spacing(--value(integer)) * -1);
  }
  @utility text-* {
    font-size: --value(--text-*, [length]);
    line-height: --modifier(--leading-*, [length], [*]);    /* enables text-lg/loose */
  }
  @utility tab-* {
    tab-size: --value(integer, --default(4));                /* bare `tab` falls back to 4 */
  }
  ```
- **`@custom-variant`** — register a reusable variant. Shorthand for a single selector, block form
  (with `@slot`) for anything needing nesting (media queries, multiple rules):
  ```css
  @custom-variant theme-midnight (&:where([data-theme="midnight"] *));

  @custom-variant any-hover {
    @media (any-hover: hover) { &:hover { @slot; } }
  }
  ```
  As of v4.3, `@variant` supports stacking multiple variants in one block —
  `@variant hover:focus { ... }` (both must match) and `@variant hover, focus { ... }`
  (either matches).
- **`@reference`** — import theme tokens/utilities/variants into a scope *without* duplicating
  Tailwind's output, for Vue/Svelte `<style>` blocks or CSS Modules where `@apply`/`@variant`
  would otherwise have no theme to resolve against:
  ```vue
  <style>
  @reference "../../app.css";     /* or `@reference "tailwindcss";` if using only default theme */
  h1 { @apply text-2xl font-bold text-red-500; }
  </style>
  ```
- **`@plugin`** — load a legacy JS plugin: `@plugin "@tailwindcss/typography";`. Can coexist with
  `@theme`/`@utility`/`@custom-variant` in the same file; CSS-defined tokens win over the plugin's.
- **`@variant`** — apply a variant *inside* a hand-written CSS rule (as opposed to `@custom-variant`,
  which *defines* a new one):
  ```css
  .my-element {
    background: white;
    @variant dark { background: black; }
  }
  ```

## The default color palette

22 hue families (`red orange amber yellow lime green emerald teal cyan sky blue indigo violet
purple fuchsia pink rose` + grays `slate gray zinc neutral stone`) plus four palettes added in
**v4.2**: `mauve olive mist taupe` — muted, gray-adjacent neutrals distinct from the existing
5-gray set. Every family has shades `50`–`950` in OKLCH. Opacity is a slash modifier, not a
separate utility: `bg-sky-500/50`, `bg-pink-500/[71.37%]`, `bg-cyan-400/(--my-alpha-value)` — never
`bg-opacity-50` (removed, see `pitfalls.md`).
