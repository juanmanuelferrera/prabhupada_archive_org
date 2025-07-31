#!/bin/bash

# Lanzador inteligente para Archive.org Uploader GUI
# ================================================

echo "🚀 Iniciando Archive.org Uploader GUI (modo inteligente)..."

# Función para probar si una versión de Python tiene tkinter
test_python_tkinter() {
    local python_cmd="$1"
    if $python_cmd -c "import tkinter; print('OK')" 2>/dev/null | grep -q "OK"; then
        return 0
    else
        return 1
fi
}

# Probar diferentes versiones de Python
PYTHON_VERSIONS=(
    "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
    "python3"
    "python3.11"
    "python3.10"
    "python3.9"
    "/opt/homebrew/bin/python3"
)

PYTHON_CMD=""

echo "🔍 Buscando versión de Python con tkinter..."

for python_version in "${PYTHON_VERSIONS[@]}"; do
    if command -v "$python_version" &> /dev/null; then
        echo "  Probando: $python_version"
        if test_python_tkinter "$python_version"; then
            PYTHON_CMD="$python_version"
            echo "✅ Encontrada versión compatible: $python_version"
            break
        else
            echo "  ❌ No tiene tkinter"
        fi
    else
        echo "  ⚠️  No encontrada: $python_version"
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ No se encontró ninguna versión de Python con tkinter"
    echo ""
    echo "🔧 Soluciones:"
    echo "1. Instalar tkinter para Python:"
    echo "   brew install python-tk"
    echo ""
    echo "2. Usar la versión de Python del sistema:"
    echo "   /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 archive_uploader_gui.py"
    echo ""
    echo "3. Instalar Python desde python.org (incluye tkinter)"
    exit 1
fi

# Verificar que el archivo GUI existe
if [ ! -f "archive_uploader_gui.py" ]; then
    echo "❌ No se encontró archive_uploader_gui.py"
    echo "Asegúrate de estar en el directorio correcto"
    exit 1
fi

# Verificar que el uploader principal existe
if [ ! -f "archive_uploader.py" ]; then
    echo "❌ No se encontró archive_uploader.py"
    echo "Asegúrate de que todos los archivos estén presentes"
    exit 1
fi

echo "✅ Iniciando interfaz gráfica con: $PYTHON_CMD"
$PYTHON_CMD archive_uploader_gui.py 