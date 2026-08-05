# Ownership & Borrowing Reference

## The model in three lines

Every value has exactly one owner; ownership moves on assignment/call unless the type is `Copy`.
Any number of shared borrows (`&T`) XOR exactly one exclusive borrow (`&mut T`), never both
alive at once. Borrows must not outlive the owner — lifetimes only *describe* this, they never
extend anything.

## Designing ownership (do this before fighting the checker)

- **Who owns the data?** One clear owner per value; everything else borrows. If two things
  "need to own" it, decide: clone (cheap? fine), `Arc` (genuinely shared), or restructure so one
  owns and hands out views.
- Functions that only read take `&T`; that mutate take `&mut T`; that consume/store take `T`.
  Taking `T` "to be safe" forces clones on every caller.
- Store owned data in structs (`String`, `Vec<T>`); reach for `&'a str` fields only when the
  struct is a genuinely short-lived view — a lifetime parameter on a long-lived struct infects
  every user.

## Common checker fights and the right escape

| Symptom | Wrong fix | Right fix |
|---|---|---|
| "cannot borrow as mutable more than once" | `clone()` | split the struct, or borrow fields separately (the checker understands disjoint field borrows) |
| "borrowed value does not live long enough" | `'static` everywhere | make the owner live longer, or return owned data |
| self-referential struct | `unsafe` | restructure: store indices/keys instead of references, or use `Rc`/owner-arena patterns |
| need the value out of an `Option`/struct | fight with `&mut` | `take()` / `mem::replace` / `std::mem::swap` |
| iterating while mutating | index gymnastics | `retain`, `drain`, `extract_if`, or collect changes then apply |

## Clones: when they're fine

Cheap and honest: `Rc`/`Arc` handle clones, small `Copy` types, startup-time config. A `.clone()`
in a hot loop or added *solely* to satisfy the checker is the smell — restructure ownership.
Prefer `Cow<'_, str>` when a function sometimes borrows and sometimes owns.

## Smart pointers, minimal set

- `Box<T>` — heap allocation, single owner (recursive types, large values, `dyn`).
- `Rc<T>` / `Arc<T>` — shared ownership (single-thread / cross-thread). Add `RefCell`/`Mutex`
  only if the shared value must also mutate.
- `Weak<T>` — break `Rc`/`Arc` cycles (parent↔child graphs), or caches that must not keep
  values alive.

## Lifetime notes that matter in practice

- Elision covers most signatures; write explicit lifetimes only when the compiler asks or the
  relationship is genuinely ambiguous.
- Returning `&T` derived from a parameter ties the return to that parameter — if callers need it
  longer, return owned.
- Edition 2024 changed `impl Trait` capture defaults: opaque return types now capture all
  in-scope lifetimes unless you write precise capturing (`impl Iterator<Item = u32> + use<'a>`).
  If a return type suddenly "borrows too much" after an edition bump, that's why.
