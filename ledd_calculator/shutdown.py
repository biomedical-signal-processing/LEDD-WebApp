"""Process shutdown helper used by the packaged desktop application."""

from __future__ import annotations

import os
import threading
import time


def exit_application(delay_seconds: float = 0.4) -> None:
    """Terminate the local process after Streamlit renders its final response.

    Streamlit owns the main event loop, so a delayed hard exit is the reliable way
    to stop the embedded server after the user presses ``Exit Calculator``.
    """

    def terminate() -> None:
        """Wait for the confirmation message to render, then stop the process."""
        time.sleep(delay_seconds)
        os._exit(0)

    # A daemon thread cannot keep the application alive during normal shutdown.
    threading.Thread(target=terminate, daemon=True).start()
