#!/bin/bash
set -e

# Create the content of the .desktop file
DESKTOP_ENTRY="[Desktop Entry]
Name=delayed-shutdown
Comment=Starts the delayed-shutdown application
Exec=$HOME/.local/bin/delayed-shutdown
Icon=
Terminal=false
Type=Application
Path=$HOME/.local/bin/
"

# Create the directory and the .desktop file
APP_DIR="$HOME/.config/autostart"
mkdir -p "$APP_DIR"
DESKTOP_FILE_PATH="$APP_DIR/delayed-shutdown.desktop"

echo "Creating the .desktop file at: $DESKTOP_FILE_PATH"
echo -e "$DESKTOP_ENTRY" > "$DESKTOP_FILE_PATH"

echo "Desktop entry created successfully!"
echo "You may need to restart your session for it to appear in the applications menu."
