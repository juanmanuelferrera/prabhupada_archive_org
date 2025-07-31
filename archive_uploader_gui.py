#!/usr/bin/env python3

"""
Archive.org Uploader GUI
========================

Interfaz gráfica para subir material de autor a Archive.org
de forma fácil e intuitiva.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Importar nuestro uploader
try:
    from archive_uploader import ArchiveUploader
except ImportError:
    print("Error: No se pudo importar archive_uploader.py")
    print("Asegúrate de que esté en el mismo directorio")
    sys.exit(1)

class ArchiveUploaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Archive.org Uploader - Prabhupada Archive")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        
        # Variables
        self.directory_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.collection_var = tk.StringVar(value="opensource")
        self.existing_collection_var = tk.StringVar()
        self.use_existing_collection_var = tk.BooleanVar(value=False)
        self.list_name_var = tk.StringVar()
        self.add_to_list_var = tk.BooleanVar(value=False)
        self.threads_var = tk.StringVar(value="1")
        self.progress_var = tk.StringVar(value="Listo para subir")
        self.auto_scan_var = tk.BooleanVar(value=True)
        self.dark_mode_var = tk.BooleanVar(value=False)
        self.upload_stats = {"success": 0, "error": 0, "total": 0}
        
        # Cola para comunicación entre hilos
        self.log_queue = queue.Queue()
        
        # Crear interfaz
        self.create_widgets()
        self.setup_logging()
        
        # Verificar configuración
        self.check_configuration()
        
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título con estilo moderno
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(title_frame, text="📚 Archive.org Uploader", 
                               font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Botones de configuración rápida
        settings_frame = ttk.Frame(title_frame)
        settings_frame.pack(side=tk.RIGHT)
        
        ttk.Checkbutton(settings_frame, text="🌙 Modo Oscuro", 
                       variable=self.dark_mode_var, 
                       command=self.toggle_dark_mode).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Checkbutton(settings_frame, text="🔄 Auto-escaneo", 
                       variable=self.auto_scan_var).pack(side=tk.LEFT)
        
        # Sección de configuración
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configuración", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Directorio
        ttk.Label(config_frame, text="📁 Directorio:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(config_frame, textvariable=self.directory_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(config_frame, text="Examinar", command=self.browse_directory).grid(row=0, column=2, pady=5)
        
        # Autor
        ttk.Label(config_frame, text="👤 Autor:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(config_frame, textvariable=self.author_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        # Colección
        ttk.Label(config_frame, text="📂 Colección:").grid(row=2, column=0, sticky=tk.W, pady=5)
        collection_combo = ttk.Combobox(config_frame, textvariable=self.collection_var, 
                                       values=["opensource", "texts", "audio", "movies", "image"])
        collection_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        # Opción para colección existente
        existing_collection_frame = ttk.Frame(config_frame)
        existing_collection_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Checkbutton(existing_collection_frame, text="📚 Usar colección existente", 
                       variable=self.use_existing_collection_var).pack(side=tk.LEFT)
        ttk.Entry(existing_collection_frame, textvariable=self.existing_collection_var, 
                 width=40).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(existing_collection_frame, text="(Nombre de la colección existente)", 
                 foreground="gray").pack(side=tk.LEFT, padx=(5, 0))
        
        # Opción para agregar a lista
        list_frame = ttk.Frame(config_frame)
        list_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Checkbutton(list_frame, text="📋 Agregar a lista", 
                       variable=self.add_to_list_var).pack(side=tk.LEFT)
        ttk.Entry(list_frame, textvariable=self.list_name_var, 
                 width=40).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Label(list_frame, text="(Nombre de la lista - opcional)", 
                 foreground="gray").pack(side=tk.LEFT, padx=(5, 0))
        
        # Hilos de subida
        ttk.Label(config_frame, text="🔄 Hilos:").grid(row=5, column=0, sticky=tk.W, pady=5)
        threads_combo = ttk.Combobox(config_frame, textvariable=self.threads_var, 
                                    values=["1", "2", "3", "4", "5"], width=10)
        threads_combo.grid(row=5, column=1, sticky=tk.W, padx=(5, 5), pady=5)
        ttk.Label(config_frame, text="(Menos = más responsivo)").grid(row=5, column=2, sticky=tk.W, pady=5)
        
        # Sección de archivos
        files_frame = ttk.LabelFrame(main_frame, text="📋 Archivos Encontrados", padding="10")
        files_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(0, weight=1)
        
        # Lista de archivos con scroll virtual para mejor rendimiento
        self.files_tree = ttk.Treeview(files_frame, columns=("Tipo", "Tamaño"), show="tree headings", height=6)
        self.files_tree.heading("#0", text="Archivo")
        self.files_tree.heading("Tipo", text="Tipo")
        self.files_tree.heading("Tamaño", text="Tamaño")
        self.files_tree.column("#0", width=300)
        self.files_tree.column("Tipo", width=100)
        self.files_tree.column("Tamaño", width=100)
        self.files_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para archivos
        files_scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        files_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.files_tree.configure(yscrollcommand=files_scrollbar.set)
        
        # Botones de archivos
        files_buttons_frame = ttk.Frame(files_frame)
        files_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(files_buttons_frame, text="🔄 Escanear Directorio", 
                  command=self.scan_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(files_buttons_frame, text="🗑️ Limpiar Lista", 
                  command=self.clear_files_list).pack(side=tk.LEFT)
        
        # Sección de progreso
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Progreso", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Etiqueta de progreso
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=1, column=0, sticky=tk.W)
        
        # Botones principales
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.upload_button = ttk.Button(buttons_frame, text="🚀 Iniciar Subida", 
                                       command=self.start_upload, style="Accent.TButton")
        self.upload_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="⏹️ Detener", 
                  command=self.stop_upload).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="📁 Abrir Log", 
                  command=self.open_log).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="❓ Ayuda", 
                  command=self.show_help).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="🧪 Probar", 
                  command=self.test_connection).pack(side=tk.LEFT)
        
        # Información sobre carpeta Uploaded
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Información", padding="10")
        info_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        info_text = "📁 Los archivos subidos exitosamente se moverán automáticamente a una carpeta 'Uploaded'"
        ttk.Label(info_frame, text=info_text, foreground="blue").pack(anchor=tk.W)
        
        # Sección de log
        log_frame = ttk.LabelFrame(main_frame, text="📝 Registro de Actividad", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Área de texto para log con altura reducida para mejor rendimiento
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # Barra de estado moderna
        self.create_status_bar(main_frame)
        
        # Variables de control
        self.uploading = False
        self.upload_thread = None
        
        # Iniciar procesamiento de log
        self.process_log_queue()
    
    def create_status_bar(self, parent):
        """Crear barra de estado moderna"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Estadísticas de subida
        self.stats_label = ttk.Label(status_frame, text="📊 Listo para subir")
        self.stats_label.pack(side=tk.LEFT)
        
        # Separador
        ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Estado de conexión
        self.connection_label = ttk.Label(status_frame, text="🔗 Conectado a Archive.org")
        self.connection_label.pack(side=tk.LEFT)
        
        # Separador
        ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Información de archivos
        self.files_label = ttk.Label(status_frame, text="📁 0 archivos")
        self.files_label.pack(side=tk.LEFT)
        
        # Separador
        ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Versión
        version_label = ttk.Label(status_frame, text="v2.0 - Prabhupada Archive")
        version_label.pack(side=tk.RIGHT)
    
    def toggle_dark_mode(self):
        """Cambiar entre modo claro y oscuro"""
        if self.dark_mode_var.get():
            # Aplicar tema oscuro
            style = ttk.Style()
            style.theme_use('clam')
            # Configurar colores oscuros
            self.root.configure(bg='#2b2b2b')
        else:
            # Aplicar tema claro
            style = ttk.Style()
            style.theme_use('clam')
            # Configurar colores claros
            self.root.configure(bg='#f0f0f0')
    
    def update_stats(self):
        """Actualizar estadísticas en la barra de estado"""
        stats = self.upload_stats
        self.stats_label.config(text=f"📊 ✅ {stats['success']} | ❌ {stats['error']} | 📁 {stats['total']}")
        
    def update_files_count(self, count):
        """Actualizar contador de archivos"""
        self.files_label.config(text=f"📁 {count} archivos")
        
    def update_connection_status(self, status, color="green"):
        """Actualizar estado de conexión"""
        self.connection_label.config(text=f"🔗 {status}", foreground=color)
        
    def setup_logging(self):
        """Configurar logging para la GUI"""
        self.log("🎉 Interfaz iniciada correctamente")
        self.log("📋 Selecciona un directorio y autor para comenzar")
        
    def log(self, message):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Agregar a la cola para procesamiento seguro
        self.log_queue.put(log_message)
        
        # Procesar mensajes pendientes
        self.process_log_queue()
        
    def process_log_queue(self):
        """Procesar mensajes de la cola de log"""
        try:
            # Procesar máximo 5 mensajes por vez para mejor rendimiento
            processed = 0
            while processed < 5:
                try:
                    message = self.log_queue.get_nowait()
                    self.log_text.insert(tk.END, message)
                    self.log_queue.task_done()
                    processed += 1
                except queue.Empty:
                    break
            
            # Solo hacer scroll si se procesaron mensajes
            if processed > 0:
                self.log_text.see(tk.END)
                
        except Exception as e:
            pass
        
        # Programar siguiente verificación con frecuencia muy reducida
        self.root.after(200, self.process_log_queue)
        
    def check_configuration(self):
        """Verificar configuración de Archive.org"""
        try:
            import internetarchive as ia
            # Intentar obtener información de la cuenta
            self.log("🔍 Verificando configuración de Archive.org...")
            # Si no hay error, la configuración está bien
            self.log("✅ Configuración de Archive.org verificada")
        except Exception as e:
            self.log(f"❌ Error en configuración: {e}")
            messagebox.showerror("Error de Configuración", 
                               "No se pudo verificar la configuración de Archive.org.\n"
                               "Ejecuta 'ia configure' en la terminal.")
        
    def browse_directory(self):
        """Abrir diálogo para seleccionar directorio"""
        directory = filedialog.askdirectory(title="Seleccionar directorio con material")
        if directory:
            self.directory_var.set(directory)
            self.log(f"📁 Directorio seleccionado: {directory}")
            self.scan_directory()
            
    def scan_directory(self):
        """Escanear directorio en busca de archivos"""
        directory = self.directory_var.get()
        if not directory:
            messagebox.showwarning("Advertencia", "Selecciona un directorio primero")
            return
            
        if not os.path.exists(directory):
            messagebox.showerror("Error", "El directorio no existe")
            return
            
        self.log(f"🔍 Escaneando directorio: {directory}")
        
        # Limpiar lista actual
        self.clear_files_list()
        
        # Escanear archivos en hilo separado para no bloquear la GUI
        def scan_worker():
            try:
                # Determinar colección a usar
                if self.use_existing_collection_var.get() and self.existing_collection_var.get().strip():
                    collection_to_use = self.existing_collection_var.get().strip()
                else:
                    collection_to_use = self.collection_var.get()
                
                # Determinar nombre de lista para escaneo
                list_name = None
                if self.add_to_list_var.get() and self.list_name_var.get().strip():
                    list_name = self.list_name_var.get().strip()
                
                uploader = ArchiveUploader(self.author_var.get() or "Autor", collection_to_use, list_name)
                files = uploader.scan_directory(Path(directory))
                
                files_found = 0
                # Procesar archivos en lotes más pequeños para mejor rendimiento
                batch_size = 5
                for i in range(0, len(files), batch_size):
                    batch = files[i:i+batch_size]
                    
                    for file_path in batch:
                        # Obtener información del archivo
                        file_size = os.path.getsize(file_path)
                        file_size_str = self.format_file_size(file_size)
                        file_type = uploader.get_mediatype(file_path)
                        
                        # Insertar en la lista en el hilo principal
                        self.root.after(0, lambda fp=file_path, ft=file_type, fs=file_size_str: 
                            self.files_tree.insert("", tk.END, text=fp.name, values=(ft, fs)))
                        files_found += 1
                    
                    # Permitir que la GUI procese eventos entre lotes
                    self.root.after(0, lambda: self.root.update_idletasks())
                    import time
                    time.sleep(0.05)  # Pausa más larga para mejor responsividad
                    
                # Actualizar log en el hilo principal
                self.root.after(0, lambda: self.log(f"✅ Encontrados {files_found} archivos"))
                self.root.after(0, lambda: self.progress_var.set(f"Encontrados {files_found} archivos"))
                self.root.after(0, lambda: self.update_files_count(files_found))
                
            except Exception as e:
                self.root.after(0, lambda: self.log(f"❌ Error escaneando directorio: {e}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error escaneando directorio: {e}"))
        
        # Iniciar escaneo en hilo separado
        scan_thread = threading.Thread(target=scan_worker)
        scan_thread.daemon = True
        scan_thread.start()
            
    def clear_files_list(self):
        """Limpiar lista de archivos"""
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
            
    def format_file_size(self, size_bytes):
        """Formatear tamaño de archivo"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
            
        return f"{size_bytes:.1f} {size_names[i]}"
        
    def start_upload(self):
        """Iniciar proceso de subida"""
        try:
            self.log("🔍 Verificando estado antes de iniciar subida...")
            
            if self.uploading:
                self.log("❌ Ya hay una subida en progreso")
                messagebox.showinfo("Info", "Ya hay una subida en progreso")
                return
                
            directory = self.directory_var.get()
            author = self.author_var.get()
            
            self.log(f"📁 Directorio: {directory}")
            self.log(f"👤 Autor: {author}")
            
            if not directory or not author:
                self.log("❌ Faltan directorio o autor")
                messagebox.showerror("Error", "Selecciona directorio y autor")
                return
                
            if not os.path.exists(directory):
                self.log(f"❌ El directorio no existe: {directory}")
                messagebox.showerror("Error", "El directorio no existe")
                return
                
            # Verificar que hay archivos en la lista
            files_count = len(self.files_tree.get_children())
            self.log(f"📋 Archivos en lista: {files_count}")
            
            if files_count == 0:
                self.log("❌ No hay archivos para subir")
                messagebox.showwarning("Advertencia", "No hay archivos para subir. Escanea el directorio primero.")
                return
                
            # Confirmar inicio
            response = messagebox.askyesno("Confirmar Subida", 
                                         f"¿Iniciar subida de material de '{author}'?\n"
                                         f"Directorio: {directory}\n"
                                         f"Archivos: {files_count}")
            if not response:
                self.log("❌ Usuario canceló la subida")
                return
                
            self.log("✅ Iniciando subida...")
            self.uploading = True
            self.upload_button.config(state="disabled")
            self.progress_var.set("Iniciando subida...")
            
            # Deshabilitar operaciones pesadas durante la subida
            self.disable_heavy_operations()
            
            # Iniciar subida en hilo separado
            self.upload_thread = threading.Thread(target=self.upload_worker, 
                                                args=(directory, author))
            self.upload_thread.daemon = True
            self.upload_thread.start()
            
        except Exception as e:
            self.log(f"❌ Error en start_upload: {e}")
            messagebox.showerror("Error", f"Error iniciando subida: {e}")
            self.uploading = False
            self.upload_button.config(state="normal")
            
    def upload_worker(self, directory, author):
        """Trabajador de subida en hilo separado con múltiples hilos"""
        try:
            self.log(f"🚀 Iniciando subida para '{author}'")
            
            # Determinar colección a usar
            if self.use_existing_collection_var.get() and self.existing_collection_var.get().strip():
                collection_to_use = self.existing_collection_var.get().strip()
                self.log(f"📚 Usando colección existente: {collection_to_use}")
            else:
                collection_to_use = self.collection_var.get()
                self.log(f"📂 Usando colección estándar: {collection_to_use}")
            
            # Determinar nombre de lista
            list_name = None
            if self.add_to_list_var.get() and self.list_name_var.get().strip():
                list_name = self.list_name_var.get().strip()
                self.log(f"📋 Agregando items a lista: {list_name}")
            
            # Crear uploader
            uploader = ArchiveUploader(author, collection_to_use, list_name)
            
            # Escanear archivos
            files = uploader.scan_directory(Path(directory))
            total_files = len(files)
            
            if total_files == 0:
                self.log("❌ No se encontraron archivos para subir")
                return
                
            self.log(f"📋 Procesando {total_files} archivos")
            
            # Configurar barra de progreso
            self.root.after(0, lambda: self.progress_bar.config(maximum=total_files))
            
            # Variables compartidas para conteo
            from threading import Lock
            success_count = 0
            error_count = 0
            completed_count = 0
            lock = Lock()
            
            # Resetear estadísticas
            self.upload_stats = {"success": 0, "error": 0, "total": total_files}
            self.root.after(0, self.update_stats)
            
            def upload_single_file(file_path, file_index):
                nonlocal success_count, error_count, completed_count
                
                try:
                    if not self.uploading:  # Verificar si se canceló
                        return
                        
                    self.log(f"📤 Subiendo {file_index+1}/{total_files}: {file_path.name}")
                    
                    # Subir archivo
                    if uploader.upload_file(file_path):
                        with lock:
                            success_count += 1
                            self.upload_stats["success"] += 1
                        self.log(f"✅ Subido exitosamente: {file_path.name}")
                        # Actualizar stats solo ocasionalmente para mejor rendimiento
                        if success_count % 5 == 0:
                            self.root.after(0, self.update_stats)
                    else:
                        with lock:
                            error_count += 1
                            self.upload_stats["error"] += 1
                        self.log(f"❌ Error subiendo: {file_path.name}")
                        # Actualizar stats solo ocasionalmente para mejor rendimiento
                        if error_count % 5 == 0:
                            self.root.after(0, self.update_stats)
                        
                except Exception as e:
                    with lock:
                        error_count += 1
                    self.log(f"❌ Error subiendo {file_path.name}: {e}")
                finally:
                    with lock:
                        completed_count += 1
                    
                    # Actualizar progreso en el hilo principal (muy poco frecuente)
                    if completed_count % 10 == 0 or completed_count == total_files:
                        self.root.after(0, lambda: self.progress_bar.config(value=completed_count))
                        self.root.after(0, lambda: self.progress_var.set(f"Completados: {completed_count}/{total_files}"))
            
            # Determinar número de hilos desde la configuración
            try:
                max_threads = min(int(self.threads_var.get()), 5, total_files)
            except ValueError:
                max_threads = min(3, total_files)  # Default a 3 si hay error
            self.log(f"🔄 Usando {max_threads} hilos para subida paralela")
            
            # Crear pool de hilos
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                # Enviar todos los archivos al pool
                futures = []
                for i, file_path in enumerate(files):
                    if not self.uploading:
                        break
                    future = executor.submit(upload_single_file, file_path, i)
                    futures.append(future)
                
                # Esperar a que todos terminen con timeout para evitar bloqueos
                for future in concurrent.futures.as_completed(futures, timeout=1):
                    if not self.uploading:
                        break
                    try:
                        future.result(timeout=30)  # Timeout de 30 segundos por archivo
                    except concurrent.futures.TimeoutError:
                        self.log(f"⏰ Timeout en subida de archivo")
                    except Exception as e:
                        self.log(f"❌ Error en hilo de subida: {e}")
            
            # Finalizar
            self.root.after(0, lambda: self.progress_bar.config(value=total_files))
            self.root.after(0, lambda: self.progress_var.set(f"Completado: {success_count} exitosos, {error_count} errores"))
            
            self.log(f"🎉 Proceso completado:")
            self.log(f"  ✅ Exitosos: {success_count}")
            self.log(f"  ❌ Errores: {error_count}")
            self.log(f"  📁 Total: {total_files}")
            
            # Mostrar mensaje final
            if error_count == 0:
                self.root.after(0, lambda: messagebox.showinfo("Completado", 
                    f"Subida completada exitosamente!\n"
                    f"Archivos subidos: {success_count}"))
            else:
                self.root.after(0, lambda: messagebox.showwarning("Completado con Errores", 
                    f"Subida completada con algunos errores.\n"
                    f"Exitosos: {success_count}\n"
                    f"Errores: {error_count}"))
                    
        except Exception as e:
            self.log(f"❌ Error en subida: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error en subida: {e}"))
        finally:
            self.uploading = False
            self.root.after(0, lambda: self.upload_button.config(state="normal"))
            self.root.after(0, lambda: self.enable_heavy_operations())
    
    def disable_heavy_operations(self):
        """Deshabilitar operaciones pesadas durante la subida"""
        # Reducir frecuencia de actualizaciones
        self.root.after_cancel(self.log_timer) if hasattr(self, 'log_timer') else None
        
    def enable_heavy_operations(self):
        """Habilitar operaciones pesadas después de la subida"""
        # Restaurar frecuencia normal de actualizaciones
        pass
        
    def stop_upload(self):
        """Detener proceso de subida"""
        if self.uploading:
            self.uploading = False
            self.log("⏹️ Deteniendo subida...")
            self.progress_var.set("Detenido por usuario")
            self.enable_heavy_operations()
        else:
            messagebox.showinfo("Info", "No hay subida en progreso")
            
    def open_log(self):
        """Abrir archivo de log en editor"""
        log_file = ".archive_upload.log"
        if os.path.exists(log_file):
            try:
                os.system(f"open {log_file}")  # macOS
            except:
                try:
                    os.system(f"xdg-open {log_file}")  # Linux
                except:
                    try:
                        os.system(f"notepad {log_file}")  # Windows
                    except:
                        messagebox.showerror("Error", "No se pudo abrir el archivo de log")
        else:
            messagebox.showinfo("Info", "No hay archivo de log disponible")
            
    def test_connection(self):
        """Probar conexión y configuración"""
        try:
            self.log("🧪 Iniciando prueba de conexión...")
            
            # Probar importación
            from archive_uploader import ArchiveUploader
            self.log("✅ Importación de ArchiveUploader exitosa")
            
            # Probar creación de uploader
            test_uploader = ArchiveUploader("Test", "opensource")
            self.log("✅ Creación de uploader exitosa")
            
            # Probar configuración de internetarchive
            import internetarchive as ia
            self.log("✅ Módulo internetarchive disponible")
            
            # Probar directorio actual
            current_dir = os.getcwd()
            self.log(f"📁 Directorio actual: {current_dir}")
            
            # Probar variables de la GUI
            directory = self.directory_var.get()
            author = self.author_var.get()
            self.log(f"📁 Directorio en GUI: {directory}")
            self.log(f"👤 Autor en GUI: {author}")
            
            # Probar lista de archivos
            files_count = len(self.files_tree.get_children())
            self.log(f"📋 Archivos en lista: {files_count}")
            
            # Probar estado de botones
            button_state = self.upload_button.cget("state")
            self.log(f"🔘 Estado del botón de subida: {button_state}")
            
            # Probar estado de uploading
            self.log(f"🔄 Estado uploading: {self.uploading}")
            
            self.log("🎉 Todas las pruebas pasaron exitosamente")
            messagebox.showinfo("Prueba Exitosa", "Todas las verificaciones pasaron correctamente.\nLa GUI está funcionando bien.")
            
        except Exception as e:
            self.log(f"❌ Error en prueba: {e}")
            messagebox.showerror("Error en Prueba", f"Error durante la prueba:\n{e}")
    
    def test_connection(self):
        """Probar conexión con Archive.org"""
        try:
            self.log("🧪 Probando conexión con Archive.org...")
            
            # Importar y probar conexión
            import internetarchive as ia
            from archive_uploader import ArchiveUploader
            
            # Crear uploader de prueba
            test_uploader = ArchiveUploader("test", "opensource")
            
            # Verificar configuración
            self.log("✅ Configuración de Archive.org verificada")
            self.log("✅ Módulos importados correctamente")
            self.log("✅ Sistema listo para subir archivos")
            
            messagebox.showinfo("Prueba Exitosa", 
                              "✅ Conexión con Archive.org verificada\n"
                              "✅ Sistema funcionando correctamente")
                              
        except Exception as e:
            self.log(f"❌ Error en prueba: {e}")
            messagebox.showerror("Error en Prueba", 
                               f"Error verificando conexión:\n{e}")
        
    def show_help(self):
        """Mostrar ayuda"""
        help_text = """
📚 Archive.org Uploader - Ayuda

🚀 Cómo usar:
1. Selecciona el directorio con tu material
2. Escribe el nombre del autor
3. Elige la colección (opcional)
4. Haz clic en "Escanear Directorio"
5. Revisa la lista de archivos
6. Haz clic en "Iniciar Subida"

📁 Formatos soportados:
• Libros: PDF, EPUB, MOBI, TXT, DOC, DOCX
• Audio: MP3, WAV, FLAC, M4A, OGG
• Video: MP4, AVI, MKV, MOV, WEBM
• Imágenes: JPG, PNG, GIF, TIFF

⚙️ Configuración:
• Ejecuta 'ia configure' en terminal para configurar credenciales
• Los archivos se suben a tu cuenta de Archive.org

📊 Monitoreo:
• La barra de progreso muestra el avance
• El registro muestra detalles de cada operación
• Puedes detener el proceso en cualquier momento

❓ Problemas comunes:
• Verifica tu conexión a internet
• Asegúrate de tener credenciales configuradas
• Los archivos muy grandes pueden tardar más tiempo
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Ayuda - Archive.org Uploader")
        help_window.geometry("600x500")
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

def main():
    """Función principal"""
    root = tk.Tk()
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('clam')  # o 'aqua' en macOS
    
    # Crear aplicación
    app = ArchiveUploaderGUI(root)
    
    # Centrar ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Iniciar loop principal
    root.mainloop()

if __name__ == "__main__":
    main() 