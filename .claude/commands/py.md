When writing or reviewing Python code in this project, apply these rules:

## Formatting (enforced by ruff)
- Double quotes for all strings
- Line length ≤ 100 characters
- Imports ordered: stdlib → third-party → local, separated by blank lines

## Type hints
- All function signatures must be fully annotated (parameters + return type)
- Use `X | Y` union syntax (Python 3.10+), not `Optional[X]` or `Union[X, Y]`
- Use lowercase generics: `list[x]`, `dict[k, v]`, `tuple[...]`, not `List`, `Dict`, `Tuple`
- Use `ClassVar[T]` for mutable class-level attributes
- Use `dict[str, Any]` when a dict is unpacked as `**kwargs` into typed functions

## Style
- Private members prefixed with `_`
- Lambdas that close over exception variables must capture by default arg: `lambda e=exc: f(e)`
- Prefer `contextlib.suppress(ExcType)` over bare `try/except/pass`
- No comments explaining *what* — only *why* when non-obvious

## Imports
- Remove all unused imports — ruff catches most (`F401`), but **submodule imports** (e.g. `import pkg.sub`) are silently skipped because ruff assumes they may be for side-effects. Review these manually.

## Linting commands
```bash
uv run ruff check src/ snapsolve.py          # lint
uv run ruff check --fix src/ snapsolve.py    # lint + auto-fix
uv run ruff format src/ snapsolve.py         # format
uv run pyright src/                          # type check
```

All three must pass with zero errors before considering code complete.
