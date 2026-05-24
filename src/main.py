"""
App orchestration: ties together hotkey → screenshot → AI → UI.

Thread model
────────────
  Main thread   : tkinter event loop (required by tkinter on all platforms)
  Hotkey thread : pynput GlobalHotKeys listener (daemon)
  Worker thread : screenshot + API call per trigger (daemon)

UI updates are always scheduled on the main thread via root.after(0, fn).
"""

import logging
import threading
import tkinter as tk

from .ai_client import analyze
from .config import config
from .hotkey import HotkeyListener
from .screenshot import capture_screen
from .ui import ResponseWindow

log = logging.getLogger("snapsolve.main")


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

        log.info("Running. Press %s to capture.", config.HOTKEY)
        log.info("Press Ctrl-C in this terminal to quit.")

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
                log.info("Already processing — ignoring hotkey.")
                return
            self._busy = True

        # Capture screenshot immediately (before the UI window appears,
        # so the window doesn't show up in the screenshot)
        log.info("Taking screenshot...")
        try:
            png = capture_screen()
            log.info("Screenshot captured (%s bytes).", f"{len(png):,}")
        except Exception as exc:
            log.error("Error capturing screenshot: %s", exc)
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
            log.info("Sending screenshot to %s (%s)...", config.provider, config.model)
            response = analyze(png)
            log.info("Response received. Displaying result.")
            self._root.after(0, lambda: self._window.show_response(response))
        except Exception as exc:
            log.error("Error generating response: %s", exc)
            self._root.after(0, lambda e=exc: self._show_error(str(e)))
        finally:
            with self._lock:
                self._busy = False

    def _show_error(self, message: str) -> None:
        log.info("Showing error to user: %s", message)
        self._window.show_error(message)
