#!/usr/bin/env python3

"""
Archive.org Uploader para Material de Autor
===========================================

Script automatizado para subir libros, videos y material audiovisual
de un autor específico a Archive.org.

Uso:
    python archive_uploader.py /ruta/a/material "Nombre del Autor"

Dependencias:
    pip install internetarchive requests
"""

import os
import sys
import json
import argparse
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import internetarchive as ia
except ImportError:
    print('Error: internetarchive library not found')
    print('Instalar con: pip install internetarchive')
    sys.exit(1)

try:
    import requests
except ImportError:
    print('Error: requests library not found')
    print('Instalar con: pip install requests')
    sys.exit(1)

# Configuración
PROGRESS_FILE = '.archive_progress.json'
LOG_FILE = '.archive_upload.log'
SUPPORTED_EXTENSIONS = {
    'books': ['.pdf', '.epub', '.mobi', '.txt', '.doc', '.docx'],
    'audio': ['.mp3', '.wav', '.flac', '.m4a', '.ogg'],
    'video': ['.mp4', '.avi', '.mkv', '.mov', '.webm'],
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.tiff']
}

class ArchiveUploader:
    def __init__(self, author_name: str, collection: str = 'opensource'):
        self.author_name = author_name
        self.collection = collection
        self.progress = self.load_progress()
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_progress(self) -> Dict:
        """Cargar progreso guardado"""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error cargando progreso: {e}")
        return {}
        
    def save_progress(self):
        """Guardar progreso"""
        try:
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error guardando progreso: {e}")
            
    def get_mediatype(self, file_path: Path) -> str:
        """Determinar el tipo de medio basado en la extensión"""
        ext = file_path.suffix.lower()
        
        for mediatype, extensions in SUPPORTED_EXTENSIONS.items():
            if ext in extensions:
                return mediatype
        return 'data'  # Por defecto
        
    def generate_identifier(self, file_path: Path) -> str:
        """Generar identificador único para Archive.org"""
        # Limpiar nombre del archivo - solo caracteres válidos para Archive.org
        clean_name = file_path.stem.lower()
        # Solo permitir letras, números, guiones y guiones bajos
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c in '-_')
        clean_name = clean_name.replace(' ', '-')
        
        # Limpiar autor también
        clean_author = self.author_name.lower()
        clean_author = ''.join(c for c in clean_author if c.isalnum() or c in '-_')
        clean_author = clean_author.replace(' ', '-')
        
        # Agregar autor y timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d')
        identifier = f"{clean_author}-{clean_name}-{timestamp}"
        
        # Asegurar que el identificador cumple con las reglas de Archive.org
        # Máximo 100 caracteres, empezar con alfanumérico
        if len(identifier) > 100:
            identifier = identifier[:100]
        
        return identifier
        
    def generate_metadata(self, file_path: Path, mediatype: str) -> Dict:
        """Generar metadatos para el archivo"""
        title = file_path.stem.replace('_', ' ').title()
        
        metadata = {
            'title': title,
            'creator': self.author_name,
            'collection': self.collection,
            'mediatype': mediatype,
            'language': 'es',  # Cambiar según necesidad
            'licenseurl': 'https://creativecommons.org/licenses/by-sa/4.0/',
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'description': f"Material de {self.author_name}: {title}",
            'subject': [self.author_name, mediatype, 'opensource']
        }
        
        # Metadatos específicos por tipo
        if mediatype == 'books':
            metadata['mediatype'] = 'texts'
        elif mediatype == 'audio':
            metadata['mediatype'] = 'audio'
        elif mediatype == 'video':
            metadata['mediatype'] = 'movies'
        elif mediatype == 'images':
            metadata['mediatype'] = 'image'
            
        return metadata
        
    def upload_file(self, file_path: Path) -> bool:
        """Subir un archivo a Archive.org"""
        file_id = str(file_path)
        
        # Verificar si ya se subió
        if file_id in self.progress and self.progress[file_id].get('status') == 'success':
            self.logger.info(f"Archivo ya subido: {file_path.name}")
            return True
            
        try:
            # Generar identificador y metadatos
            identifier = self.generate_identifier(file_path)
            mediatype = self.get_mediatype(file_path)
            metadata = self.generate_metadata(file_path, mediatype)
            
            self.logger.info(f"Subiendo: {file_path.name} -> {identifier}")
            self.logger.info(f"Colección: {self.collection}")
            
            # Subir archivo
            item = ia.upload(identifier, files=str(file_path), metadata=metadata)
            
            # Verificar respuesta
            if item and len(item) > 0:
                response = item[0]
                if isinstance(response, requests.Response) and response.ok:
                    self.progress[file_id] = {
                        'status': 'success',
                        'identifier': identifier,
                        'date': datetime.datetime.now().isoformat()
                    }
                    self.save_progress()
                    # Mover archivo a carpeta "Uploaded" después de subida exitosa
                    self.move_to_uploaded_folder(file_path)
                    self.logger.info(f"✅ Subido exitosamente: {file_path.name}")
                    return True
                else:
                    self.logger.error(f"❌ Error en respuesta: {response.status_code}")
                    return False
            else:
                self.logger.error(f"❌ No se recibió respuesta válida")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error subiendo {file_path.name}: {e}")
            self.progress[file_id] = {
                'status': 'error',
                'error': str(e),
                'date': datetime.datetime.now().isoformat()
            }
            self.save_progress()
            return False
            
    def scan_directory(self, directory: Path) -> List[Path]:
        """Escanear directorio en busca de archivos soportados"""
        files = []
        all_extensions = []
        for ext_list in SUPPORTED_EXTENSIONS.values():
            all_extensions.extend(ext_list)
            
        for file_path in directory.rglob('*'):
            # Excluir archivos en carpetas "Uploaded"
            if "Uploaded" in file_path.parts:
                continue
                
            if file_path.is_file() and file_path.suffix.lower() in all_extensions:
                files.append(file_path)
                
        return sorted(files)
        
    def move_to_uploaded_folder(self, file_path: Path):
        """Mover archivo a carpeta 'Uploaded' después de subida exitosa"""
        try:
            self.logger.info(f"🔄 Intentando mover archivo: {file_path}")
            
            # Crear carpeta "Uploaded" en el directorio padre del archivo
            uploaded_dir = file_path.parent / "Uploaded"
            self.logger.info(f"📁 Creando carpeta: {uploaded_dir}")
            uploaded_dir.mkdir(exist_ok=True)
            
            # Definir ruta de destino
            destination = uploaded_dir / file_path.name
            self.logger.info(f"🎯 Destino: {destination}")
            
            # Si ya existe un archivo con el mismo nombre, agregar timestamp
            if destination.exists():
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = file_path.stem, timestamp, file_path.suffix
                destination = uploaded_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                self.logger.info(f"🕐 Archivo existe, nuevo destino: {destination}")
            
            # Mover archivo
            import shutil
            self.logger.info(f"📦 Moviendo de {file_path} a {destination}")
            shutil.move(str(file_path), str(destination))
            self.logger.info(f"✅ Movido exitosamente a: {destination}")
            
        except Exception as e:
            self.logger.error(f"❌ Error moviendo archivo a carpeta Uploaded: {e}")
            import traceback
            self.logger.error(f"📋 Traceback: {traceback.format_exc()}")
        
    def process_directory(self, directory: str):
        """Procesar directorio completo"""
        directory_path = Path(directory)
        
        if not directory_path.exists():
            self.logger.error(f"Directorio no existe: {directory}")
            return
            
        self.logger.info(f"Escaneando directorio: {directory}")
        files = self.scan_directory(directory_path)
        
        if not files:
            self.logger.warning("No se encontraron archivos soportados")
            return
            
        self.logger.info(f"Encontrados {len(files)} archivos para procesar")
        
        success_count = 0
        error_count = 0
        
        for i, file_path in enumerate(files, 1):
            self.logger.info(f"Procesando {i}/{len(files)}: {file_path.name}")
            
            if self.upload_file(file_path):
                success_count += 1
            else:
                error_count += 1
                
        self.logger.info(f"Proceso completado:")
        self.logger.info(f"  ✅ Exitosos: {success_count}")
        self.logger.info(f"  ❌ Errores: {error_count}")
        self.logger.info(f"  📁 Total: {len(files)}")

def main():
    parser = argparse.ArgumentParser(
        description="Subir material de autor a Archive.org"
    )
    parser.add_argument(
        'directory',
        help='Directorio con el material a subir'
    )
    parser.add_argument(
        'author',
        help='Nombre del autor'
    )
    parser.add_argument(
        '--collection',
        default='opensource',
        help='Colección en Archive.org (default: opensource)'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Reanudar desde el último archivo procesado'
    )
    
    args = parser.parse_args()
    
    # Crear uploader y procesar
    uploader = ArchiveUploader(args.author, args.collection)
    uploader.process_directory(args.directory)

if __name__ == '__main__':
    main() 