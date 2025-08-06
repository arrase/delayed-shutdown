#!/bin/bash

# Install the package
pip install .

# Get the executable path
EXE_PATH=$(which delayed-shutdown)

# Get the icon path
ICON_NAME=icon.png
SITE_PACKAGES=$(python -c 'import site; print(site.getsitepackages()[0])')
ICON_PATH=$SITE_PACKAGES/delayed_shutdown/ui/images/$ICON_NAME

# Create the .desktop file
APPLICATIONS_DIR=~/.local/share/applications
mkdir -p $APPLICATIONS_DIR
DESKTOP_FILE=$APPLICATIONS_DIR/delayed-shutdown.desktop
echo "[Desktop Entry]
Version=1.0
Type=Application
Name=Delayed Shutdown
Comment=Shutdown computer after specified processes finish
Exec=$EXE_PATH
Icon=$ICON_PATH
Terminal=false
Categories=System;Utility;
" > $DESKTOP_FILE

echo "Installation complete. You can find 'Delayed Shutdown' in your applications menu."
