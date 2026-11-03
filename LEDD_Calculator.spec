"""PyInstaller recipe for Windows executables and macOS app bundles."""

import sys

from PyInstaller.utils.hooks import collect_all


# Streamlit discovers components dynamically, so include its data, binaries, and
# hidden imports rather than relying only on static import analysis.
streamlit_datas, streamlit_bins, streamlit_hidden = collect_all("streamlit")

# Analyze the desktop launcher and bundle the UI plus medication catalogue as
# runtime data files. The Agg backend avoids GUI-framework dependencies.
a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=streamlit_bins,
    datas=streamlit_datas + [
        ("app.py", "."),
        ("config_Switzerland.json", "."),
    ],
    hiddenimports=streamlit_hidden + [
        "pandas",
        "fpdf",
        "matplotlib.pyplot",
        "matplotlib.backends.backend_agg",
        "ledd_calculator.core",
        "ledd_calculator.shutdown",
    ],
    hookspath=[],
    hooksconfig={"matplotlib": {"backends": ["Agg"]}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
# Package pure Python modules into PyInstaller's embedded archive.
pyz = PYZ(a.pure)

# Build a windowed executable. ``exclude_binaries`` creates an onedir layout,
# which avoids extracting the entire scientific stack on every launch.
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="LEDD Calculator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
# Place the executable, native libraries, and resources in one distributable
# directory; Inno Setup later turns this directory into a Windows installer.
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="LEDD Calculator",
)
# macOS requires the collected directory to be wrapped in a standard .app bundle.
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="LEDD Calculator.app",
        icon=None,
        bundle_identifier="ch.supsi.ledd.calculator",
        info_plist={"LSMinimumSystemVersion": "12.0"},
    )
