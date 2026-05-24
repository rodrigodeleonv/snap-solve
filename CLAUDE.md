# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install / sync all dependencies (including dev)
uv sync

# Run the app
uv run python snapsolve.py

# Add a runtime package
uv add <package>

# Add a dev-only package
uv add --dev <package>
```

Always use `uv` — never `pip` or `python -m pip`.

## Code quality

```bash
uv run ruff check src/ snapsolve.py          # lint
uv run ruff check --fix src/ snapsolve.py    # lint + auto-fix
uv run ruff format src/ snapsolve.py         # format
uv run pyright src/                          # type check
```

All three must pass before committing. Run `/py` for the full style guide.

## Configuration

The app reads from `.env` (git-ignored). Copy `example.env` to `.env` to configure. The only required field is one of `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `GROQ_API_KEY`.

## Architecture

The entry point is `snapsolve.py` → `src/main.py:App`. The flow on every hotkey press:

```
pynput thread  →  App._on_hotkey()
                      ├─ capture_screen()          # sync, in pynput thread
                      ├─ root.after(0, show_loading)  # schedules UI on main thread
                      └─ threading.Thread → _analyze_and_display()
                                                ├─ ai_client.analyze()   # blocking API call
                                                └─ root.after(0, show_response/show_error)
```

**Thread rule:** tkinter must only be touched from the main thread. All UI updates from background threads go through `root.after(0, fn)`.

**Provider selection** (`src/config.py`): `config.provider` auto-detects from which API key is present. Priority: `claude` → `openai` → `groq`. Override with `SNAPSOLVE_PROVIDER`.

**`src/ai_client.py`**: dispatches to `_claude()`, `_openai()`, or `_groq()` based on `config.provider`. All three take `png_bytes: bytes` and return `str`.

**`src/ui.py:ResponseWindow`**: a `tk.Toplevel` (not a standalone `Tk()`). The hidden root `Tk()` in `App.__init__` owns the event loop; `ResponseWindow` is created/destroyed on each capture cycle.

## macOS permissions

Global hotkeys require **Accessibility** and screenshots require **Screen Recording** in System Settings → Privacy & Security. Without these the app runs silently but does nothing.
