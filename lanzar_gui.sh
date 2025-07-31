#!/bin/bash

# Lanzador para Archive.org Uploader GUI
# =====================================

echo "🚀 Iniciando Archive.org Uploader GUI..."

# Verificar que Python esté disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "Instala Python 3 desde: https://python.org"
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

echo "✅ Iniciando interfaz gráfica..."
# Usar la versión específica de Python que tiene tkinter
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3 archive_uploader_gui.py 