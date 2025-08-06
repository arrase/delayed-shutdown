#!/bin/bash
set -e

echo "Este script crea una entrada de escritorio para Delayed Shutdown."
echo "Asume que la aplicación fue instalada usando pipx."

# Verificar si pipx está instalado
if ! command -v pipx &> /dev/null; then
    echo "Error: pipx no está instalado o no se encuentra en el PATH."
    echo "Por favor, instala pipx para continuar."
    exit 1
fi

echo "Buscando la instalación de 'delayed-shutdown' con pipx..."

# Usar la salida JSON de pipx list para mayor robustez
PIPX_JSON=$(pipx list --json)

# Usar un script de Python para analizar el JSON de forma segura y extraer la ruta del venv
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

    # La ruta del venv es dos niveles por encima de la ruta del ejecutable (p. ej., /ruta/al/venv/bin/app)
    venv_path = os.path.dirname(os.path.dirname(app_path))
    print(venv_path)
    sys.exit(0)
except (KeyError, IndexError, json.JSONDecodeError):
    sys.exit(1)
'''

VENV_PATH=$(echo "$PIPX_JSON" | python3 -c "$GET_VENV_PATH_PY")

if [ -z "$VENV_PATH" ]; then
    echo "Error: No se pudo encontrar 'delayed-shutdown' instalado a través de pipx, o no se pudo determinar su ruta."
    echo "Asegúrate de que está instalado con: pipx install git+https://github.com/arrase/delayed-shutdown.git"
    exit 1
fi

echo "Ruta del entorno virtual encontrada: $VENV_PATH"

# Localizar el ejecutable principal
EXECUTABLE_PATH=$(which delayed-shutdown)
if [ -z "$EXECUTABLE_PATH" ]; then
    echo "Error: No se pudo encontrar el ejecutable 'delayed-shutdown' en el PATH."
    exit 1
fi

echo "Ejecutable encontrado en: $EXECUTABLE_PATH"

# Encontrar la ruta del paquete dentro del venv
PACKAGE_PATH=$(find "$VENV_PATH" -type d -name "delayed_shutdown" | head -n 1)
if [ -z "$PACKAGE_PATH" ]; then
    echo "Error: No se pudo encontrar el directorio del paquete 'delayed_shutdown' dentro de $VENV_PATH."
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
echo -e "$DESKTOP_ENTRY" > "$DESKTOP_FILE_PATH"

chmod +x "$DESKTOP_FILE_PATH"

echo "¡Entrada de escritorio creada con éxito!"
echo "Puede que necesites reiniciar tu sesión para que aparezca en el menú de aplicaciones."
