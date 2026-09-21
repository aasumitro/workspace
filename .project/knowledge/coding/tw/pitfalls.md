# Tailwind v4 Pitfalls & Anti-Patterns

Models (including this one) default to v3 muscle memory. Every item here is a case where the old,
plausible-looking syntax either silently does nothing, does something different, or was removed
outright. When reviewing or writing Tailwind code, check against this list first.

## Renamed utilities (the #1 hallucination source)

The `-sm` size shifted down a step across every filter/shadow/radius scale, and the old `-sm` slot
now means something one step smaller:

| v3 | v4 |
|---|---|
| `shadow-sm` | `shadow-xs` |
| `shadow` | `shadow-sm` |
| `drop-shadow-sm` | `drop-shadow-xs` |
| `drop-shadow` | `drop-shadow-sm` |
| `blur-sm` | `blur-xs` |
| `blur` | `blur-sm` |
| `backdrop-blur-sm` | `backdrop-blur-xs` |
| `backdrop-blur` | `backdrop-blur-sm` |
| `rounded-sm` | `rounded-xs` |
| `rounded` | `rounded-sm` |
| `outline-none` | `outline-hidden` (now correctly sets `outline-style: none`; the old `outline-none` name is gone) |
| `ring` (bare, 3px) | `ring-3` (bare `ring` is now 1px — the default width changed, not just the name) |
| `flex-shrink-*` | `shrink-*` |
| `flex-grow-*` | `grow-*` |
| `overflow-ellipsis` | `text-ellipsis` |
| `decoration-slice` / `decoration-clone` | `box-decoration-slice` / `box-decoration-clone` |

## Opacity modifiers replaced the `-opacity-*` utilities

`bg-opacity-50`, `text-opacity-50`, `border-opacity-50`, `divide-opacity-50`, `ring-opacity-50`,
`placeholder-opacity-50` are all **gone**. Opacity is always a slash modifier on the color utility
itself: `bg-black/50`, `text-red-500/75`. There is no separate opacity class to combine with a
solid-color one.

## Default value changes

| Property | v3 default | v4 default |
|---|---|---|
| Border color | `gray-200` | `currentColor` — a bare `border` class now needs an explicit color utility next to it or it inherits the text color |
| Ring width | `3px` | `1px` (use `ring-3` for the old width) |
| Ring color | `blue-500` | `currentColor` |
| Placeholder color | `gray-400` | current text color at 50% opacity |
| Button cursor | `pointer` | `default` (matches native browser button behavior — add `cursor-pointer` explicitly if the old feel is wanted) |

## The important modifier moved to a suffix

```html
<!-- v3 -->
<div class="!flex !bg-red-500">
<!-- v4 -->
<div class="flex bg-red-500 hover:bg-red-600/50!">
```

`!` goes at the end of the individual utility, including after a variant chain, not at the front of
the class.

## Conflicting utilities resolve by CSS source order, not HTML order

```html
<div class="grid flex"><!-- renders as display: grid, not flex --></div>
```

Whichever utility's generated rule comes later in the **compiled stylesheet** wins — Tailwind's
internal ordering, not the order you typed the classes in the `class` attribute. Never rely on
"later in the string wins"; only ever put one utility per CSS property on an element, branching in
the source instead (`gridLayout ? "grid" : "flex"`).

## Variant stacking order flipped

```html
<!-- v3: right-to-left -->
<ul class="py-4 first:*:pt-0 last:*:pb-0">
<!-- v4: left-to-right -->
<ul class="py-4 *:first:pt-0 *:last:pb-0">
```

## `space-y-*` / `space-x-*` selector changed

```css
/* v3 */
.space-y-4 > :not([hidden]) ~ :not([hidden]) { margin-top: 1rem; }
/* v4 */
.space-y-4 > :not(:last-child) { margin-bottom: 1rem; }
```

Behaves differently around inline elements and children with their own margins. For anything new,
prefer `flex flex-col gap-4` over `space-y-4` — it sidesteps the selector entirely and was already
the general recommendation even before this change.

## Arbitrary CSS-variable syntax changed brackets to parentheses

```html
<!-- v3 -->
<div class="bg-[--brand-color]">
<!-- v4 -->
<div class="bg-(--brand-color)">
```

`[...]` is still correct for literal arbitrary values (`bg-[#316ff6]`); only the CSS-variable
shorthand moved to `(...)`.

## Comma-separated arbitrary values need underscores

```html
<!-- v3 -->
<div class="grid-cols-[max-content,auto]">
<!-- v4 -->
<div class="grid-cols-[max-content_auto]">
```

## Gradients preserve un-overridden stops across variants

In v3, overriding one gradient stop via a variant (e.g. `dark:from-blue-500`) reset the whole
gradient. In v4 the other stops persist, so a three-stop gradient overridden only for `from`/`to`
in dark mode keeps the original `via` color unless it's reset explicitly:

```html
<div class="bg-linear-to-r from-red-500 via-orange-400 to-yellow-400
            dark:from-blue-500 dark:via-none dark:to-teal-400">
```

## `transform`-resetting utilities now reset only that axis

```html
<!-- v3: focus:transform-none reset scale AND rotate AND translate -->
<button class="scale-150 focus:transform-none">
<!-- v4: reset the specific transform property -->
<button class="scale-150 focus:scale-none">
```

## Container utility lost its config options

v3's `container` had `theme.container.center`/`.padding` config keys; v4 has none — define the
same behavior as a custom `@utility`:

```css
@utility container {
  margin-inline: auto;
  padding-inline: 2rem;
}
```

## Class prefixes now look like a variant

```html
<!-- v4, with `@import "tailwindcss" prefix(tw);` -->
<div class="tw:flex tw:bg-red-500 tw:hover:bg-red-600">
```

The prefix sits at the very front of the class, before any variant, not glued to the utility name
as it was in v3's config-based prefix.

## `theme()` function argument syntax changed

```css
/* v3 */
@media (width >= theme(screens.xl)) { ... }
/* v4 */
@media (width >= theme(--breakpoint-xl)) { ... }
```

Dot-notation paths (`spacing.12`) still parse for compatibility, but reference the CSS variable
name (`--spacing-12`) in new code — or better, skip `theme()` entirely and use
`var(--breakpoint-xl)` / `--spacing()` directly (`modern-syntax.md`).

## Dynamic class construction still doesn't work — it never did

Unchanged from v3, but worth restating because it's the most common actual bug, not just a
stylistic nit: Tailwind parses source as plain text. `` `text-${color}-600` `` and
`{{ 'text-' + color + '-600' }}` produce zero matching classes at build time no matter how
confident the runtime string looks. See `best-practices.md` §1 for the fix.
