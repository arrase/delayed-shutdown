#!/bin/bash
set -e

echo "Buscando el ejecutable de delayed-shutdown..."
# Localizar el ejecutable principal
EXECUTABLE_PATH=$(which delayed-shutdown)

if [ -z "$EXECUTABLE_PATH" ]; then
    echo "Error: No se pudo encontrar el ejecutable 'delayed-shutdown' en el PATH."
    echo "Asegúrate de que la aplicación está instalada y de que su ubicación está en el PATH."
    exit 1
fi

echo "Ejecutable encontrado en: $EXECUTABLE_PATH"
echo "Buscando la ruta de instalación del paquete..."

# Usar Python para encontrar la ruta del paquete. Esto funciona para pip y pipx.
PACKAGE_PATH=$(python3 -c "import delayed_shutdown; import os; print(os.path.dirname(delayed_shutdown.__file__))")

if [ -z "$PACKAGE_PATH" ]; then
    echo "Error: No se pudo determinar la ruta del paquete 'delayed_shutdown'."
    exit 1
fi

ICON_PATH="$PACKAGE_PATH/ui/images/icon.png"

if [ ! -f "$ICON_PATH" ]; then
    echo "Error: No se pudo encontrar el icono en la ruta esperada: $ICON_PATH"
    exit 1
fi

echo "Icono encontrado en: $ICON_PATH"

# Crear el contenido del fichero .desktop
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

# Crear el directorio y el fichero .desktop
APP_DIR="$HOME/.local/share/applications"
mkdir -p "$APP_DIR"

DESKTOP_FILE_PATH="$APP_DIR/delayed-shutdown.desktop"

echo "Creando el fichero .desktop en: $DESKTOP_FILE_PATH"
echo "$DESKTOP_ENTRY" > "$DESKTOP_FILE_PATH"

# Darle permisos de ejecución por si acaso (aunque no es estrictamente necesario para .desktop)
chmod +x "$DESKTOP_FILE_PATH"

echo "¡Entrada de escritorio creada con éxito!"
echo "Puede que necesites reiniciar tu sesión para que aparezca en el menú de aplicaciones."
