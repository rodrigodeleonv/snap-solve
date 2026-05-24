"""
Response window shown after a screenshot is analyzed.

Runs exclusively on the main thread via root.after() callbacks.
"""

import contextlib
import tkinter as tk
from tkinter import font as tkfont
from typing import Any

# ── Color palette ──────────────────────────────────────────────────────────────
BG_DARK = "#0f0f1a"
BG_PANEL = "#1a1a2e"
BG_TEXT = "#16213e"
ACCENT = "#4cc9f0"
ACCENT_DIM = "#1d6fa4"
FG_WHITE = "#f0f0f0"
FG_MUTED = "#8888aa"
BTN_CLOSE = "#e94560"
BTN_COPY = "#2d6a4f"


class ResponseWindow:
    """Floating always-on-top window that shows AI responses."""

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._top: tk.Toplevel | None = None
        self._text: tk.Text | None = None
        self._status: tk.Label | None = None

    # ── Public API ─────────────────────────────────────────────────────────────

    def show_loading(self) -> None:
        """Create (or reset) the window and show a loading indicator."""
        self._destroy_existing()
        self._build()
        self._set_status("Analyzing screenshot…", color=ACCENT)

    def show_response(self, text: str) -> None:
        """Replace loading indicator with the AI response."""
        if self._top is None:
            return
        self._set_status("")
        self._write(text)

    def show_error(self, message: str) -> None:
        if self._top is None:
            return
        self._set_status(f"Error: {message}", color=BTN_CLOSE)
        self._write("")

    # ── Internal ───────────────────────────────────────────────────────────────

    def _destroy_existing(self) -> None:
        if self._top is not None:
            with contextlib.suppress(tk.TclError):
                self._top.destroy()
            self._top = None

    def _build(self) -> None:
        top = tk.Toplevel(self._root)
        top.title("SnapSolve")
        top.attributes("-topmost", True)
        top.configure(bg=BG_DARK)
        top.resizable(True, True)

        # Center on screen
        w, h = 560, 420
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()
        top.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        # ── Status line ───────────────────────────────────────────────────────
        self._status = tk.Label(
            top,
            text="",
            bg=BG_DARK,
            fg=ACCENT,
            font=("Helvetica", 9),
            anchor="w",
            padx=12,
            pady=6,
        )
        self._status.pack(side=tk.TOP, fill=tk.X)

        # ── Bottom buttons ────────────────────────────────────────────────────
        # Pack BEFORE the text area with side=BOTTOM so the buttons reserve
        # their space first and never get pushed off-screen by the expanding text.
        btn_bar = tk.Frame(top, bg=BG_DARK, pady=10)
        btn_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10)

        self._make_button(
            btn_bar,
            text="Copy",
            bg=BTN_COPY,
            hover_bg="#1b4332",
            command=self._copy_to_clipboard,
        ).pack(side=tk.LEFT)

        self._make_button(
            btn_bar,
            text="Close",
            bg=BTN_CLOSE,
            hover_bg="#b5153e",
            command=self._close,
        ).pack(side=tk.RIGHT)

        # ── Scrollable text area (fills remaining space) ──────────────────────
        frame = tk.Frame(top, bg=BG_DARK, padx=10, pady=4)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(frame, troughcolor=BG_DARK, bg=BG_PANEL)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        body_font = tkfont.Font(family="Helvetica", size=11)
        self._text = tk.Text(
            frame,
            bg=BG_TEXT,
            fg=FG_WHITE,
            font=body_font,
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=10,
            yscrollcommand=sb.set,
            state=tk.DISABLED,
            insertbackground=ACCENT,
            selectbackground=ACCENT_DIM,
        )
        self._text.pack(fill=tk.BOTH, expand=True)
        sb.config(command=self._text.yview)

        top.bind("<Escape>", lambda _: self._close())
        top.protocol("WM_DELETE_WINDOW", self._close)

        self._top = top

    def _make_button(
        self, parent: tk.Widget, text: str, bg: str, hover_bg: str, command: Any
    ) -> tk.Frame:
        """Frame+Label fake button — tk.Button ignores bg on macOS, this doesn't."""
        btn_font = tkfont.Font(family="Helvetica", size=11, weight="bold")
        frame = tk.Frame(parent, bg=bg, padx=18, pady=8, cursor="hand2")
        label = tk.Label(frame, text=text, bg=bg, fg=FG_WHITE, font=btn_font, cursor="hand2")
        label.pack()

        def on_enter(_: tk.Event) -> None:
            frame.config(bg=hover_bg)
            label.config(bg=hover_bg)

        def on_leave(_: tk.Event) -> None:
            frame.config(bg=bg)
            label.config(bg=bg)

        def on_click(_: tk.Event) -> None:
            command()

        for w in (frame, label):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)
        return frame

    def _set_status(self, text: str, color: str = FG_MUTED) -> None:
        if self._status:
            self._status.config(text=text, fg=color)

    def _write(self, text: str) -> None:
        if self._text is None:
            return
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        if text:
            self._text.insert(tk.END, text)
        self._text.config(state=tk.DISABLED)

    def _copy_to_clipboard(self) -> None:
        if self._text is None:
            return
        try:
            import pyperclip

            content = self._text.get("1.0", tk.END).strip()
            pyperclip.copy(content)
            self._set_status("Copied to clipboard!", color=ACCENT)
            if self._top:
                self._top.after(1500, lambda: self._set_status(""))
        except Exception as exc:
            self._set_status(f"Copy failed: {exc}", color=BTN_CLOSE)

    def _close(self) -> None:
        self._destroy_existing()
