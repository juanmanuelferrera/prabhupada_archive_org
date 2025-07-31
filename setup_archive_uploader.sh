#!/bin/bash

# Script de instalación para Archive.org Uploader
# ==============================================

echo "🚀 Configurando Archive.org Uploader..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "Instala Python 3 desde: https://python.org"
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Instalar dependencias
echo "📦 Instalando dependencias..."

pip3 install internetarchive requests

if [ $? -eq 0 ]; then
    echo "✅ Dependencias instaladas correctamente"
else
    echo "❌ Error instalando dependencias"
    exit 1
fi

# Hacer el script ejecutable
chmod +x archive_uploader.py

echo ""
echo "🎉 Instalación completada!"
echo ""
echo "📖 Uso:"
echo "  python3 archive_uploader.py /ruta/a/material \"Nombre del Autor\""
echo ""
echo "📋 Ejemplos:"
echo "  python3 archive_uploader.py ~/Documents/libros \"Carlos Fuentes\""
echo "  python3 archive_uploader.py ~/Videos/conferencias \"Eduardo Galeano\" --collection opensource"
echo ""
echo "📁 El script creará:"
echo "  - .archive_progress.json (progreso guardado)"
echo "  - .archive_upload.log (registro de actividades)"
echo ""
echo "🔧 Para configurar credenciales de Archive.org:"
echo "  ia configure" 