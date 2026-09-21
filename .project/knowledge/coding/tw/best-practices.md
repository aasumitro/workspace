# Best Practices for Tailwind v4

## 1. Class detection is text scanning, not code parsing

Tailwind treats every source file as plain text and looks for tokens that look like class names —
it never evaluates JS/template logic. A dynamically-built string can't be found.

```jsx
// Bad — no "bg-${color}-500" class exists anywhere for the scanner to find
<div className={`bg-${color}-500`} />

// Good — every branch is a complete, literal string somewhere in the source
const colors = { blue: "bg-blue-500", red: "bg-red-500" };
<div className={colors[color]} />
```

If a value is genuinely dynamic and can't be enumerated (a user-picked hex color, a CMS value),
don't fight the scanner — use an inline style, optionally driving a Tailwind utility through a CSS
variable set in that same inline style:

```jsx
<button
  style={{ "--bg-color": buttonColor, "--bg-color-hover": buttonColorHover }}
  className="bg-(--bg-color) hover:bg-(--bg-color-hover) rounded-md px-3 py-1.5"
>
```

For anything the scanner should generate but that never appears literally in source (e.g. a class
name assembled by a shared component library at runtime), force it with `@source inline()` instead
of a JS `safelist` array — see `tooling-and-migration.md`.

## 2. Dark mode: default vs manual toggle

v4 defaults to OS preference via `prefers-color-scheme` — the `dark:` variant needs zero config.
Override it only when the product needs a user-facing toggle independent of the OS:

```css
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));                       /* class-based toggle */
@custom-variant dark (&:where([data-theme=dark], [data-theme=dark] *)); /* data-attribute toggle */
```

To support **both** a manual toggle and "respect system preference" without a flash of the wrong
theme, resolve and apply the class *before* first paint — inline in `<head>`, not in a bundled
script that loads after the DOM:

```html
<script>
  document.documentElement.classList.toggle(
    "dark",
    localStorage.theme === "dark" ||
      (!("theme" in localStorage) && window.matchMedia("(prefers-color-scheme: dark)").matches),
  );
</script>
```

```js
localStorage.theme = "light";       // explicit light
localStorage.theme = "dark";        // explicit dark
localStorage.removeItem("theme");   // back to following the OS
```

The theme choice can just as validly be resolved server-side and rendered directly into the
`class`/`data-theme` attribute — the inline-script version above is only needed for a purely
client-persisted preference.

## 3. `@utility` vs `@layer components` — they solve different problems

Both are correct in v4; they are not interchangeable, and picking the wrong one is the most common
mistake carried over from over-correcting v3 advice.

- **`@layer components`** — a reusable class for a whole component (`.card`, `.btn`) that utilities
  can still override by normal cascade-layer precedence. No variant support of its own; you write
  hover/dark states inside the rule with nesting or `@variant`.
  ```css
  @layer components {
    .card {
      background-color: var(--color-white);
      border-radius: var(--radius-lg);
      padding: var(--spacing-6);
      box-shadow: var(--shadow-xl);
    }
  }
  ```
  ```html
  <div class="card rounded-none"><!-- utility override still wins --></div>
  ```
- **`@utility`** — for something that should behave like a *real* utility: composable with
  `hover:`/`md:`/any variant automatically, and optionally parsing a value
  (`--value()`/`--modifier()`, see `modern-syntax.md`). Use this for design-system primitives, not
  for whole-component styling.
  ```css
  @utility btn {
    border-radius: var(--radius-md);
    padding-inline: var(--spacing-4);
  }
  ```
  ```html
  <button class="btn hover:btn md:btn"><!-- variants "just work" --></button>
  ```

Rule of thumb: reach for `@utility` only when you need variant composition or parsed values that
`@layer components` genuinely can't give you; default to `@layer components` (or a framework
component) for everything else.

## 4. `@apply`/`@variant` in framework `<style>` blocks need `@reference`

`@apply` and `@variant` need Tailwind's theme in scope to resolve against. A component-scoped
`<style>` block (Vue SFC, Svelte, CSS Modules) is compiled independently of the main stylesheet, so
without `@reference` it has no theme to resolve against and either errors or silently loses tokens.
`@reference` pulls in the theme/utilities/variants **without duplicating Tailwind's compiled output**
into every component's CSS:

```vue
<style>
@reference "../../app.css";       /* or `@reference "tailwindcss";` for the stock default theme */
.my-component {
  @apply text-red-500 bg-gray-100;
}
</style>
```

Note the current docs de-emphasize `@apply` for whole-component styling in favor of `@layer
components` classes or template partials — reach for `@apply` mainly to retrofit utility-driven
tokens onto CSS you don't otherwise control (a third-party widget's classes), not as the default
way to build new components.

## 5. Safelisting utilities

There is no JS `safelist` array in v4. Force generation of a class the scanner won't see (e.g. it's
assembled at runtime by a dependency) with `@source inline()` in CSS:

```css
@source inline("underline");                                 /* generates .underline */
@source inline("{hover:,focus:,}underline");                  /* + hover:/focus: variants */
@source inline("{hover:,}bg-red-{50,{100..900..100},950}");   /* brace-expansion ranges */
```

The inverse, `@source not inline(...)`, excludes classes that *would* otherwise be generated (a
narrow safety valve — reach for it rarely, e.g. to keep an unused color ramp out of the build).
