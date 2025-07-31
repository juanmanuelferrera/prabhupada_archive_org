# Archive.org Uploader para Material de Autor

Script automatizado para subir libros, videos y material audiovisual de un autor específico a Archive.org.

**🎉 ¡NUEVO! Interfaz gráfica incluida para uso más fácil.**

## 🚀 Características

- **Subida automatizada** de múltiples tipos de archivos
- **Metadatos automáticos** basados en el autor y tipo de archivo
- **Sistema de progreso** que permite reanudar interrupciones
- **Logging detallado** para seguimiento de errores
- **Soporte para múltiples formatos**: PDF, EPUB, MP3, MP4, etc.

## 📦 Instalación

### 1. Clonar o descargar los archivos
```bash
# Si tienes git
git clone <url-del-repositorio>
cd archive-uploader

# O descargar manualmente los archivos
```

### 2. Ejecutar el script de instalación
```bash
chmod +x setup_archive_uploader.sh
./setup_archive_uploader.sh
```

### 3. Configurar credenciales de Archive.org
```bash
ia configure
```
Sigue las instrucciones para configurar tu cuenta de Archive.org.

## 🖥️ Interfaz Gráfica (GUI)

### Lanzar la GUI:
```bash
# Opción 1: Script de lanzamiento
./lanzar_gui.sh

# Opción 2: Directamente con Python
python3 archive_uploader_gui.py
```

### Características de la GUI:
- **Interfaz intuitiva** con botones y menús
- **Selección visual** de directorios
- **Lista de archivos** con información detallada
- **Barra de progreso** en tiempo real
- **Registro de actividad** integrado
- **Botones de control** (Iniciar, Detener, Ayuda)

## 📖 Uso Básico

```bash
python3 archive_uploader.py /ruta/a/material "Nombre del Autor"
```

### Ejemplos

```bash
# Subir libros de un autor
python3 archive_uploader.py ~/Documents/libros "Carlos Fuentes"

# Subir videos de conferencias
python3 archive_uploader.py ~/Videos/conferencias "Eduardo Galeano"

# Subir material a una colección específica
python3 archive_uploader.py ~/Audio/podcasts "Gabriel García Márquez" --collection opensource
```

## 🔧 Opciones Avanzadas

### Argumentos del script

- `directory`: Directorio con el material a subir
- `author`: Nombre del autor
- `--collection`: Colección en Archive.org (default: opensource)
- `--resume`: Reanudar desde el último archivo procesado

### Formatos Soportados

**Libros:**
- PDF, EPUB, MOBI, TXT, DOC, DOCX

**Audio:**
- MP3, WAV, FLAC, M4A, OGG

**Video:**
- MP4, AVI, MKV, MOV, WEBM

**Imágenes:**
- JPG, JPEG, PNG, GIF, TIFF

## 📁 Estructura de Archivos

### Archivos del Sistema:
- `archive_uploader.py` - Script principal (línea de comandos)
- `archive_uploader_gui.py` - Interfaz gráfica
- `setup_archive_uploader.sh` - Script de instalación
- `lanzar_gui.sh` - Lanzador de la GUI
- `README.md` - Documentación

### Archivos Creados Automáticamente:
- `.archive_progress.json`: Progreso guardado (permite reanudar)
- `.archive_upload.log`: Registro detallado de actividades

## 🎯 Metadatos Automáticos

El script genera automáticamente:

- **Título**: Basado en el nombre del archivo
- **Autor**: El nombre especificado
- **Fecha**: Fecha actual
- **Licencia**: Creative Commons BY-SA 4.0
- **Idioma**: Español (configurable)
- **Tipo de medio**: Detectado automáticamente

### Ejemplo de metadatos generados:

```json
{
  "title": "El Laberinto De La Soledad",
  "creator": "Octavio Paz",
  "collection": "opensource",
  "mediatype": "texts",
  "language": "es",
  "licenseurl": "https://creativecommons.org/licenses/by-sa/4.0/",
  "date": "2025-01-15",
  "description": "Material de Octavio Paz: El Laberinto De La Soledad",
  "subject": ["Octavio Paz", "books", "opensource"]
}
```

## 🔄 Reanudar Proceso Interrumpido

Si el proceso se interrumpe, puedes reanudarlo:

```bash
python3 archive_uploader.py /ruta/a/material "Nombre del Autor" --resume
```

El script detectará automáticamente los archivos ya subidos y continuará desde donde se quedó.

## 📊 Monitoreo del Progreso

### Ver progreso en tiempo real:
```bash
tail -f .archive_upload.log
```

### Ver archivos ya procesados:
```bash
cat .archive_progress.json | jq '.'
```

## ⚠️ Consideraciones Importantes

### Límites de Archive.org
- **Tamaño máximo por archivo**: 100GB
- **Límite de velocidad**: Respeta los límites de la API
- **Cuota diaria**: Verifica los límites de tu cuenta

### Organización de Archivos
- **Nombres descriptivos**: Los nombres de archivo se usan para generar títulos
- **Estructura de carpetas**: El script procesa recursivamente subdirectorios
- **Evitar caracteres especiales**: Usa nombres simples para mejores resultados

### Metadatos Personalizados
Para personalizar metadatos, edita la función `generate_metadata()` en el script:

```python
def generate_metadata(self, file_path: Path, mediatype: str) -> Dict:
    # Personalizar aquí los metadatos
    metadata = {
        'title': file_path.stem.replace('_', ' ').title(),
        'creator': self.author_name,
        'collection': self.collection,
        # Agregar campos personalizados aquí
        'custom_field': 'valor_personalizado'
    }
    return metadata
```

## 🐛 Solución de Problemas

### Error: "internetarchive library not found"
```bash
pip3 install internetarchive
```

### Error: "requests library not found"
```bash
pip3 install requests
```

### Error de autenticación
```bash
ia configure
```

### Error de permisos
```bash
chmod +x archive_uploader.py
```

### Archivo muy grande
- Verifica que el archivo no exceda 100GB
- Considera dividir archivos grandes

## 📈 Comparación con el Script Original

| Característica | Script Original | Este Script |
|----------------|-----------------|-------------|
| Complejidad | Alta (YouTube + Markdown) | Media (Archivos locales) |
| Configuración | Compleja | Simple |
| Metadatos | Desde Markdown | Automáticos |
| Progreso | JSONL | JSON |
| Logging | Avanzado | Básico |
| Uso | Específico | General |

## 🤝 Contribuciones

Para mejorar el script:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este script está bajo la licencia MIT. Ver archivo LICENSE para detalles.

## 🙏 Agradecimientos

- Basado en el trabajo de Amin Bandali
- Utiliza la librería `internetarchive` de Archive.org
- Inspirado en el script de Protesilaos Stavrou

---

**Nota**: Este script es para uso educativo y de preservación. Asegúrate de tener los derechos necesarios para subir el material a Archive.org. 