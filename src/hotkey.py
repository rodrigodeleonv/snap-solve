import logging
import threading
from collections.abc import Callable

from pynput import keyboard

log = logging.getLogger("snapsolve.hotkey")


class HotkeyListener:
    """Listens for a global keyboard shortcut and fires a callback."""

    def __init__(self, hotkey: str, callback: Callable[[], None]) -> None:
        self._hotkey = hotkey
        self._callback = callback
        self._thread: threading.Thread | None = None
        self._listener: keyboard.GlobalHotKeys | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()

    def _run(self) -> None:
        log.info("Listening on hotkey: %s", self._hotkey)
        self._listener = keyboard.GlobalHotKeys({self._hotkey: self._on_activate})
        with self._listener:
            self._listener.join()

    def _on_activate(self) -> None:
        # pynput fires this in its own thread — safe to call callback directly
        self._callback()
