import base64
import io

import mss
from PIL import Image


def capture_screen(monitor: int = 1) -> bytes:
    """Capture the primary monitor and return raw PNG bytes."""
    with mss.mss() as sct:
        # monitor 0 = all monitors combined; 1 = primary
        mon = sct.monitors[monitor]
        raw = sct.grab(mon)
        img = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()


def to_base64(png_bytes: bytes) -> str:
    return base64.standard_b64encode(png_bytes).decode("utf-8")
