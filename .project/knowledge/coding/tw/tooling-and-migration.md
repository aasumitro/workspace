# Tooling and Setup

## Browser support is a hard floor, not a graceful-degradation target

v4 requires **Chrome 111+, Safari 16.4+, Firefox 128+** — it depends on native cascade layers,
`@property`, and `color-mix()`, none of which have a polyfill path. There is no v4 build that
degrades cleanly on older browsers; a project with a real legacy-browser requirement stays on v3.

## Installation

- **Vite:** `npm install tailwindcss @tailwindcss/vite`, add the plugin, import once in CSS:
  ```ts
  // vite.config.ts
  import tailwindcss from "@tailwindcss/vite";
  export default defineConfig({ plugins: [tailwindcss()] });
  ```
  ```css
  /* entry CSS */
  @import "tailwindcss";
  ```
- **PostCSS:** `@tailwindcss/postcss` replaces `tailwindcss` as a PostCSS plugin, and also
  replaces `postcss-import` + `autoprefixer` — v4 handles both internally via Lightning CSS:
  ```js
  export default { plugins: { "@tailwindcss/postcss": {} } };
  ```
- **CLI (no bundler):** `@tailwindcss/cli` —
  `npx @tailwindcss/cli -i input.css -o output.css`.
- **Webpack:** a dedicated `@tailwindcss/webpack` plugin exists (added alongside v4.2) for a large
  build-perf win over the generic PostCSS path in webpack-based frameworks (e.g. Next.js).

The legacy `@tailwind base;`/`@tailwind components;`/`@tailwind utilities;` three-directive form is
gone — it's a single `@import "tailwindcss";`.

## Source detection

Tailwind auto-scans the project as plain text (`best-practices.md` §1 on why that matters), skipping
anything `.gitignore`d, everything under `node_modules`, binary files, CSS files, and lockfiles. No
`content: []` array to maintain. Extend or restrict it explicitly:

```css
@import "tailwindcss";
@source "../node_modules/@my-company/ui-lib";      /* register a path the scanner wouldn't see (e.g. gitignored) */
@source not "../src/components/legacy";            /* exclude a path known not to use Tailwind */
```

```css
@import "tailwindcss" source("../src");             /* set the base scan path (monorepos run from root) */
@import "tailwindcss" source(none);                  /* disable auto-detection entirely */
@source "../admin";                                  /* — then opt in explicitly, path by path */
@source "../shared";
```

`source(none)` is for a project running multiple independent Tailwind stylesheets that must each
see a different class set — most projects never need it.

## Upgrading an existing v3 project

`npx @tailwindcss/upgrade` migrates config and CSS to v4 syntax automatically (requires Node 20+).
It rewrites most of `pitfalls.md`'s renames for you, but always diff the result — automated
migration of `@apply`-heavy custom CSS and JS-config edge cases (`corePlugins`, plugin options)
needs a manual pass.

## `@config` / `@plugin` — the incremental-migration escape hatches

A v3 `tailwind.config.js` can still be loaded during migration:

```css
@import "tailwindcss";
@config "../../tailwind.config.js";
```

`corePlugins`, `safelist`, and `separator` from that config are **not honored** in v4 — replace
`safelist` with `@source inline()` (`best-practices.md` §5); there's no v4 equivalent for
`corePlugins`/`separator` because the concepts they gated no longer exist. Legacy JS plugins load
with `@plugin "@tailwindcss/typography";` and can coexist with CSS-native `@theme`/`@utility`
definitions in the same file — CSS-defined tokens take precedence over the plugin's.

## Preprocessors (Sass/Less/Stylus) are actively discouraged, not just unnecessary

v4 fills the roles a preprocessor used to: `@import` bundling (no `postcss-import` needed), native
CSS nesting via Lightning CSS, native `var()` in place of preprocessor variables, and
`calc()`/`min()`/`max()`/`round()` for math `color-mix()` for what `darken()`/`lighten()` used to
do. Layering Sass on top adds a second variable/nesting system fighting the one Tailwind already
provides, with no capability gained — treat Tailwind itself as the preprocessor.
