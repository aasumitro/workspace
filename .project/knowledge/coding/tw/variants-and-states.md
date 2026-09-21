# Variants and States

A variant is a prefix that scopes a utility to a condition — `hover:bg-sky-700` only applies
`bg-sky-700` inside a compiled `&:hover` rule. Variants stack (`dark:md:hover:bg-fuchsia-600`) and
apply **left-to-right**, both in the class name and in how you reason about them.

## Pseudo-classes

**Interactive:** `hover:` (wrapped in `@media (hover: hover)` so touch devices don't get stuck
"hover" states), `focus:`, `focus-within:`, `focus-visible:`, `active:`, `visited:`.

**Structural / position:** `first:`, `last:`, `only:`, `odd:`, `even:`, `first-of-type:`,
`last-of-type:`, `only-of-type:`, `empty:`, `target:`. Arbitrary position: `nth-3:`,
`nth-last-5:`, `nth-of-type-3:`, `nth-last-of-type-6:`, or `nth-[3n+1]:` for a full expression.

**Form state:** `disabled:`, `enabled:`, `checked:`, `indeterminate:`, `default:`, `required:`,
`optional:`, `valid:`, `invalid:`, `user-valid:`, `user-invalid:` (only after the user has
interacted — use these instead of `invalid:` to avoid red-bordering an untouched field),
`in-range:`, `out-of-range:`, `placeholder-shown:`, `autofill:`, `read-only:`.

**Relational:** `has-[selector]:` — style based on a descendant (`has-checked:bg-indigo-50`,
`has-[img]:block`); `not-[selector]:` — negate any selector (`hover:not-focus:bg-indigo-700`
applies on hover unless also focused); `inert:` — styled while the element carries the `inert`
attribute.

## Pseudo-elements

`before:` / `after:` (auto-include `content: ''`, so `after:content-['*']` is enough to set text),
`placeholder:`, `file:` (the file-input button), `marker:` (list bullets/numbers, inherits down),
`selection:` (text-selection highlight, inherits down — set once on `<body>` for the whole page),
`first-line:`, `first-letter:`, `backdrop:` (native `<dialog>`'s backdrop), `details-content:`
(the `<details>` disclosure content box).

## Media / feature queries

**Responsive breakpoints** (mobile-first — unprefixed = all sizes, prefixed = that size *and up*):

| Prefix | Min width | Prefix | Min width |
|---|---|---|---|
| `sm:` | 40rem / 640px | `xl:` | 80rem / 1280px |
| `md:` | 48rem / 768px | `2xl:` | 96rem / 1536px |
| `lg:` | 64rem / 1024px | | |

Every breakpoint has a `max-*` inverse (`max-md:` = `< 48rem`) — stack the two to target a range:
`md:max-lg:flex` applies only between 768px and 1024px. Arbitrary one-offs: `min-[320px]:`,
`max-[600px]:`. Redefine the scale via `@theme { --breakpoint-* }` (`modern-syntax.md`).

**Container queries** — respond to a *parent's* size instead of the viewport; more portable for a
reusable component than a breakpoint variant. Mark the parent `@container`, condition the children
on `@sm:`…`@7xl:` (default container scale runs `@3xs` 16rem through `@7xl` 80rem — finer-grained
than the breakpoint scale since containers are commonly narrower than the viewport). `@container`
only queries inline-size; use `@container-size` (added v4.3) when you need block-size too, unlocking
`cqb`/`cqh` units. Named containers for nesting: `@container/sidebar` on the parent,
`@sm/sidebar:flex-row` on a descendant several levels down. Ranges and arbitrary values work the
same as breakpoints: `@sm:@max-md:flex-col`, `@min-[475px]:flex-row`.

**Color scheme:** `dark:` — `@media (prefers-color-scheme: dark)` by default; see
`best-practices.md` for the manual-toggle override.

**Motion / vision preferences:** `motion-safe:`, `motion-reduce:`, `contrast-more:`,
`contrast-less:`, `forced-colors:` / `not-forced-colors:` (Windows High Contrast Mode — pair with
`appearance-none forced-colors:appearance-auto` on custom radio/checkbox replacements so forced
colors mode gets the native control back), `inverted-colors:`.

**Input mechanism:** `pointer-fine:`, `pointer-coarse:`, `pointer-none:` and the `any-pointer-*`
equivalents (any connected pointer, not just the primary one) — use `pointer-coarse:p-4` to give
touch targets more padding without a JS device check.

**Other:** `portrait:`/`landscape:`, `print:`, `supports-[...]:`/`not-supports-[...]:` (`@supports`
feature detection — `supports-[display:grid]:grid` falls back gracefully), `starting:` (maps to
`@starting-style`, the entry-transition at-rule — needed for `<dialog>`/popover open transitions
that CSS couldn't animate before this).

## Attribute selectors

**ARIA:** `aria-checked:`, `aria-disabled:`, `aria-expanded:`, `aria-hidden:`, `aria-pressed:`,
`aria-selected:`, etc. target `[aria-x="true"]`; arbitrary values for non-boolean ARIA:
`aria-[sort=ascending]:bg-[url('/down-arrow.svg')]`.

**Data attributes:** `data-active:` checks existence (`&[data-active]`); `data-[size=large]:p-8`
checks a specific value. Custom data-attribute variants that need substring/token matching go
through `@custom-variant`: `@custom-variant data-checked (&[data-ui~="checked"]);`.

**Direction:** `rtl:`/`ltr:` (`:dir()`) — for logically-aware spacing prefer the logical-property
utilities in `patterns.md` over `ltr:ml-3 rtl:mr-3` pairs.

**Disclosure state:** `open:` — `<details>`/`<dialog>` open, or `:popover-open`.

## Parent / sibling / descendant state

- **`group`** on the ancestor, **`group-*`** on descendants: `group-hover:text-white`. Works with
  any pseudo-class (`group-focus`, `group-odd`, …).
- **Named groups** for nested `group`s: `group/item` on the outer, `group-hover/item:visible` on
  the element that must react specifically to `.group\/item`'s hover, not a closer ancestor group.
- **`peer`** on a sibling, **`peer-*`** on a *later* sibling: `peer-invalid:visible` on a hint
  paragraph after a `peer`-marked `<input>`. CSS limitation, not a Tailwind one: `peer` only
  reaches forward, never backward — order your markup accordingly. Named peers
  (`peer/draft`, `peer-checked/draft:text-sky-500`) disambiguate multiple peers in one form.
- **`has-*`**, **`group-has-*`**, **`peer-has-*`** — react to a *descendant's* state instead of the
  element's own or a sibling/parent's: `group-has-[a]:block` shows an icon only if the group
  contains a link.
- **`*:`** — style direct children from the parent without touching child markup:
  `*:rounded-full *:border`. A child cannot out-specificity a parent's `*:` rule for the same
  property (same specificity, parent's rule is emitted later) — reach for a real child selector or
  arbitrary variant if a child genuinely needs to override it.
- **`**:`** — same idea for *all* descendants, not just direct children: useful combined with an
  attribute selector to reach into a component you don't control the markup of:
  `**:data-avatar:size-12`.
- **`in-*:`** — like `group-*` but for when adding a literal `group` class isn't practical (e.g. no
  control over the ancestor's class list): `in-focus:opacity-100` reacts to *any* focused ancestor.

## Arbitrary and custom variants

One-off selector, written inline with `[&...]`:

```html
<div class="[&.is-dragging]:cursor-grabbing [&_p]:mt-4 flex [@supports(display:grid)]:grid">
```

(`&_p` — underscore for the descendant-combinator space, same escaping rule as arbitrary values.)
Register a reusable version with `@custom-variant` when the same custom selector shows up more than
once — see `modern-syntax.md` for the directive syntax.

## v4-specific additions to watch for

`nth-*` family (full arbitrary-expression support), `inert:`, `**:`, `starting:`, and `not-*:` are
all new since v3 — a model trained mostly on v3 examples will not reach for these on its own even
though they're frequently the right tool.
