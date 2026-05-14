"""
App orchestration: ties together hotkey → screenshot → AI → UI.

Thread model
────────────
  Main thread   : tkinter event loop (required by tkinter on all platforms)
  Hotkey thread : pynput GlobalHotKeys listener (daemon)
  Worker thread : screenshot + API call per trigger (daemon)

UI updates are always scheduled on the main thread via root.after(0, fn).
"""

import threading
import tkinter as tk

from .ai_client import analyze
from .config import config
from .hotkey import HotkeyListener
from .screenshot import capture_screen
from .ui import ResponseWindow


class App:
    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.withdraw()  # hidden host window — event loop only
        self._window = ResponseWindow(self._root)
        self._lock = threading.Lock()  # prevents overlapping captures
        self._busy = False

    def run(self) -> None:
        config.validate()

        listener = HotkeyListener(
            hotkey=config.HOTKEY,
            callback=self._on_hotkey,
        )
        listener.start()

        print(f"[SnapSolve] Running. Press {config.HOTKEY} to capture.")
        print("[SnapSolve] Press Ctrl-C in this terminal to quit.")

        try:
            self._root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            listener.stop()

    # ── Hotkey callback (runs in pynput thread) ────────────────────────────────

    def _on_hotkey(self) -> None:
        with self._lock:
            if self._busy:
                return
            self._busy = True

        # Capture screenshot immediately (before the UI window appears,
        # so the window doesn't show up in the screenshot)
        try:
            png = capture_screen()
        except Exception as exc:
            self._root.after(0, lambda e=exc: self._show_error(str(e)))
            with self._lock:
                self._busy = False
            return

        # Show loading window on main thread
        self._root.after(0, self._window.show_loading)

        # Analyze in background
        worker = threading.Thread(
            target=self._analyze_and_display,
            args=(png,),
            daemon=True,
        )
        worker.start()

    # ── Worker (background thread) ─────────────────────────────────────────────

    def _analyze_and_display(self, png: bytes) -> None:
        try:
            response = analyze(png)
            self._root.after(0, lambda: self._window.show_response(response))
        except Exception as exc:
            self._root.after(0, lambda e=exc: self._show_error(str(e)))
        finally:
            with self._lock:
                self._busy = False

    def _show_error(self, message: str) -> None:
        self._window.show_error(message)
