#!/bin/zsh
# Local macOS release builder. Exit on errors or undefined variables.
set -eu

# Resolve the repository independently of the directory used to invoke the script.
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd -P)"
cd "$SCRIPT_DIR"

# Accept an optional output directory and keep build dependencies isolated.
OUTPUT_DIRECTORY="${1:-releases}"
VENV_PATH="$SCRIPT_DIR/.venv"
if [ ! -x "$VENV_PATH/bin/python" ]; then
  python3 -m venv "$VENV_PATH"
fi
"$VENV_PATH/bin/python" -m pip install --upgrade pip
"$VENV_PATH/bin/python" -m pip install -r requirements-build.txt

# Remove only generated staging directories before making a reproducible build.
WORK_PATH="$SCRIPT_DIR/.build/macos"
DIST_PATH="$SCRIPT_DIR/dist"
rm -rf -- "$WORK_PATH" "$DIST_PATH"
mkdir -p "$WORK_PATH" "$DIST_PATH" "$OUTPUT_DIRECTORY"
"$VENV_PATH/bin/python" -m PyInstaller --noconfirm --clean --workpath "$WORK_PATH" --distpath "$DIST_PATH" LEDD_Calculator.spec

# Clear inherited quarantine metadata and apply an ad-hoc signature. Distribution
# outside the App Store may still show Gatekeeper warnings without notarization.
xattr -cr "$DIST_PATH/LEDD Calculator.app"
codesign --force --deep --sign - "$DIST_PATH/LEDD Calculator.app"

# Include the hardware architecture in the DMG name because Intel and Apple
# Silicon builds contain different native Python binaries.
ARCHITECTURE="$(uname -m)"
DMG_PATH="$OUTPUT_DIRECTORY/LEDD-Calculator-macOS-$ARCHITECTURE.dmg"
rm -f -- "$DMG_PATH"
hdiutil create -volname "LEDD Calculator" -srcfolder "$DIST_PATH/LEDD Calculator.app" -ov -format UDZO "$DMG_PATH"
echo "Created $DMG_PATH"
