# Go Guide — use when working with `.go` files

> Current to **Go 1.26**. General-purpose reference + style guide — project-independent. Match
> features to the project's `go.mod` version: use everything up to it, nothing past it
> (`modern-syntax.md` is version-gated for exactly this).

## Files

| File | Read when |
|---|---|
| `modern-syntax.md` | Always at least once — version-gated feature reference, Go 1.0 → 1.26 (incl. `new(val)`, `errors.AsType[T]`, `slog.NewMultiHandler`, `go fix`) |
| `patterns.md` | Naming, package layout, interfaces, constructors — the "how Go code looks" doc |
| `error-handling.md` | Any error path: wrapping, sentinel vs typed errors, messages |
| `context-patterns.md` | Anything taking/passing `context.Context` |
| `concurrency.md` | Goroutines, channels, errgroup, sync primitives |
| `slices-and-maps.md` | Slice/map mechanics, aliasing, memory-leak traps |
| `generics.md` | Type parameters — when to use and when not to |
| `testing.md` | Writing tests: table-driven, helpers, parallel, fuzzing |
| `performance.md` | Only with a measured symptom — allocation, pooling, GOMAXPROCS |
| `pitfalls.md` | Reviewing or debugging — the classic traps (nil interface, closure capture, …) |

## The five rules that outrank everything

1. Handle every error; wrap with context: `fmt.Errorf("pkg.Op: %w", err)`.
2. `gofmt` output is not negotiable; naming per `patterns.md` (MixedCaps, `ID`/`URL` caps, no
   `Get` prefix).
3. Accept interfaces, return concrete types; keep interfaces small and defined by the consumer.
4. Never start a goroutine you can't stop — every goroutine has an owner and an exit path.
5. The race detector (`go test -race`) is part of "tests pass".
