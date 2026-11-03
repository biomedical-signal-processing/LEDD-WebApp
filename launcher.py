"""Desktop entry point for the packaged LEDD Calculator.

The launcher starts Streamlit on the loopback interface and opens the user's
default browser. It is kept separate from ``app.py`` so PyInstaller has a normal
blocking command-line entry point to package.
"""

from __future__ import annotations

import argparse
import os
import socket
import threading
import time
import webbrowser

from streamlit.web import bootstrap

from ledd_calculator.paths import resource_path


def available_port() -> int:
    """Ask Windows/macOS for an unused local TCP port and return its number."""
    # Binding to port zero lets the operating system select an available port.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def open_browser(port: int) -> None:
    """Open the local application after giving Streamlit time to start."""
    time.sleep(1.4)
    webbrowser.open(f"http://127.0.0.1:{port}")


def main() -> None:
    """Parse launch options and run the embedded Streamlit server."""
    parser = argparse.ArgumentParser(description="Run LEDD Calculator locally.")
    parser.add_argument("--port", type=int, help="Local port; defaults to a free port.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser.")
    args = parser.parse_args()

    # Command-line arguments take precedence over environment configuration.
    configured_port = args.port or os.environ.get("LEDD_PORT")
    port = int(configured_port) if configured_port else available_port()
    if not 1 <= port <= 65535:
        parser.error("--port must be between 1 and 65535")

    # Browser startup happens on a daemon thread so it does not block the server.
    if not args.no_browser and os.environ.get("LEDD_NO_BROWSER") != "1":
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # Limit the server to this computer. In particular, 127.0.0.1 prevents the
    # calculator from being exposed to other devices on the local network.
    options = {
        "global_developmentMode": False,
        "server_address": "127.0.0.1",
        "server_port": port,
        "server_headless": True,
        "browser_gatherUsageStats": False,
        "client_showErrorDetails": True,
    }
    # Run the bundled app through Streamlit's supported bootstrap layer.
    bootstrap.load_config_options(options)
    bootstrap.run(str(resource_path("app.py")), False, [], options)


if __name__ == "__main__":
    main()
