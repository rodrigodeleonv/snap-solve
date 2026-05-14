# SnapSolve

A lightweight desktop utility that captures your screen with a keyboard shortcut, sends the screenshot to an AI model (Claude), and displays the response in a floating window — without leaving your current application.

---

## How it works

```
Keyboard shortcut
      │
      ▼
 Screenshot taken        ← before the response window appears
      │
      ▼
 Sent to Claude API      ← vision-capable model
      │
      ▼
 Response shown          ← always-on-top floating window
```

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| API key | Anthropic **or** OpenAI (at least one) |

---

## Installation

### 1 — Clone and enter the directory

```bash
git clone <repo-url>
cd snap-solve
```

### 2 — Install dependencies

```bash
uv sync
```

This creates a `.venv` and installs all packages automatically.

### 3 — Configure

Copy the example environment file and fill in your API key:

```bash
cp example.env .env
```


Open `.env` and set one API key:

```env
# Option A — Anthropic / Claude
ANTHROPIC_API_KEY=sk-ant-...

# Option B — OpenAI / ChatGPT
OPENAI_API_KEY=sk-...

# Option C — Groq
GROQ_API_KEY=gsk_...
```

SnapSolve auto-detects the provider from whichever key is set. Priority when multiple keys are present: Claude → OpenAI → Groq. Override with `SNAPSOLVE_PROVIDER=groq`.

All other settings are optional (see [Configuration](#configuration)).

---

## Running

```bash
uv run python snapsolve.py
```

The tool starts silently in the background. Press the configured hotkey (default: **Ctrl + Shift + S**) at any time to capture the screen and get an AI response.

Press **Ctrl-C** in the terminal to quit.

---

## Configuration

All options live in `.env`:

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Anthropic API key (Claude) |
| `OPENAI_API_KEY` | — | OpenAI API key (ChatGPT) |
| `GROQ_API_KEY` | — | Groq API key |
| `SNAPSOLVE_PROVIDER` | auto | `claude`, `openai`, or `groq` — auto-detected if omitted |
| `SNAPSOLVE_MODEL` | see below | Model ID — defaults per provider |
| `SNAPSOLVE_HOTKEY` | `<ctrl>+<shift>+s` | Global keyboard shortcut |
| `SNAPSOLVE_SYSTEM_PROMPT` | *(see example.env)* | Instructions sent to the model |
| `SNAPSOLVE_MAX_TOKENS` | `1024` | Maximum response length |

### Changing the hotkey

Use [pynput key names](https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key):

```env
# Ctrl + Shift + S  (default, works on both platforms)
SNAPSOLVE_HOTKEY=<ctrl>+<shift>+s

# Ctrl + Alt + Space
SNAPSOLVE_HOTKEY=<ctrl>+<alt>+<space>

# macOS: Command + Shift + S
SNAPSOLVE_HOTKEY=<cmd>+<shift>+s
```

### Available vision models

**Claude (Anthropic)**

| Model ID | Speed | Notes |
|---|---|---|
| `claude-sonnet-4-6` | Balanced | Default for Claude |
| `claude-opus-4-5` | Slower, thorough | Best accuracy |
| `claude-haiku-4-5-20251001` | Fastest | Good for simple questions |

**OpenAI / ChatGPT**

| Model ID | Speed | Notes |
|---|---|---|
| `gpt-4o` | Fast | Default for OpenAI — recommended |
| `gpt-4o-mini` | Fastest | Lower cost, less accurate |
| `gpt-4-turbo` | Balanced | Older vision model |

**Groq**

| Model ID | Speed | Notes |
|---|---|---|
| `meta-llama/llama-4-scout-17b-16e-instruct` | Very fast | Default for Groq |
| `meta-llama/llama-4-maverick-17b-128e-instruct` | Fast | More capable |

---

## Platform notes

### macOS

Two system permissions are required:

1. **Accessibility** — needed to listen for global hotkeys.
   - System Settings → Privacy & Security → Accessibility → enable your terminal app (or Python).

2. **Screen Recording** — needed to capture the screen.
   - System Settings → Privacy & Security → Screen Recording → enable your terminal app (or Python).

If either permission is missing, SnapSolve will either fail silently on the hotkey or crash with a permissions error. Grant both, then restart.

### Windows

Run the terminal (or `.exe`) **as Administrator** if global hotkeys are not firing. Windows may block low-level keyboard hooks for non-elevated processes depending on UAC settings.

---

## Project structure

```
snap-solve/
├── snapsolve.py          Entry point
├── pyproject.toml        uv project config & dependencies
├── uv.lock               Reproducible lockfile
├── example.env          Config template
├── .env                  Your local config (git-ignored)
└── src/
    ├── config.py         Reads environment variables
    ├── hotkey.py         Global keyboard listener (pynput)
    ├── screenshot.py     Screen capture (mss + Pillow)
    ├── ai_client.py      Claude API call (anthropic SDK)
    ├── ui.py             Floating response window (tkinter)
    └── main.py           Orchestration & thread model
```

---

## Thread model

```
Main thread    tkinter event loop — all UI creation and updates happen here
Hotkey thread  pynput GlobalHotKeys listener (daemon)
Worker thread  screenshot capture + API call, one per trigger (daemon)
```

UI updates from background threads are always scheduled via `root.after(0, fn)` to ensure thread safety.

---

## Response window

| Action | Shortcut / control |
|---|---|
| Close | **Esc** or the **Close** button |
| Copy response to clipboard | **Copy** button |
| Move window | Click-drag the title bar |

---

## License

MIT
