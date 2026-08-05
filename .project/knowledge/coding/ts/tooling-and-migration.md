# Tooling & Migration Reference (tsconfig · TS 6 → 7)

## tsconfig baseline (new projects)

```jsonc
{
  "compilerOptions": {
    // strictness — the floor
    "strict": true,
    "noUncheckedIndexedAccess": true,     // arr[i] is T | undefined — honest
    "exactOptionalPropertyTypes": true,   // x?: T ≠ x: T | undefined
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "noPropertyAccessFromIndexSignature": true,

    // module honesty
    "module": "nodenext",                 // or "preserve" + bundler resolution for bundled apps
    "verbatimModuleSyntax": true,         // type imports are explicit, emit is predictable
    "isolatedModules": true,

    // output hygiene (libraries)
    "declaration": true,
    "isolatedDeclarations": true,         // d.ts emit without type-checking dependencies — faster, parallel
    "skipLibCheck": true,

    "target": "es2023",                   // match the real runtime floor
    "lib": ["es2023"]                     // + "dom" only for browser code
  }
}
```

Apps that bundle (Vite-class): `moduleResolution: "bundler"`, `noEmit: true` — the bundler
emits, `tsc` only checks. Monorepos: project references + `composite`; one root
`tsc -b` builds the graph.

## The support cadence

- **TS 5.x** — legacy line; fine to stay on until your toolchain's ecosystem (framework
  plugins, editor) supports 6/7.
- **TS 6.x** — the bridge: last JS-based compiler, behavior aligned with 7, legacy flags
  removed. Being clean on 6 *is* the 7 migration.
- **TS 7.x** — the native (Go) compiler: ~10x faster type-checking/builds, dramatically better
  editor latency on large repos. Same language; new toolchain internals.

## Migrating 5.x → 6

1. Upgrade TS only (no config changes); fix new type errors — they're usually found bugs.
2. Remove/replace deprecated options the 6.x line rejects: ancient `target`s, `namespace`-era
   emit modes, AMD/UMD/`outFile`, old `moduleResolution` values (`node10`) — move to
   `nodenext`/`bundler` resolution.
3. Turn on the module-honesty flags (`verbatimModuleSyntax`, `isolatedModules`) if not already —
   mechanical fixes (`import type`), big payoff.
4. Kill remaining `enum`/`namespace`/decorator-legacy patterns in *new* code paths
   (`modern-syntax.md` idiom table); existing const enums: replace with `as const` objects
   (const enum inlining is a cross-compiler hazard).
5. Green build with **zero deprecation warnings** = ready for 7.

## Migrating 6 → 7

- **Source code**: little to none — the language is the same.
- **Toolchain**: swap the compiler package/CLI per the 7.x install docs; editor/LSP updates；
  CI scripts that shell out to `tsc` keep working via the compatibility CLI, but re-measure
  timeouts (they'll be embarrassingly oversized).
- **Breakage surface = programmatic compiler-API use**: custom transformers, lint rules built
  on the TS API, codegen scripts importing `typescript`. Inventory these first
  (`grep -r "from \"typescript\""`); migrate or pin them deliberately.
- Run 6 and 7 side by side in CI for one cycle (`tsc` vs native check) — diffs are either 7
  finding real issues or a migration gap; triage before switching the gate.

## Lint & format

- Formatter (prettier or biome) settles style; nobody argues in review.
- typescript-eslint with the async-safety pack non-negotiable: `no-floating-promises`,
  `no-misused-promises`, `await-thenable`, `no-unnecessary-condition`,
  `switch-exhaustiveness-check`, `consistent-type-imports`.
- Type-aware lint is slow on big repos — scope it to CI + editor-on-save, not pre-commit.

## Dependency hygiene

Types ship with packages (`@types/*` only for stragglers, dev-dependency). Library authors:
test your published types (`arethetypeswrong`-class checks) — ESM/CJS dual-publish typing is
where consumers break. Pin the `typescript` version in `devDependencies` exactly during the
6→7 window; loose ranges across a compiler-engine swap invite "works on my machine".
