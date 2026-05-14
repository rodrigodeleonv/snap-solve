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

        # ── Header bar ────────────────────────────────────────────────────────
        header = tk.Frame(top, bg=BG_PANEL, pady=8)
        header.pack(fill=tk.X)

        logo_font = tkfont.Font(family="Helvetica", size=13, weight="bold")
        tk.Label(header, text="  SnapSolve", font=logo_font, bg=BG_PANEL, fg=ACCENT).pack(
            side=tk.LEFT
        )

        tk.Button(
            header,
            text="✕",
            bg=BG_PANEL,
            fg=FG_MUTED,
            activebackground=BTN_CLOSE,
            activeforeground=FG_WHITE,
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=4,
            command=self._close,
        ).pack(side=tk.RIGHT)

        # ── Status line ───────────────────────────────────────────────────────
        self._status = tk.Label(
            top, text="", bg=BG_DARK, fg=ACCENT, font=("Helvetica", 9), anchor="w", padx=12
        )
        self._status.pack(fill=tk.X)

        # ── Scrollable text area ───────────────────────────────────────────────
        frame = tk.Frame(top, bg=BG_DARK, padx=10, pady=4)
        frame.pack(fill=tk.BOTH, expand=True)

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

        # ── Bottom buttons ────────────────────────────────────────────────────
        btn_bar = tk.Frame(top, bg=BG_DARK, pady=8)
        btn_bar.pack(fill=tk.X, padx=10)

        btn_style: dict[str, Any] = dict(
            relief=tk.FLAT, bd=0, padx=16, pady=6, font=("Helvetica", 10, "bold"), cursor="hand2"
        )

        tk.Button(
            btn_bar,
            text="Copy",
            bg=BTN_COPY,
            fg=FG_WHITE,
            activebackground="#1b4332",
            command=self._copy_to_clipboard,
            **btn_style,
        ).pack(side=tk.LEFT)

        tk.Button(
            btn_bar,
            text="Close",
            bg=BTN_CLOSE,
            fg=FG_WHITE,
            activebackground="#b5153e",
            command=self._close,
            **btn_style,
        ).pack(side=tk.RIGHT)

        top.bind("<Escape>", lambda _: self._close())
        top.protocol("WM_DELETE_WINDOW", self._close)

        # Make window draggable by header
        self._make_draggable(header)

        self._top = top

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

    def _make_draggable(self, widget: tk.Widget) -> None:
        widget.bind("<ButtonPress-1>", self._drag_start)
        widget.bind("<B1-Motion>", self._drag_move)

    def _drag_start(self, event: tk.Event) -> None:
        self._drag_x = event.x_root - (self._top.winfo_x() if self._top else 0)
        self._drag_y = event.y_root - (self._top.winfo_y() if self._top else 0)

    def _drag_move(self, event: tk.Event) -> None:
        if self._top:
            x = event.x_root - self._drag_x
            y = event.y_root - self._drag_y
            self._top.geometry(f"+{x}+{y}")
