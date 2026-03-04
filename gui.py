"""
Interfaz gráfica con Tkinter para el conversor de diálogos.
"""

import platform
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from src.batch_processor import BatchProcessor
from src.converter import DialogConverter
from src import updater


class DialogConverterGUI:
    """Interfaz gráfica para conversión de diálogos."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Conversor de Diálogos a Español")
        self.root.geometry("1000x750")

        # Prevenir que la ventana sea más pequeña
        self.root.minsize(900, 650)

        # Variables
        self.selected_files: List[Path] = []
        self.output_dir: Optional[Path] = None
        self.recursive_var = tk.BooleanVar(value=True)

        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Crear UI
        self._create_widgets()

        # Configurar ícono si existe
        self._setup_icon()

        # Configurar drag & drop (cross-platform)
        self._setup_drag_drop()

        # Comprobar actualizaciones al arrancar (solo cuando corre como AppImage)
        if updater.is_running_as_appimage():
            threading.Thread(target=self._check_updates_async, daemon=True).start()

    def _check_updates_async(self):
        """Comprueba actualizaciones en segundo plano y notifica si hay alguna."""
        result = updater.check_for_updates()
        if result.get("available"):
            self.root.after(0, lambda: self._show_update_banner(result))

    def _manual_check_update(self):
        """Disparado por el botón: comprueba actualizaciones y da feedback visible."""
        self.update_btn.config(state="disabled", text="Buscando...")

        def _check():
            result = updater.check_for_updates()

            def _done():
                self.update_btn.config(state="normal", text="Buscar actualización")
                if result.get("available"):
                    self._show_update_banner(result)
                elif result.get("error"):
                    messagebox.showwarning(
                        "Error al verificar",
                        f"No se pudo comprobar actualizaciones:\n{result['error']}",
                    )
                elif not result.get("is_appimage"):
                    messagebox.showinfo(
                        "Actualizaciones",
                        "No estás corriendo la app como AppImage.\n"
                        "Descargá la última versión desde:\n"
                        f"{updater.GITHUB_RELEASES_URL}",
                    )
                else:
                    messagebox.showinfo(
                        "Actualizaciones", "✅ Ya tenés la versión más reciente."
                    )

            self.root.after(0, _done)

        threading.Thread(target=_check, daemon=True).start()

    def _show_update_banner(self, check_result: dict):
        """Muestra un banner no bloqueante en la parte superior cuando hay update."""
        latest = check_result.get("latest_version", "")

        # Destruir contenido previo del banner_row y rellenarlo
        for w in self._banner_row.winfo_children():
            w.destroy()

        self._banner_row.config(bg="#2e7d32")
        inner = tk.Frame(self._banner_row, bg="#2e7d32", pady=4)
        inner.pack(fill="x")

        tk.Label(
            inner,
            text=f"Nueva versión disponible: v{latest}",
            bg="#2e7d32",
            fg="white",
            font=("", 10),
        ).pack(side="left", padx=(12, 8))

        tk.Button(
            inner,
            text="Actualizar ahora",
            command=lambda: self._apply_update(self._banner_row, check_result),
            bg="#1b5e20",
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=8,
        ).pack(side="left")

        def _hide():
            for w in self._banner_row.winfo_children():
                w.destroy()
            self._banner_row.config(bg="")

        tk.Button(
            inner,
            text="✕",
            command=_hide,
            bg="#2e7d32",
            fg="white",
            relief="flat",
            cursor="hand2",
        ).pack(side="right", padx=4)

    def _apply_update(self, banner: tk.Frame, check_result: dict):
        """Descarga el nuevo AppImage y reemplaza el actual."""
        download_url = check_result.get("download_url")
        if not download_url:
            messagebox.showinfo(
                "Actualización",
                f"No se encontró el archivo de descarga automática.\n"
                f"Descargalo manualmente desde:\n{updater.GITHUB_RELEASES_URL}",
            )
            return

        for w in self._banner_row.winfo_children():
            w.destroy()
        self._banner_row.config(bg="")

        progress_win = tk.Toplevel(self.root)
        progress_win.title("Actualizando...")
        progress_win.resizable(False, False)
        progress_win.grab_set()
        tk.Label(progress_win, text="Descargando actualización…", padx=20, pady=12).pack()
        bar = ttk.Progressbar(progress_win, mode="determinate", length=300, maximum=100)
        bar.pack(padx=20, pady=(0, 4))
        size_label = tk.Label(progress_win, text="", padx=20)
        size_label.pack(pady=(0, 12))

        def _progress(done, total):
            if total:
                pct = int(done / total * 100)
                mb_done = done / 1_048_576
                mb_total = total / 1_048_576
                self.root.after(0, lambda: bar.config(value=pct))
                self.root.after(0, lambda: size_label.config(text=f"{mb_done:.1f} / {mb_total:.1f} MB"))

        def _do_update():
            result = updater.apply_update(download_url, progress_callback=_progress)
            self.root.after(0, progress_win.destroy)
            if result["success"]:
                messagebox.showinfo(
                    "Actualización completada",
                    "✅ Actualización descargada correctamente.\n"
                    "Reiniciá la app para usar la nueva versión.",
                )
            else:
                messagebox.showerror(
                    "Error al actualizar",
                    f"No se pudo completar la actualización:\n{result.get('error', 'Error desconocido')}",
                )

        threading.Thread(target=_do_update, daemon=True).start()

    def _setup_icon(self):
        """Configura el ícono de la ventana."""
        icon_path = Path(__file__).parent / "icon.png"
        if icon_path.exists():
            try:
                icon = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, icon)
            except Exception:
                pass  # Silently fail if icon cannot be loaded

    def _create_widgets(self):
        """Crea los widgets de la interfaz."""
        # Frame principal con padding
        self._main_frame = ttk.Frame(self.root, padding="10")
        self._main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame = self._main_frame

        # Fila 0 reservada para el banner de actualizaciones (oculta si no hay update)
        self._banner_row = tk.Frame(main_frame)  # vacío por defecto
        self._banner_row.grid(row=0, column=0, sticky="ew")

        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)  # fila del treeview se expande

        # Header row: título + botón de actualización a la derecha (row=1)
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=1, column=0, sticky="ew", pady=(0, 2))
        header_frame.columnconfigure(0, weight=1)

        ttk.Label(
            header_frame,
            text="Conversor de Diálogos a Español",
            font=("Helvetica", 16, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.update_btn = ttk.Button(
            header_frame,
            text="Buscar actualización",
            command=self._manual_check_update,
        )
        self.update_btn.grid(row=0, column=1, sticky="e")

        # Subtítulo (row=2)
        ttk.Label(
            main_frame,
            text="Convierte diálogos con comillas al formato español con raya (—)",
            font=("Helvetica", 10),
        ).grid(row=2, column=0, pady=(0, 10), sticky=tk.W)

        # Botones de selección (row=3)
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, sticky=tk.EW, pady=(0, 5))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        buttons_frame.columnconfigure(3, weight=1)

        ttk.Button(
            buttons_frame, text="Seleccionar Archivos", command=self._select_files
        ).grid(row=0, column=0, padx=5, sticky=tk.EW)

        ttk.Button(
            buttons_frame, text="Seleccionar Carpeta", command=self._select_folder
        ).grid(row=0, column=1, padx=5, sticky=tk.EW)

        ttk.Button(
            buttons_frame,
            text="Eliminar Seleccionados",
            command=self._remove_selected_files,
        ).grid(row=0, column=2, padx=5, sticky=tk.EW)

        ttk.Button(buttons_frame, text="Limpiar Lista", command=self._clear_files).grid(
            row=0, column=3, padx=5, sticky=tk.EW
        )

        # Checkbox recursivo
        ttk.Checkbutton(
            main_frame,
            text="Buscar en subcarpetas (Recursivo)",
            variable=self.recursive_var,
        ).grid(row=4, column=0, sticky="w", padx=5, pady=2)

        # Separator
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=5, column=0, sticky="ew", pady=5
        )

        # Frame de archivos con scrollbar
        files_label = ttk.Label(
            main_frame, text="Archivos seleccionados:", font=("Helvetica", 11, "bold")
        )
        files_label.grid(row=5, column=0, sticky="w", pady=(0, 5))

        # Treeview para lista de archivos
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=6, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        self.files_tree = ttk.Treeview(
            tree_frame,
            columns=("nombre", "tipo", "tamaño", "ruta"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )

        vsb.config(command=self.files_tree.yview)
        hsb.config(command=self.files_tree.xview)

        # Bind tecla Delete/Supr
        self.files_tree.bind("<Delete>", lambda e: self._remove_selected_files())

        # Configurar columnas
        self.files_tree.heading("nombre", text="Nombre")
        self.files_tree.heading("tipo", text="Tipo")
        self.files_tree.heading("tamaño", text="Tamaño")
        self.files_tree.heading("ruta", text="Ruta")

        self.files_tree.column("nombre", width=200)
        self.files_tree.column("tipo", width=60)
        self.files_tree.column("tamaño", width=100)
        self.files_tree.column("ruta", width=400)

        # Grid layout
        self.files_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Output directory
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=7, column=0, sticky="ew", pady=(10, 0))
        output_frame.columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="Carpeta de salida:").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )

        # Default: carpeta del primer archivo seleccionado / convertidos
        self.output_var = tk.StringVar(value="")
        output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=50)
        output_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ttk.Button(
            output_frame, text="...", command=self._select_output_dir, width=5
        ).grid(row=0, column=2)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode="determinate", length=300)
        self.progress.grid(row=8, column=0, sticky="ew", pady=(10, 5))

        # Status label
        self.status_var = tk.StringVar(value="Listo para procesar archivos")
        ttk.Label(
            main_frame, textvariable=self.status_var, font=("Helvetica", 9)
        ).grid(row=9, column=0, sticky="w")

        # Botón procesar
        self.process_btn = ttk.Button(
            main_frame,
            text="Procesar Archivos",
            command=self._process_files,
            style="Accent.TButton",
        )
        self.process_btn.grid(row=10, column=0, pady=(15, 0), sticky="ew")

        # Configurar estilo del botón
        self.style.configure(
            "Accent.TButton", font=("Helvetica", 11, "bold"), padding=10
        )

    def _setup_drag_drop(self):
        """Configura drag & drop (básico con bind)."""
        # Sin mensaje de tip - dejamos más espacio para la UI
        pass

    def _select_files(self):
        """Abre diálogo para seleccionar archivos."""
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos",
            filetypes=[
                ("Archivos de texto", "*.txt *.odt"),
                ("Archivos de texto", "*.txt"),
                ("Documentos ODT", "*.odt"),
                ("Todos los archivos", "*.*"),
            ],
        )

        if files:
            for file_path in files:
                path = Path(file_path)
                if path not in self.selected_files:
                    self.selected_files.append(path)

            self._update_files_list()
            self._update_default_output()
            self.status_var.set(
                f"OK: {len(self.selected_files)} archivo(s) seleccionado(s)"
            )

    def _select_folder(self):
        """Abre diálogo para seleccionar carpeta."""
        folder = filedialog.askdirectory(title="Seleccionar carpeta")

        if folder:
            folder_path = Path(folder)

            # Usar BatchProcessor para encontrar archivos (reutilizar lógica)
            # Buscar recursivamente para encontrar archivos en subcarpetas
            converter = DialogConverter()
            batch = BatchProcessor(converter)
            new_files = batch.find_files(
                folder_path, "*.*", recursive=self.recursive_var.get()
            )

            for file_path in new_files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)

            self._update_files_list()
            self._update_default_output()

            if new_files:
                self.status_var.set(
                    f"OK: {len(new_files)} archivo(s) encontrado(s) en la carpeta"
                )
            else:
                self.status_var.set(
                    "AVISO: No se encontraron archivos .txt o .odt en la carpeta"
                )

    def _update_default_output(self):
        """Actualiza la carpeta de salida por defecto basada en archivos seleccionados."""
        if self.selected_files and not self.output_var.get():
            # Usar la carpeta del primer archivo seleccionado
            first_file = self.selected_files[0]
            default_output = first_file.parent / "convertidos"
            self.output_var.set(str(default_output))

    def _select_output_dir(self):
        """Selecciona carpeta de salida."""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder:
            self.output_var.set(folder)

    def _remove_selected_files(self):
        """Elimina los archivos seleccionados de la lista."""
        selected_items = self.files_tree.selection()
        if not selected_items:
            messagebox.showinfo(
                "Sin selección", "Por favor, selecciona archivos para eliminar"
            )
            return

        # Confirmación si son muchos archivos
        if len(selected_items) > 1:
            if not messagebox.askyesno(
                "Confirmar", f"¿Eliminar {len(selected_items)} archivos de la lista?"
            ):
                return

        # Identificar archivos a eliminar
        files_to_remove = []
        for item_id in selected_items:
            values = self.files_tree.item(item_id, "values")
            # Reconstruir path: values[3] es la ruta padre, values[0] es el nombre
            file_path = Path(values[3]) / values[0]
            files_to_remove.append(file_path)

        # Eliminar de la lista interna
        for file_path in files_to_remove:
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)

        # Actualizar UI
        self._update_files_list()
        self._update_default_output()
        self.status_var.set(
            f"INFO: Se eliminaron {len(files_to_remove)} archivos de la lista"
        )

    def _clear_files(self):
        """Limpia la lista de archivos."""
        self.selected_files.clear()
        self._update_files_list()
        self.output_var.set("")  # Limpiar también el output
        self.status_var.set("Lista de archivos limpiada")

    def _update_files_list(self):
        """Actualiza la lista visual de archivos."""
        # Limpiar árbol
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)

        # Añadir archivos
        for file_path in self.selected_files:
            file_type = file_path.suffix.upper().lstrip(".")
            file_size = self._format_size(file_path.stat().st_size)

            self.files_tree.insert(
                "",
                "end",
                values=(file_path.name, file_type, file_size, str(file_path.parent)),
            )

    def _format_size(self, size_bytes: int) -> str:
        """Formatea tamaño de archivo."""
        size: float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def _process_files(self):
        """Procesa los archivos seleccionados usando BatchProcessor (en hilo secundario)."""
        if not self.selected_files:
            messagebox.showwarning(
                "Sin archivos",
                "Por favor, selecciona al menos un archivo para procesar",
            )
            return

        # Si no hay output configurado, usar default
        output_path_str = self.output_var.get()
        if not output_path_str:
            output_path = self.selected_files[0].parent / "convertidos"
            self.output_var.set(str(output_path))
        else:
            output_path = Path(output_path_str)

        output_path.mkdir(parents=True, exist_ok=True)

        # Reiniciar progreso y deshabilitar botón
        self.progress["maximum"] = len(self.selected_files)
        self.progress["value"] = 0
        self.process_btn.config(state="disabled")

        # Callback thread-safe para actualizar UI desde el hilo secundario
        def update_progress(current, total, filename):
            self.root.after(
                0,
                lambda c=current, t=total, f=filename: (
                    self.status_var.set(f"Procesando {c}/{t}: {f}"),
                    self.progress.config(value=c),
                ),
            )

        def run_in_thread():
            try:
                converter = DialogConverter()
                batch = BatchProcessor(converter)

                results_list = batch.process_files(
                    files=self.selected_files,
                    output_dir=output_path,
                    progress_callback=update_progress,
                )

                results = []
                for result in results_list:
                    if result["success"]:
                        results.append((Path(result["file"]), True, result))
                    else:
                        results.append(
                            (
                                Path(result["file"]),
                                False,
                                result.get("error", "Error desconocido"),
                            )
                        )

                self.root.after(0, lambda: self._on_processing_done(results, output_path))

            except Exception as e:
                self.root.after(0, lambda err=e: self._on_processing_error(err))

        threading.Thread(target=run_in_thread, daemon=True).start()

    def _on_processing_done(self, results: List, output_path: Path):
        """Llamado en el hilo principal cuando el procesamiento termina con éxito."""
        self.process_btn.config(state="normal")
        self._show_results(results, output_path)

    def _on_processing_error(self, error: Exception):
        """Llamado en el hilo principal si el procesamiento falla."""
        self.process_btn.config(state="normal")
        messagebox.showerror(
            "Error", f"Error durante el procesamiento:\n\n{str(error)}"
        )

    def _show_results(self, results: List, output_dir: Path):
        """Muestra resumen de resultados con opción de ver logs."""
        success_count = sum(1 for _, success, _ in results if success)
        total = len(results)

        # Ventana de resultados
        result_window = tk.Toplevel(self.root)
        result_window.title("Resultados del Procesamiento")
        result_window.geometry("900x600")

        # Header
        header_frame = ttk.Frame(result_window, padding="10")
        header_frame.pack(fill=tk.X)

        if success_count == total:
            message = f"OK: Se procesaron exitosamente {total} archivo(s)"
            color = "green"
        else:
            message = f"AVISO: Se procesaron {success_count}/{total} archivo(s)"
            color = "orange"

        ttk.Label(
            header_frame, text=message, font=("Helvetica", 12, "bold"), foreground=color
        ).pack()

        ttk.Label(
            header_frame,
            text=f"📁 Archivos guardados en: {output_dir}",
            font=("Helvetica", 9),
        ).pack(pady=(5, 0))

        # Lista de resultados con scrollbar
        tree_frame = ttk.Frame(result_window, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        tree = ttk.Treeview(
            tree_frame,
            columns=("archivo", "estado", "cambios"),
            show="headings",
            yscrollcommand=vsb.set,
        )
        vsb.config(command=tree.yview)

        tree.heading("archivo", text="Archivo")
        tree.heading("estado", text="Estado")
        tree.heading("cambios", text="Cambios")

        tree.column("archivo", width=400)
        tree.column("estado", width=150)
        tree.column("cambios", width=150)

        # Mapeo de items a archivos de log (por nombre de archivo)
        self.result_logs = {}

        for idx, (file_path, success, result) in enumerate(results):
            # Asegurar que file_path sea Path
            if isinstance(file_path, str):
                file_path = Path(file_path)

            filename = file_path.name

            if success:
                status = "OK"
                changes = str(result.get("changes", 0))
                # Guardar path del log usando el nombre de archivo como clave
                log_file = output_dir / f"{file_path.stem}_convertido.log.txt"
                self.result_logs[filename] = log_file
            else:
                status = "ERROR"
                changes = "-"
                self.result_logs[filename] = None

            # Insertar en el tree sin intentar modificar la columna #0
            tree.insert("", "end", values=(filename, status, changes))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Función para ver log del archivo seleccionado
        def view_selected_log():
            selection = tree.selection()
            if not selection:
                messagebox.showinfo(
                    "Sin selección", "Por favor, selecciona un archivo para ver su log"
                )
                return

            # Obtener el nombre del archivo del primer item seleccionado
            item_id = selection[0]
            values = tree.item(item_id, "values")
            filename = values[0]

            # Buscar el log correspondiente
            log_file = self.result_logs.get(filename)

            if log_file and log_file.exists():
                self._show_log_window(log_file, filename)
            else:
                messagebox.showerror(
                    "Error", f"No se encontró el archivo de log para: {filename}"
                )

        # Doble clic para ver log
        tree.bind("<Double-Button-1>", lambda e: view_selected_log())

        # Botones
        button_frame = ttk.Frame(result_window, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Ver Log", command=view_selected_log).pack(
            side=tk.LEFT, padx=5
        )

        ttk.Button(
            button_frame,
            text="Abrir Carpeta de Salida",
            command=lambda: self._open_folder(output_dir),
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Cerrar", command=result_window.destroy).pack(
            side=tk.RIGHT, padx=5
        )

        # Actualizar status principal
        self.status_var.set(
            f"OK: Procesamiento completado: {success_count}/{total} archivos"
        )

    def _show_log_window(self, log_file: Path, filename: str):
        """Muestra ventana con el contenido del log formateado."""
        log_window = tk.Toplevel(self.root)
        log_window.title(f"Log de conversión - {filename}")
        log_window.geometry("1000x700")

        # Header
        header_frame = ttk.Frame(log_window, padding="10")
        header_frame.pack(fill=tk.X)

        ttk.Label(
            header_frame,
            text=f"Log de conversión: {filename}",
            font=("Helvetica", 12, "bold"),
        ).pack(side=tk.LEFT)

        ttk.Label(
            header_frame,
            text=f"Archivo: {log_file.name}",
            font=("Helvetica", 9),
            foreground="gray",
        ).pack(side=tk.RIGHT)

        # Text widget con scrollbar
        text_frame = ttk.Frame(log_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(text_frame, orient="vertical")
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=vsb.set,
            font=("Monospace", 10),
            bg="#f5f5f5",
            fg="#333333",
            padx=10,
            pady=10,
        )
        vsb.config(command=text_widget.yview)

        # Configurar tags para colores
        text_widget.tag_config(
            "header", font=("Helvetica", 11, "bold"), foreground="#2c3e50"
        )
        text_widget.tag_config(
            "change_num", font=("Monospace", 10, "bold"), foreground="#2980b9"
        )
        text_widget.tag_config("location", font=("Monospace", 9), foreground="#7f8c8d")
        text_widget.tag_config(
            "rule", font=("Monospace", 9, "italic"), foreground="#8e44ad"
        )
        text_widget.tag_config(
            "section",
            font=("Monospace", 10, "bold"),
            foreground="#16a085",
            underline=True,
        )
        text_widget.tag_config(
            "original",
            background="#ffe6e6",
            foreground="#c0392b",
            font=("Monospace", 10),
        )
        text_widget.tag_config(
            "converted",
            background="#e6ffe6",
            foreground="#27ae60",
            font=("Monospace", 10),
        )
        text_widget.tag_config("separator", foreground="#bdc3c7")
        text_widget.tag_config(
            "summary", font=("Helvetica", 11, "bold"), foreground="#34495e"
        )
        text_widget.tag_config("stats", font=("Monospace", 9), foreground="#7f8c8d")

        # Leer y parsear log
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                log_content = f.read()

            # Parsear y formatear log
            self._format_log_content(text_widget, log_content)
            text_widget.config(state="disabled")  # Solo lectura
        except Exception as e:
            text_widget.insert("1.0", f"Error al leer el log:\n{str(e)}")
            text_widget.config(state="disabled")

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Botón cerrar
        button_frame = ttk.Frame(log_window, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Cerrar", command=log_window.destroy).pack(
            side=tk.RIGHT
        )

    def _format_log_content(self, text_widget: tk.Text, log_content: str):
        """Formatea el contenido del log con colores y estructura."""
        lines = log_content.split("\n")
        in_change = False
        section = None
        skip_diff = False

        for line in lines:
            stripped = line.strip()

            # Header del archivo
            if stripped.startswith("====="):
                text_widget.insert(tk.END, line + "\n", "separator")
                continue

            # Resumen
            if "RESUMEN" in stripped or "Total de cambios" in stripped:
                text_widget.insert(tk.END, line + "\n", "summary")
                continue

            # Estadísticas
            if any(
                x in stripped
                for x in ["Líneas afectadas:", "Reglas aplicadas:", "aplicada"]
            ):
                text_widget.insert(tk.END, line + "\n", "stats")
                continue

            # Cambio individual
            if stripped.startswith("CAMBIO #"):
                if in_change:
                    text_widget.insert(tk.END, "\n" + "─" * 80 + "\n\n")
                text_widget.insert(tk.END, stripped + "\n", "change_num")
                in_change = True
                section = None
                skip_diff = False
                continue

            # Ubicación del cambio
            if stripped.startswith("Línea:"):
                text_widget.insert(tk.END, "  " + stripped + "\n", "location")
                continue

            # Regla aplicada
            if stripped.startswith("Regla:") or stripped.startswith("Regla aplicada:"):
                text_widget.insert(tk.END, "  " + stripped + "\n", "rule")
                continue

            # Secciones
            if stripped == "ORIGINAL:":
                text_widget.insert(tk.END, "\n  " + stripped + "\n", "section")
                section = "original"
                continue

            if stripped == "CONVERTIDO:":
                text_widget.insert(tk.END, "\n  " + stripped + "\n", "section")
                section = "converted"
                continue

            # OCULTAR sección DIFF
            if stripped.startswith("DIFF"):
                skip_diff = True
                section = None
                continue

            # Separador entre cambios - resetear skip_diff
            if stripped.startswith("-----"):
                in_change = False
                section = None
                skip_diff = False
                continue

            # Saltar líneas de diff
            if skip_diff:
                continue

            # Contenido según sección
            if section == "original" and line.strip():
                # Remover indentación inicial
                content = line[2:] if line.startswith("  ") else line
                text_widget.insert(tk.END, "    " + content + "\n", "original")
            elif section == "converted" and line.strip():
                # Remover indentación inicial
                content = line[2:] if line.startswith("  ") else line
                text_widget.insert(tk.END, "    " + content + "\n", "converted")
            elif not skip_diff and line.strip() and not stripped.startswith("-----"):
                # Líneas normales (solo si no estamos en diff)
                text_widget.insert(tk.END, line + "\n")

    def _open_folder(self, folder: Path):
        """Abre carpeta en explorador del sistema."""
        system = platform.system()

        try:
            if system == "Windows":
                subprocess.run(["explorer", str(folder)])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(folder)])
            else:  # Linux
                subprocess.run(["xdg-open", str(folder)])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta: {e}")


def main():
    """Punto de entrada de la aplicación."""
    root = tk.Tk()
    DialogConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
