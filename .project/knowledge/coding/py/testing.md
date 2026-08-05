# Testing Reference

pytest is the assumed runner. Plain `assert`, plain functions, fixtures for setup — no
unittest-style classes unless the project already has them.

## Layout & naming

`tests/` mirrors the package (tests/billing/test_invoices.py ↔ pkg/billing/invoices.py).
Test names state behavior: `test_expired_trial_resumes_as_trialing`, not `test_resume_2`.
Arrange–act–assert with a blank line between phases; one behavior per test.

## Parametrize over copy-paste

```python
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1.00", 100),
        ("0", 0),
        pytest.param("1e2", 10000, id="scientific"),
    ],
)
def test_parse_cents(raw: str, expected: int) -> None:
    assert parse_cents(raw) == expected
```

Failure output names the case (`id=`) — a failing row must identify itself.

## Fixtures

- Small, composable, narrowest scope that works (function default; `session` only for genuinely
  shared, immutable, expensive things like a container).
- `yield` fixtures own their teardown; `tmp_path` for files; `monkeypatch` for env/attrs —
  never hand-rolled try/finally cleanup in tests.
- `conftest.py` per directory for shared fixtures; if a fixture needs a docstring novel, it's
  doing too much — split it.
- Factory fixtures (`def make_order(**overrides) -> Order`) over big frozen fixture objects —
  each test states only what it cares about.

## Exceptions & warnings

```python
with pytest.raises(QuotaExceeded) as exc_info:
    reserve(order)
assert exc_info.value.metric == "storage"
```

Assert on the exception's *fields/type*, not its message string. `match=` sparingly (regex on
messages is brittleness by subscription). `pytest.warns` for warning contracts.

## Test doubles

- Prefer real objects → hand-rolled fakes implementing the Protocol seam (`typing.md`) →
  `unittest.mock` last.
- When mocking: patch **where it's used** (`patch("pkg.billing.invoices.gateway")`, not
  `patch("gateway_lib.charge")`); use `autospec=True`/`create_autospec` so signature drift
  fails tests; assert on *observable effects* first, `assert_called_once_with` second.
- A test that mostly asserts mock call sequences is testing the implementation — rewrite
  against behavior.

## Async tests

`pytest-asyncio` (or anyio): `async def test_...` with the project's configured mode. Fake the
clock/timeouts where possible; a real `sleep` in a test is a flake with a fuse. TaskGroup-based
code: assert on `ExceptionGroup` contents with `except*` semantics in mind.

## Coverage & discipline

- Regression test per bug fix — written to fail without the fix.
- Coverage (`pytest --cov`) is a risk map, not a KPI; assertion-free tests to inflate it are
  worse than nothing.
- Tests are parallel-safe (`pytest -n auto` with xdist): unique tmp dirs, no fixed ports, no
  module-global mutation without `monkeypatch`.
- Property-based testing (`hypothesis`) for parsers/round-trips/invariants; keep found
  counterexamples as explicit `@example`s.
