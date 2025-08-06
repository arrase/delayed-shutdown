#!/bin/bash
set -e

echo "This script creates a desktop entry for Delayed Shutdown."
echo "It assumes the application was installed using pipx."

# Check if pipx is installed
if ! command -v pipx &> /dev/null; then
    echo "Error: pipx is not installed or not in the PATH."
    echo "Please install pipx to continue."
    exit 1
fi

echo "Searching for 'delayed-shutdown' installation with pipx..."

# Use the JSON output of pipx list for greater robustness
PIPX_JSON=$(pipx list --json)

# Use a Python script to safely parse the JSON and extract the venv path
GET_VENV_PATH_PY='''
import sys, json, os
try:
    data = json.load(sys.stdin)
    venvs = data.get("venvs", {})
    app_data = venvs.get("delayed-shutdown")
    if not app_data:
        sys.exit(1) # App not found

    main_package = app_data.get("metadata", {}).get("main_package", {})
    app_paths = main_package.get("app_paths", [])
    if not app_paths:
        sys.exit(1) # No app_paths found

    app_path = app_paths[0].get("__Path__")
    if not app_path:
        sys.exit(1) # No __Path__ found

    # The venv path is two levels above the executable path (e.g., /path/to/venv/bin/app)
    venv_path = os.path.dirname(os.path.dirname(app_path))
    print(venv_path)
    sys.exit(0)
except (KeyError, IndexError, json.JSONDecodeError):
    sys.exit(1)
'''

VENV_PATH=$(echo "$PIPX_JSON" | python3 -c "$GET_VENV_PATH_PY")

if [ -z "$VENV_PATH" ]; then
    echo "Error: Could not find 'delayed-shutdown' installed via pipx, or its path could not be determined."
    echo "Make sure it is installed with: pipx install git+https://github.com/arrase/delayed-shutdown.git"
    exit 1
fi

echo "Virtual environment path found: $VENV_PATH"

# Locate the main executable
EXECUTABLE_PATH=$(which delayed-shutdown)
if [ -z "$EXECUTABLE_PATH" ]; then
    echo "Error: Could not find the 'delayed-shutdown' executable in the PATH."
    exit 1
fi

echo "Executable found at: $EXECUTABLE_PATH"

# Find the package path within the venv
PACKAGE_PATH=$(find "$VENV_PATH" -type d -name "delayed_shutdown" | head -n 1)
if [ -z "$PACKAGE_PATH" ]; then
    echo "Error: Could not find the 'delayed_shutdown' package directory inside $VENV_PATH."
    exit 1
fi

ICON_PATH="$PACKAGE_PATH/ui/images/icon.png"
if [ ! -f "$ICON_PATH" ]; then
    echo "Error: Could not find the icon at the expected path: $ICON_PATH"
    exit 1
fi

echo "Icon found at: $ICON_PATH"

# Create the content of the .desktop file
DESKTOP_ENTRY="[Desktop Entry]
Version=1.0
Type=Application
Name=Delayed Shutdown
Comment=Shutdown computer after specified processes finish
Exec=$EXECUTABLE_PATH
Icon=$ICON_PATH
Terminal=false
Categories=System;Utility;
"

# Create the directory and the .desktop file
APP_DIR="$HOME/.local/share/applications"
mkdir -p "$APP_DIR"
DESKTOP_FILE_PATH="$APP_DIR/delayed-shutdown.desktop"

echo "Creating the .desktop file at: $DESKTOP_FILE_PATH"
echo -e "$DESKTOP_ENTRY" > "$DESKTOP_FILE_PATH"

chmod +x "$DESKTOP_FILE_PATH"

echo "Desktop entry created successfully!"
echo "You may need to restart your session for it to appear in the applications menu."
