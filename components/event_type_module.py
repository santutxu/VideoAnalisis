import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from resources.icon_data_base import IconDatabase
from .icon_picker import IconPickerWindow
@dataclass
class EventTemplate:
    """Estructura de un evento en la plantilla"""
    name: str
    type: str
    color: str
    icon: str
    shortcut: str = ""
    description: str = ""
    tags: List[str] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class IconSelectorDialog(QDialog):
    """Diálogo para seleccionar iconos"""
    
    def __init__(self, current_icon="📌", parent=None):
        super().__init__(parent)
        self.selected_icon = current_icon
        self.icon_db = IconDatabase()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Seleccionar Icono")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Barra de búsqueda
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar icono por nombre o palabras clave...")
        self.search_input.textChanged.connect(self.filter_icons)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Área de scroll para los iconos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.icons_widget = QWidget()
        self.icons_layout = QVBoxLayout(self.icons_widget)
        self.icons_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.icons_widget)
        layout.addWidget(scroll)
        
        # Vista previa del icono seleccionado
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Seleccionado:"))
        self.preview_label = QLabel(self.selected_icon)
        self.preview_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                padding: 10px;
                background-color: #f0f0f0;
                border: 2px solid #ddd;
                border-radius: 5px;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        preview_layout.addStretch()
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        preview_layout.addWidget(buttons)
        
        layout.addLayout(preview_layout)
        self.setLayout(layout)
        
        # Cargar iconos
        self.load_icons()
        
    def load_icons(self, search_text=""):
        """Carga los iconos en el widget"""
        # Limpiar layout existente
        while self.icons_layout.count():
            child = self.icons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        icons_data = self.icon_db.get_icons()
        search_lower = search_text.lower()
        
        for category, icons in icons_data.items():
            # Filtrar iconos según búsqueda
            if search_text:
                filtered_icons = [
                    icon for icon in icons
                    if search_lower in icon.name.lower() or
                    any(search_lower in keyword.lower() for keyword in icon.keywords)
                ]
                if not filtered_icons:
                    continue
            else:
                filtered_icons = icons
            
            # Grupo de categoría
            category_group = QGroupBox(category)
            category_layout = QVBoxLayout()
            
            # Grid de iconos
            icons_grid = QGridLayout()
            icons_grid.setSpacing(5)
            
            for i, icon_data in enumerate(filtered_icons):
                # Botón de icono
                btn = QPushButton(icon_data.emoji)
                btn.setToolTip(f"{icon_data.name}\nPalabras clave: {', '.join(icon_data.keywords)}")
                btn.setFixedSize(50, 50)
                btn.setStyleSheet("""
                    QPushButton {
                        font-size: 24px;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        background-color: white;
                    }
                    QPushButton:hover {
                        background-color: #e3f2fd;
                        border: 2px solid #2196F3;
                    }
                    QPushButton:pressed {
                        background-color: #bbdefb;
                    }
                """)
                
                # Conectar clic
                btn.clicked.connect(lambda checked, emoji=icon_data.emoji: self.select_icon(emoji))
                
                # Añadir al grid
                row = i // 8  # 8 iconos por fila
                col = i % 8
                icons_grid.addWidget(btn, row, col)
            
            category_layout.addLayout(icons_grid)
            category_group.setLayout(category_layout)
            self.icons_layout.addWidget(category_group)
            
        # Añadir espaciador al final
        self.icons_layout.addStretch()
        
    def filter_icons(self, text):
        """Filtra los iconos según el texto de búsqueda"""
        self.load_icons(text)
        
    def select_icon(self, emoji):
        """Selecciona un icono"""
        self.selected_icon = emoji
        self.preview_label.setText(emoji)
        
    def get_selected_icon(self):
        """Retorna el icono seleccionado"""
        return self.selected_icon

class EventTypeListWidget(QWidget):
    """
    Widget para mostrar y seleccionar tipos de eventos tácticos.
    """
    on_file_selected = pyqtSignal(float) 
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Tipos de Eventos Tácticos")
        self.setMinimumWidth(300)
        self._setup_ui()
        
    def _setup_ui(self):
        """Crear panel izquierdo con lista de archivos"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header del panel
        header = QWidget()
        header.setObjectName("panelHeader")
        header_layout = QHBoxLayout(header)
        
        title = QLabel("📁 Plantillas Disponibles")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title)
        
        # Botón para refrescar lista
        btn_refresh = QPushButton("🔄")
        btn_refresh.setToolTip("Actualizar lista")
        btn_refresh.setFixedSize(30, 30)
        btn_refresh.clicked.connect(self.load_file_list)
        header_layout.addWidget(btn_refresh)
        
        layout.addWidget(header)
        
        # Barra de búsqueda
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Buscar plantilla...")
        self.search_bar.textChanged.connect(self.filter_file_list)
        layout.addWidget(self.search_bar)
        
        # Lista de archivos
        self.file_list = QListWidget()
        self.file_list.setObjectName("fileList")
        self.file_list.itemClicked.connect(self.on_file_selected)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_file_context_menu)
        layout.addWidget(self.file_list)
        
        # Panel de información del archivo
        info_panel = QWidget()
        info_panel.setObjectName("infoPanel")
        info_layout = QFormLayout(info_panel)
        info_layout.setContentsMargins(10, 10, 10, 10)
        
        self.info_name = QLabel("-")
        self.info_size = QLabel("-")
        self.info_modified = QLabel("-")
        self.info_events = QLabel("-")
        
        info_layout.addRow("Archivo:", self.info_name)
        info_layout.addRow("Tamaño:", self.info_size)
        info_layout.addRow("Modificado:", self.info_modified)
        info_layout.addRow("Eventos:", self.info_events)
        
        layout.addWidget(info_panel)
        
        # Botones de acción para archivos
        file_actions = QWidget()
        actions_layout = QHBoxLayout(file_actions)
        actions_layout.setSpacing(5)
        
        btn_new = QPushButton("➕ Nueva")
        btn_new.clicked.connect(self.create_new_template)
        actions_layout.addWidget(btn_new)
        
        btn_duplicate = QPushButton("📋 Duplicar")
        btn_duplicate.clicked.connect(self.duplicate_template)
        actions_layout.addWidget(btn_duplicate)
        
        btn_delete = QPushButton("🗑️ Eliminar")
        btn_delete.clicked.connect(self.delete_template)
        actions_layout.addWidget(btn_delete)
        
        layout.addWidget(file_actions)
        self.setLayout(layout)
        
    
    def load_file_list(self):
        """Cargar lista de archivos JSON del directorio"""
        self.file_list.clear()
        
        try:
            # Buscar archivos JSON
            json_files = sorted(self.templates_dir.glob("*.json"))
            
            for file_path in json_files:
                # Crear item con icono
                item = QListWidgetItem()
                item.setText(file_path.stem)  # Nombre sin extensión
                item.setData(Qt.UserRole, str(file_path))  # Guardar ruta completa
                
                # Agregar icono según el contenido
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        event_count = len(data) if isinstance(data, list) else 0
                        
                        # Icono según cantidad de eventos
                        if event_count == 0:
                            item.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
                        elif event_count < 5:
                            item.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                        else:
                            item.setIcon(self.style().standardIcon(QStyle.SP_FileDialogListView))
                            
                        # Tooltip con información
                        item.setToolTip(f"Eventos: {event_count}\nArchivo: {file_path.name}")
                        
                except:
                    item.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    item.setToolTip("Error al leer el archivo")
                    
                self.file_list.addItem(item)
                
            # Agregar item para crear nueva plantilla
            new_item = QListWidgetItem()
            new_item.setText("➕ Crear nueva plantilla...")
            new_item.setData(Qt.UserRole, "NEW")
            new_item.setForeground(QColor("#3498db"))
            self.file_list.addItem(new_item)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar archivos: {str(e)}")
            
    def filter_file_list(self, text):
        """Filtrar lista de archivos según búsqueda"""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
            
    def on_file_selected(self, item):
        """Manejar selección de archivo"""
        file_path = item.data(Qt.UserRole)
        
        if file_path == "NEW":
            self.create_new_template()
            return
            
        # Verificar si hay cambios sin guardar
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Cambios sin guardar",
                "¿Desea guardar los cambios antes de cargar otra plantilla?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_current_template()
            elif reply == QMessageBox.Cancel:
                return
                
        # Cargar archivo seleccionado
        self.load_template(file_path)
        
    def load_template(self, file_path):
        """Cargar plantilla desde archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.current_file = file_path
            self.current_data = data if isinstance(data, list) else []
            
            # Actualizar información del archivo
            file_info = Path(file_path).stat()
            self.info_name.setText(Path(file_path).name)
            self.info_size.setText(f"{file_info.st_size / 1024:.1f} KB")
            self.info_modified.setText(
                datetime.fromtimestamp(file_info.st_mtime).strftime("%Y-%m-%d %H:%M")
            )
            self.info_events.setText(str(len(self.current_data)))
            
            # Actualizar título del editor
            self.editor_title.setText(f"📝 Editando: {Path(file_path).stem}")
            
            # Cargar datos en la tabla
            self.populate_table(self.current_data)
            
            # Actualizar vista previa
            self.update_preview()
            
            # Resetear estado de modificación
            self.is_modified = False
            self.update_modified_state()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar plantilla: {str(e)}")
            
    
    def show_file_context_menu(self, position):
        """Mostrar menú contextual para archivos"""
        item = self.file_list.itemAt(position)
        if not item or item.data(Qt.UserRole) == "NEW":
            return
            
        menu = QMenu(self)
        
        action_open = QAction("📂 Abrir", menu)
        action_open.triggered.connect(lambda: self.load_template(item.data(Qt.UserRole)))
        menu.addAction(action_open)
        
        action_duplicate = QAction("📋 Duplicar", menu)
        action_duplicate.triggered.connect(self.duplicate_template)
        menu.addAction(action_duplicate)
        
        action_rename = QAction("✏️ Renombrar", menu)
        action_rename.triggered.connect(lambda: self.rename_template(item))
        menu.addAction(action_rename)
        
        menu.addSeparator()
        
        action_delete = QAction("🗑️ Eliminar", menu)
        action_delete.triggered.connect(self.delete_template)
        menu.addAction(action_delete)
        
        menu.exec_(self.file_list.mapToGlobal(position))
        
    def duplicate_template(self):
        """Duplicar plantilla seleccionada"""
        current_item = self.file_list.currentItem()
        if not current_item or current_item.data(Qt.UserRole) == "NEW":
            QMessageBox.warning(self, "Advertencia", "Seleccione una plantilla para duplicar")
            return
            
        # Obtener nombre para la copia
        original_name = current_item.text()
        new_name, ok = QInputDialog.getText(
            self,
            "Duplicar Plantilla",
            "Nombre de la nueva plantilla:",
            text=f"{original_name}_copia"
        )
        
        if not ok or not new_name:
            return
            
        try:
            # Leer plantilla original
            original_path = current_item.data(Qt.UserRole)
            with open(original_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Guardar copia
            if not new_name.endswith('.json'):
                new_name += '.json'
            new_path = self.templates_dir / new_name
            
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            # Actualizar lista
            self.load_file_list()
            
            QMessageBox.information(self, "Éxito", "Plantilla duplicada correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al duplicar plantilla: {str(e)}")
            
    def delete_template(self):
        """Eliminar plantilla seleccionada"""
        current_item = self.file_list.currentItem()
        if not current_item or current_item.data(Qt.UserRole) == "NEW":
            QMessageBox.warning(self, "Advertencia", "Seleccione una plantilla para eliminar")
            return
            
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar la plantilla '{current_item.text()}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                file_path = Path(current_item.data(Qt.UserRole))
                file_path.unlink()
                
                # Si es el archivo actual, limpiar editor
                if str(file_path) == self.current_file:
                    self.table.setRowCount(0)
                    self.current_file = None
                    self.current_data = []
                    self.editor_title.setText("📝 Editor de Plantilla")
                    
                # Actualizar lista
                self.load_file_list()
                
                QMessageBox.information(self, "Éxito", "Plantilla eliminada correctamente")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar plantilla: {str(e)}")
    def rename_template(self, item):
        """Renombrar una plantilla"""
        old_name = item.text()
        new_name, ok = QInputDialog.getText(
            self,
            "Renombrar Plantilla",
            "Nuevo nombre:",
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            try:
                old_path = Path(item.data(Qt.UserRole))
                if not new_name.endswith('.json'):
                    new_name += '.json'
                new_path = old_path.parent / new_name
                
                old_path.rename(new_path)
                
                # Si es el archivo actual, actualizar referencia
                if str(old_path) == self.current_file:
                    self.current_file = str(new_path)
                    
                self.load_file_list()
                
                QMessageBox.information(self, "Éxito", "Plantilla renombrada correctamente")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al renombrar: {str(e)}")
        
    
    def create_new_template(self):
        """Crear nueva plantilla"""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Cambios sin guardar",
                "¿Desea guardar los cambios antes de crear una nueva plantilla?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_current_template()
            elif reply == QMessageBox.Cancel:
                return
                
        # Limpiar tabla
        self.table.setRowCount(0)
        self.current_file = "NEW"
        self.current_data = []
        
        # Agregar algunas filas de ejemplo
        default_events = [
            {"name": "Inicio", "type": "General", "color": "#27ae60", "icon": "▶", "shortcut": "F1"},
            {"name": "Pausa", "type": "General", "color": "#f39c12", "icon": "⏸", "shortcut": "F2"},
            {"name": "Final", "type": "General", "color": "#e74c3c", "icon": "■", "shortcut": "F3"},
        ]
        
        for event in default_events:
            self.add_table_row_with_data(event)
            
        self.editor_title.setText("📝 Nueva Plantilla")
        self.is_modified = True
        self.update_modified_state()
        self.update_preview()
        
        
    def save_current_template(self):
        """Guardar plantilla actual"""
        if not self.current_file or self.current_file == "NEW":
            # Pedir nombre para nueva plantilla
            name, ok = QInputDialog.getText(
                self,
                "Nueva Plantilla",
                "Nombre de la plantilla:",
                text="nueva_plantilla"
            )
            
            if not ok or not name:
                return
                
            # Asegurar extensión .json
            if not name.endswith('.json'):
                name += '.json'
                
            self.current_file = str(self.templates_dir / name)
            
        # Obtener datos de la tabla
        data = self.get_table_data()
        
        try:
            # Guardar en archivo
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.is_modified = False
            self.update_modified_state()
            
            # Actualizar lista de archivos
            self.load_file_list()
            
            # Mostrar mensaje de éxito
            QMessageBox.information(self, "Guardado", "Plantilla guardada correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar plantilla: {str(e)}")

class EventTypeTableWidget(QWidget):
    """
    Widget para mostrar y seleccionar tipos de eventos tácticos.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Tipos de Eventos Tácticos")
        self.setMinimumWidth(300)
        self._setup_ui()
        
    
    def _setup_ui(self):
        """Crear panel derecho con editor de tabla"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header del panel
        header = QWidget()
        header.setObjectName("panelHeader")
        header_layout = QHBoxLayout(header)
        
        self.editor_title = QLabel("📝 Editor de Plantilla")
        self.editor_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.editor_title)
        
        header_layout.addStretch()
        
        # Indicador de modificación
        self.modified_label = QLabel()
        self.modified_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        header_layout.addWidget(self.modified_label)
        
        # Botón guardar
        self.btn_save = QPushButton("💾 Guardar")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_current_template)
        header_layout.addWidget(self.btn_save)
        
        layout.addWidget(header)
        
        # Toolbar de la tabla
        #toolbar = self.create_table_toolbar()
        #layout.addWidget(toolbar)
        
        # Tabla editable
        self.table = QTableWidget()
        self.table.setObjectName("eventTable")
        self.setup_table()
        layout.addWidget(self.table)
        
        # Panel de vista previa
        #preview_panel = self.create_preview_panel()
        #layout.addWidget(preview_panel)
        
        
    def save_current_template(self):
        """Guardar plantilla actual"""
        if not self.current_file or self.current_file == "NEW":
            # Pedir nombre para nueva plantilla
            name, ok = QInputDialog.getText(
                self,
                "Nueva Plantilla",
                "Nombre de la plantilla:",
                text="nueva_plantilla"
            )
            
            if not ok or not name:
                return
                
            # Asegurar extensión .json
            if not name.endswith('.json'):
                name += '.json'
                
            self.current_file = str(self.templates_dir / name)
            
        # Obtener datos de la tabla
        data = self.get_table_data()
        
        try:
            # Guardar en archivo
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.is_modified = False
            self.update_modified_state()
            
            # Actualizar lista de archivos
            self.load_file_list()
            
            # Mostrar mensaje de éxito
            QMessageBox.information(self, "Guardado", "Plantilla guardada correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar plantilla: {str(e)}")

class TemplateManagerDialog(QDialog):
    """Dialog principal para gestión de plantillas JSON"""
    
    template_selected = pyqtSignal(dict,bool)  # Emite la plantilla seleccionada
    
    def __init__(self, templates_dir: str = "templates", parent=None):
        super().__init__(parent)
        self.templates_dir = Path(templates_dir)
        self.current_file = None
        self.current_data = []
        self.is_modified = False
        
        # Crear directorio si no existe
        self.templates_dir.mkdir(exist_ok=True)
        
        self.init_ui()
        self.load_file_list()
        self.setup_shortcuts()
        
    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.setWindowTitle("📋 Gestor de Plantillas de Eventos")
        self.setModal(True)
        self.resize(1400, 800)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Splitter horizontal para dividir las dos secciones
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo - Lista de archivos
        left_panel = self.create_left_panel()
        #left_panel = EventTypeListWidget()
        self.splitter.addWidget(left_panel)
        
        # Panel derecho - Editor de tabla
        right_panel = self.create_right_panel()
        #right_panel = EventTypeTableWidget()
        self.splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter (30% - 70%)
        self.splitter.setSizes([400, 1000])
        
        main_layout.addWidget(self.splitter)
        
        # Barra de botones inferior
        button_bar = self.create_button_bar()
        main_layout.addWidget(button_bar)
        
        # Aplicar estilos
        #self.apply_styles()
        
    def create_left_panel(self):
        """Crear panel izquierdo con lista de archivos"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header del panel
        header = QWidget()
        header.setObjectName("panelHeader")
        header_layout = QHBoxLayout(header)
        
        title = QLabel("📁 Plantillas Disponibles")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title)
        
        # Botón para refrescar lista
        btn_refresh = QPushButton("🔄")
        btn_refresh.setToolTip("Actualizar lista")
        btn_refresh.setFixedSize(30, 30)
        btn_refresh.clicked.connect(self.load_file_list)
        header_layout.addWidget(btn_refresh)
        
        layout.addWidget(header)
        
        # Barra de búsqueda
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Buscar plantilla...")
        self.search_bar.textChanged.connect(self.filter_file_list)
        layout.addWidget(self.search_bar)
        
        # Lista de archivos
        self.file_list = QListWidget()
        self.file_list.setObjectName("fileList")
        self.file_list.itemClicked.connect(self.on_file_selected)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_file_context_menu)
        layout.addWidget(self.file_list)
        
        # Panel de información del archivo
        info_panel = QWidget()
        info_panel.setObjectName("infoPanel")
        info_layout = QFormLayout(info_panel)
        info_layout.setContentsMargins(10, 10, 10, 10)
        
        self.info_name = QLabel("-")
        self.info_size = QLabel("-")
        self.info_modified = QLabel("-")
        self.info_events = QLabel("-")
        
        info_layout.addRow("Archivo:", self.info_name)
        info_layout.addRow("Tamaño:", self.info_size)
        info_layout.addRow("Modificado:", self.info_modified)
        info_layout.addRow("Eventos:", self.info_events)
        
        layout.addWidget(info_panel)
        
        # Botones de acción para archivos
        file_actions = QWidget()
        actions_layout = QHBoxLayout(file_actions)
        actions_layout.setSpacing(5)
        
        btn_new = QPushButton("➕ Nueva")
        btn_new.clicked.connect(self.create_new_template)
        actions_layout.addWidget(btn_new)
        
        btn_duplicate = QPushButton("📋 Duplicar")
        btn_duplicate.clicked.connect(self.duplicate_template)
        actions_layout.addWidget(btn_duplicate)
        
        btn_delete = QPushButton("🗑️ Eliminar")
        btn_delete.clicked.connect(self.delete_template)
        actions_layout.addWidget(btn_delete)
        
        layout.addWidget(file_actions)
        
        return panel
        
    def create_right_panel(self):
        """Crear panel derecho con editor de tabla"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header del panel
        header = QWidget()
        header.setObjectName("panelHeader")
        header_layout = QHBoxLayout(header)
        
        self.editor_title = QLabel("📝 Editor de Plantilla")
        self.editor_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.editor_title)
        
        header_layout.addStretch()
        
        # Indicador de modificación
        self.modified_label = QLabel()
        self.modified_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        header_layout.addWidget(self.modified_label)
        
        # Botón guardar
        self.btn_save = QPushButton("💾 Guardar")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_current_template)
        header_layout.addWidget(self.btn_save)
        
        layout.addWidget(header)
        
        # Toolbar de la tabla
        toolbar = self.create_table_toolbar()
        layout.addWidget(toolbar)
        
        # Tabla editable
        self.table = QTableWidget()
        self.table.setObjectName("eventTable")
        self.setup_table()
        layout.addWidget(self.table)
        
        # Panel de vista previa
        preview_panel = self.create_preview_panel()
        layout.addWidget(preview_panel)
        
        return panel
        
    def create_table_toolbar(self):
        """Crear barra de herramientas para la tabla"""
        toolbar = QWidget()
        toolbar.setObjectName("tableToolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Botones de edición
        btn_add_row = QPushButton("➕ Agregar Evento")
        btn_add_row.clicked.connect(self.add_table_row)
        layout.addWidget(btn_add_row)
        
        btn_delete_row = QPushButton("➖ Eliminar Fila")
        btn_delete_row.clicked.connect(self.delete_table_row)
        layout.addWidget(btn_delete_row)
        
        btn_move_up = QPushButton("⬆ Subir")
        btn_move_up.clicked.connect(self.move_row_up)
        layout.addWidget(btn_move_up)
        
        btn_move_down = QPushButton("⬇ Bajar")
        btn_move_down.clicked.connect(self.move_row_down)
        layout.addWidget(btn_move_down)
        
        layout.addStretch()
        
        # Botones de importación/exportación
        btn_import = QPushButton("📥 Importar CSV")
        btn_import.clicked.connect(self.import_from_csv)
        layout.addWidget(btn_import)
        
        btn_export = QPushButton("📤 Exportar CSV")
        btn_export.clicked.connect(self.export_to_csv)
        layout.addWidget(btn_export)
        
        return toolbar
        
    def setup_table(self):
        """Configurar la tabla editable"""
        # Definir columnas
        columns = [
            ("Activo", 60),
            ("Nombre", 150),
            ("Tipo", 120),
            ("Color", 80),
            ("Icono", 60),
            ("Atajo", 80),
            ("duracion", 80)
        ]
        
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([col[0] for col in columns])
        
        # Configurar anchos de columna
        for i, (_, width) in enumerate(columns):
            self.table.setColumnWidth(i, width)
            
        # Configurar propiedades de la tabla
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_context_menu)
        
        # Conectar señales
        self.table.itemChanged.connect(self.on_table_item_changed)
        
        # Hacer que algunas columnas se estiren
        header = self.table.horizontalHeader()
        #header.setSectionResizeMode(6, QHeaderView.Stretch)  # Descripción
        #header.setSectionResizeMode(7, QHeaderView.Stretch)  # Tags
        
    def create_preview_panel(self):
        """Crear panel de vista previa"""
        panel = QGroupBox("👁 Vista Previa")
        panel.setMaximumHeight(150)
        layout = QHBoxLayout(panel)
        
        self.preview_area = QScrollArea()
        self.preview_widget = QWidget()
        self.preview_layout = QHBoxLayout(self.preview_widget)
        self.preview_layout.setSpacing(10)
        
        self.preview_area.setWidget(self.preview_widget)
        self.preview_area.setWidgetResizable(True)
        self.preview_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.preview_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        layout.addWidget(self.preview_area)
        
        return panel
        
    def create_button_bar(self):
        """Crear barra de botones inferior"""
        button_bar = QWidget()
        button_bar.setMaximumHeight(100)
        layout = QHBoxLayout(button_bar)
        
        # Botones de la izquierda
        btn_import_template = QPushButton("📥 Importar Plantilla")
        btn_import_template.clicked.connect(self.import_template)
        layout.addWidget(btn_import_template)
        
        btn_export_template = QPushButton("📤 Exportar Plantilla")
        btn_export_template.clicked.connect(self.export_template)
        layout.addWidget(btn_export_template)
        
        layout.addStretch()
        
        self.checkDefaultTemplate = QCheckBox("⭐ Establecer como Predeterminada")
        self.checkDefaultTemplate.setToolTip("Usar esta plantilla como predeterminada para nuevos proyectos")
        layout.addWidget(self.checkDefaultTemplate)
        
        # Botones de la derecha
        btn_apply = QPushButton("✅ Aplicar y Cerrar")
        btn_apply.clicked.connect(self.apply_and_close)

        layout.addWidget(btn_apply)
        
        btn_cancel = QPushButton("❌ Cancelar")
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)
        
        return button_bar
        
    def apply_styles(self):
        """Aplicar estilos CSS al diálogo"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            
            #panelHeader {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                border-radius: 5px 5px 0 0;
            }
            
            #panelHeader QLabel {
                color: white;
            }
            
            #fileList {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
            }
            
            #fileList::item {
                padding: 8px;
                margin: 2px;
                border-radius: 3px;
            }
            
            #fileList::item:selected {
                background-color: #3498db;
                color: white;
            }
            
            #fileList::item:hover {
                background-color: #ecf0f1;
            }
            
            #infoPanel {
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-top: 10px;
            }
            
            #eventTable {
                background-color: white;
                gridline-color: #ddd;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            
            #tableToolbar {
                background-color: #ecf0f1;
                border-radius: 5px;
                margin: 5px 0;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
    def load_file_list(self):
        """Cargar lista de archivos JSON del directorio"""
        self.file_list.clear()
        
        try:
            # Buscar archivos JSON
            json_files = sorted(self.templates_dir.glob("*.json"))
            
            for file_path in json_files:
                # Crear item con icono
                item = QListWidgetItem()
                item.setText(file_path.stem)  # Nombre sin extensión
                item.setData(Qt.UserRole, str(file_path))  # Guardar ruta completa
                
                # Agregar icono según el contenido
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        event_count = len(data) if isinstance(data, list) else 0
                        
                        # Icono según cantidad de eventos
                        if event_count == 0:
                            item.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
                        elif event_count < 5:
                            item.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                        else:
                            item.setIcon(self.style().standardIcon(QStyle.SP_FileDialogListView))
                            
                        # Tooltip con información
                        item.setToolTip(f"Eventos: {event_count}\nArchivo: {file_path.name}")
                        
                except:
                    item.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning))
                    item.setToolTip("Error al leer el archivo")
                    
                self.file_list.addItem(item)
                
            # Agregar item para crear nueva plantilla
            new_item = QListWidgetItem()
            new_item.setText("➕ Crear nueva plantilla...")
            new_item.setData(Qt.UserRole, "NEW")
            new_item.setForeground(QColor("#3498db"))
            self.file_list.addItem(new_item)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar archivos: {str(e)}")
            
    def filter_file_list(self, text):
        """Filtrar lista de archivos según búsqueda"""
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
            
    def on_file_selected(self, item):
        """Manejar selección de archivo"""
        file_path = item.data(Qt.UserRole)
        
        if file_path == "NEW":
            self.create_new_template()
            return
            
        # Verificar si hay cambios sin guardar
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Cambios sin guardar",
                "¿Desea guardar los cambios antes de cargar otra plantilla?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_current_template()
            elif reply == QMessageBox.Cancel:
                return
                
        # Cargar archivo seleccionado
        self.load_template(file_path)
        
    def load_template(self, file_path):
        """Cargar plantilla desde archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.current_file = file_path
            self.current_data = data if isinstance(data, list) else []
            
            # Actualizar información del archivo
            file_info = Path(file_path).stat()
            self.info_name.setText(Path(file_path).name)
            self.info_size.setText(f"{file_info.st_size / 1024:.1f} KB")
            self.info_modified.setText(
                datetime.fromtimestamp(file_info.st_mtime).strftime("%Y-%m-%d %H:%M")
            )
            self.info_events.setText(str(len(self.current_data)))
            
            # Actualizar título del editor
            self.editor_title.setText(f"📝 Editando: {Path(file_path).stem}")
            
            # Cargar datos en la tabla
            self.populate_table(self.current_data)
            
            # Actualizar vista previa
            self.update_preview()
            
            # Resetear estado de modificación
            self.is_modified = False
            self.update_modified_state()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar plantilla: {str(e)}")
            
    def populate_table(self, data):
        """Poblar tabla con datos de la plantilla"""
        self.table.setRowCount(0)
        
        for event_data in data:
            self.add_table_row_with_data(event_data)
            
    def add_table_row_with_data(self, event_data=None):
        """Agregar una fila a la tabla con datos"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Valores por defecto
        if event_data is None:
            event_data = {
                "enabled": True,
                "name": "Nuevo Evento",
                "type": "General",
                "color": "#3498db",
                "icon": "📌",
                "shortcut": "",
                "time":""
            }
            
        # Checkbox de activo
        checkbox = QCheckBox()
        checkbox.setChecked(event_data.get("enabled", True))
        checkbox.stateChanged.connect(lambda: self.mark_as_modified())
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.setAlignment(Qt.AlignCenter)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, 0, checkbox_widget)
        
        # Nombre
        self.table.setItem(row, 1, QTableWidgetItem(event_data.get("nombre", "")))
        
        # Tipo
        type_combo = QComboBox()
        type_combo.setEditable(True)
        type_combo.addItems(["General", "Defensa", "Ataque", "transicion", "bolapareda", "Táctico"])
        type_combo.setCurrentText(event_data.get("categoria", "Defensa"))
        type_combo.currentTextChanged.connect(lambda: self.mark_as_modified())
        self.table.setCellWidget(row, 2, type_combo)
        
        # Color
        color_btn = QPushButton()
        color = event_data.get("color", "#3498db")
        color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid #000;")
        color_btn.setProperty("color", color)
        color_btn.clicked.connect(lambda: self.select_color(color_btn))
        self.table.setCellWidget(row, 3, color_btn)
        
        # Icono
        icon = event_data.get("icon", "📌")
        icon_edit = QPushButton(f"{icon}" )
        #icono = QIcon(icon)
        #icon_edit.setStyleSheet(f"background-color: {color}; border: 1px solid #000;")
        #icon_edit.setIcon(icono)
        icon_edit.clicked.connect(lambda: self.select_icon(event_data,row))
        self.table.setCellWidget(row, 4, icon_edit)
        '''
        icon_edit = QLineEdit(event_data.get("icon", "📌"))
        icon_edit.setMaxLength(2)
        icon_edit.setAlignment(Qt.AlignCenter)
        icon_edit.textChanged.connect(lambda: self.mark_as_modified())
        self.table.setCellWidget(row, 4, icon_edit)
        '''
        # Atajo
        shortcut_edit = QLineEdit(event_data.get("shortcut", ""))
        shortcut_edit.setPlaceholderText("F1, Ctrl+1...")
        shortcut_edit.textChanged.connect(lambda: self.mark_as_modified())
        self.table.setCellWidget(row, 5, shortcut_edit)
        
        # Tiempo
        time_edit = QLineEdit(event_data.get("time", ""))
        time_edit.setPlaceholderText("00:00:00")
        time_edit.textChanged.connect(lambda: self.mark_as_modified())
        self.table.setCellWidget(row, 6, time_edit)
        
        #self.table.setItem(row, 6, QTableWidgetItem(event_data.get("time", "")))
        '''
        # Tags
        tags_text = ", ".join(event_data.get("tags", []))
        #self.table.setItem(row, 7, QTableWidgetItem(tags_text))
        
        # Acciones
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(2)
        
        btn_duplicate = QPushButton("📋")
        btn_duplicate.setToolTip("Duplicar fila")
        btn_duplicate.setFixedSize(25, 25)
        btn_duplicate.clicked.connect(lambda: self.duplicate_row(row))
        actions_layout.addWidget(btn_duplicate)
        
        btn_delete = QPushButton("🗑")
        btn_delete.setToolTip("Eliminar fila")
        btn_delete.setFixedSize(25, 25)
        btn_delete.clicked.connect(lambda: self.delete_row(row))
        actions_layout.addWidget(btn_delete)
        
        #self.table.setCellWidget(row, 8, actions_widget)
        '''
    def add_table_row(self):
        """Agregar nueva fila vacía a la tabla"""
        self.add_table_row_with_data()
        self.mark_as_modified()
        self.update_preview()
        
    def delete_table_row(self):
        """Eliminar filas seleccionadas de la tabla"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
            
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)
            
        self.mark_as_modified()
        self.update_preview()
        
    def delete_row(self, row):
        """Eliminar una fila específica"""
        self.table.removeRow(row)
        self.mark_as_modified()
        self.update_preview()
        
    def duplicate_row(self, row):
        """Duplicar una fila específica"""
        # Obtener datos de la fila
        event_data = self.get_row_data(row)
        event_data["name"] = event_data["name"] + " (copia)"
        
        # Agregar nueva fila con los datos
        self.add_table_row_with_data(event_data)
        self.mark_as_modified()
        self.update_preview()
        
    def move_row_up(self):
        """Mover fila seleccionada hacia arriba"""
        current_row = self.table.currentRow()
        if current_row > 0:
            self.swap_rows(current_row, current_row - 1)
            self.table.setCurrentCell(current_row - 1, 0)
            self.mark_as_modified()
            
    def move_row_down(self):
        """Mover fila seleccionada hacia abajo"""
        current_row = self.table.currentRow()
        if current_row < self.table.rowCount() - 1:
            self.swap_rows(current_row, current_row + 1)
            self.table.setCurrentCell(current_row + 1, 0)
            self.mark_as_modified()
            
    def swap_rows(self, row1, row2):
        """Intercambiar dos filas"""
        # Obtener datos de ambas filas
        data1 = self.get_row_data(row1)
        data2 = self.get_row_data(row2)
        
        # Eliminar ambas filas
        self.table.removeRow(max(row1, row2))
        self.table.removeRow(min(row1, row2))
        
        # Insertar en orden inverso
        self.table.insertRow(min(row1, row2))
        self.add_table_row_with_data(data2)
        self.table.insertRow(max(row1, row2))
        self.add_table_row_with_data(data1)
        
    def get_row_data(self, row):
        """Obtener datos de una fila como diccionario"""
        checkbox_widget = self.table.cellWidget(row, 0)
        checkbox = checkbox_widget.findChild(QCheckBox)
        
        type_combo = self.table.cellWidget(row, 2)
        color_btn = self.table.cellWidget(row, 3)
        icon_edit = self.table.cellWidget(row, 4)
        shortcut_edit = self.table.cellWidget(row, 5)
        time_edit = self.table.cellWidget(row, 6)
        
        #tags_text = self.table.item(row, 7).text() if self.table.item(row, 7) else ""
        #tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
        
        return {
            "enabled": checkbox.isChecked() if checkbox else True,
            "id":self.table.item(row, 1).text() if self.table.item(row, 1) else "",
            "nombre": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
            "categoria": type_combo.currentText() if type_combo else "",
            "color": color_btn.property("color") if color_btn else "#3498db",
            "icon": icon_edit.text() if icon_edit else "📌",
            "shortcut": shortcut_edit.text() if shortcut_edit else "",
            "time": time_edit.text() if time_edit else ""
        }
        
    def get_table_data(self):
        """Obtener todos los datos de la tabla como lista"""
        data = []
        for row in range(self.table.rowCount()):
            data.append(self.get_row_data(row))
        return data
        
    def select_color(self, button):
        """Seleccionar color para un evento"""
        current_color = button.property("color") or "#3498db"
        color = QColorDialog.getColor(QColor(current_color), self, "Seleccionar Color")
        
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #000;")
            button.setProperty("color", color.name())
            self.mark_as_modified()
            self.update_preview()
    def select_icon(self, button,row):
        """Seleccionar color para un evento"""
        #current_color = button.property("icon" or "📌")
        
        dialog = IconPickerWindow(button,row)
        dialog.icon_selected.connect(self.on_icon_selected)
        dialog.exec_()
        
        

            
    def update_preview(self):
        """Actualizar panel de vista previa"""
        # Limpiar vista previa anterior
        while self.preview_layout.count():
            child = self.preview_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Crear botones de vista previa
        data = self.get_table_data()
        for event in data:
            if not event.get("enabled", True):
                continue
                
            btn = QPushButton(f"{event['icon']} {event['nombre']}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {event['color']};
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {event['color']}dd;
                }}
            """)
            
            if event.get("shortcut"):
                btn.setToolTip(f"Atajo: {event['shortcut']}")
                
            self.preview_layout.addWidget(btn)
            
        # Agregar espaciador al final
        self.preview_layout.addStretch()
        
    def mark_as_modified(self):
        """Marcar el archivo actual como modificado"""
        self.is_modified = True
        self.update_modified_state()
        
    def update_modified_state(self):
        """Actualizar indicadores de estado de modificación"""
        if self.is_modified:
            self.modified_label.setText("● Modificado")
            self.btn_save.setEnabled(True)
        else:
            self.modified_label.setText("")
            self.btn_save.setEnabled(False)
            
    def on_table_item_changed(self, item):
        """Manejar cambios en items de la tabla"""
        self.mark_as_modified()
        self.update_preview()
        
    def save_current_template(self):
        """Guardar plantilla actual"""
        if not self.current_file or self.current_file == "NEW":
            # Pedir nombre para nueva plantilla
            name, ok = QInputDialog.getText(
                self,
                "Nueva Plantilla",
                "Nombre de la plantilla:",
                text="nueva_plantilla"
            )
            
            if not ok or not name:
                return
                
            # Asegurar extensión .json
            if not name.endswith('.json'):
                name += '.json'
                
            self.current_file = str(self.templates_dir / name)
            
        # Obtener datos de la tabla
        data = self.get_table_data()
        
        try:
            # Guardar en archivo
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.is_modified = False
            self.update_modified_state()
            
            # Actualizar lista de archivos
            self.load_file_list()
            
            # Mostrar mensaje de éxito
            QMessageBox.information(self, "Guardado", "Plantilla guardada correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar plantilla: {str(e)}")
            
    def create_new_template(self):
        """Crear nueva plantilla"""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Cambios sin guardar",
                "¿Desea guardar los cambios antes de crear una nueva plantilla?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_current_template()
            elif reply == QMessageBox.Cancel:
                return
                
        # Limpiar tabla
        self.table.setRowCount(0)
        self.current_file = "NEW"
        self.current_data = []
        
        # Agregar algunas filas de ejemplo
        default_events = [
            {"name": "Inicio", "type": "General", "color": "#27ae60", "icon": "▶", "shortcut": "F1"},
            {"name": "Pausa", "type": "General", "color": "#f39c12", "icon": "⏸", "shortcut": "F2"},
            {"name": "Final", "type": "General", "color": "#e74c3c", "icon": "■", "shortcut": "F3"},
        ]
        
        for event in default_events:
            self.add_table_row_with_data(event)
            
        self.editor_title.setText("📝 Nueva Plantilla")
        self.is_modified = True
        self.update_modified_state()
        self.update_preview()
        
    def duplicate_template(self):
        """Duplicar plantilla seleccionada"""
        current_item = self.file_list.currentItem()
        if not current_item or current_item.data(Qt.UserRole) == "NEW":
            QMessageBox.warning(self, "Advertencia", "Seleccione una plantilla para duplicar")
            return
            
        # Obtener nombre para la copia
        original_name = current_item.text()
        new_name, ok = QInputDialog.getText(
            self,
            "Duplicar Plantilla",
            "Nombre de la nueva plantilla:",
            text=f"{original_name}_copia"
        )
        
        if not ok or not new_name:
            return
            
        try:
            # Leer plantilla original
            original_path = current_item.data(Qt.UserRole)
            with open(original_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Guardar copia
            if not new_name.endswith('.json'):
                new_name += '.json'
            new_path = self.templates_dir / new_name
            
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            # Actualizar lista
            self.load_file_list()
            
            QMessageBox.information(self, "Éxito", "Plantilla duplicada correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al duplicar plantilla: {str(e)}")
            
    def delete_template(self):
        """Eliminar plantilla seleccionada"""
        current_item = self.file_list.currentItem()
        if not current_item or current_item.data(Qt.UserRole) == "NEW":
            QMessageBox.warning(self, "Advertencia", "Seleccione una plantilla para eliminar")
            return
            
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar la plantilla '{current_item.text()}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                file_path = Path(current_item.data(Qt.UserRole))
                file_path.unlink()
                
                # Si es el archivo actual, limpiar editor
                if str(file_path) == self.current_file:
                    self.table.setRowCount(0)
                    self.current_file = None
                    self.current_data = []
                    self.editor_title.setText("📝 Editor de Plantilla")
                    
                # Actualizar lista
                self.load_file_list()
                
                QMessageBox.information(self, "Éxito", "Plantilla eliminada correctamente")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar plantilla: {str(e)}")
                
    def import_template(self):
        """Importar plantilla desde archivo externo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Plantilla",
            "",
            "Archivos JSON (*.json);;Todos los archivos (*.*)"
        )
        
        if file_path:
            try:
                # Copiar archivo al directorio de plantillas
                import shutil
                dest_path = self.templates_dir / Path(file_path).name
                shutil.copy2(file_path, dest_path)
                
                # Actualizar lista
                self.load_file_list()
                
                QMessageBox.information(self, "Éxito", "Plantilla importada correctamente")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al importar plantilla: {str(e)}")
                
    def export_template(self):
        """Exportar plantilla actual"""
        if not self.current_file or self.current_file == "NEW":
            QMessageBox.warning(self, "Advertencia", "No hay plantilla para exportar")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Plantilla",
            Path(self.current_file).name,
            "Archivos JSON (*.json)"
        )
        
        if file_path:
            try:
                data = self.get_table_data()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
                QMessageBox.information(self, "Éxito", "Plantilla exportada correctamente")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar plantilla: {str(e)}")
                
    def import_from_csv(self):
        """Importar eventos desde archivo CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar desde CSV",
            "",
            "Archivos CSV (*.csv)"
        )
        
        if file_path:
            try:
                import csv
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        event_data = {
                            "enabled": row.get("enabled", "true").lower() == "true",
                            "name": row.get("name", ""),
                            "type": row.get("type", "General"),
                            "color": row.get("color", "#3498db"),
                            "icon": row.get("icon", "📌"),
                            "shortcut": row.get("shortcut", ""),
                            "description": row.get("description", ""),
                            "tags": row.get("tags", "").split(",") if row.get("tags") else []
                        }
                        self.add_table_row_with_data(event_data)
                        
                self.mark_as_modified()
                self.update_preview()
                QMessageBox.information(self, "Éxito", "Datos importados desde CSV")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al importar CSV: {str(e)}")
                
    def export_to_csv(self):
        """Exportar tabla a archivo CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar a CSV",
            "eventos.csv",
            "Archivos CSV (*.csv)"
        )
        
        if file_path:
            try:
                import csv
                data = self.get_table_data()
                
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    if data:
                        # Preparar datos para CSV
                        csv_data = []
                        for event in data:
                            csv_row = event.copy()
                            csv_row["tags"] = ",".join(event.get("tags", []))
                            csv_row["enabled"] = str(event.get("enabled", True))
                            csv_data.append(csv_row)
                            
                        writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                        writer.writeheader()
                        writer.writerows(csv_data)
                        
                QMessageBox.information(self, "Éxito", "Datos exportados a CSV")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar CSV: {str(e)}")
                
    def show_file_context_menu(self, position):
        """Mostrar menú contextual para archivos"""
        item = self.file_list.itemAt(position)
        if not item or item.data(Qt.UserRole) == "NEW":
            return
            
        menu = QMenu(self)
        
        action_open = QAction("📂 Abrir", menu)
        action_open.triggered.connect(lambda: self.load_template(item.data(Qt.UserRole)))
        menu.addAction(action_open)
        
        action_duplicate = QAction("📋 Duplicar", menu)
        action_duplicate.triggered.connect(self.duplicate_template)
        menu.addAction(action_duplicate)
        
        action_rename = QAction("✏️ Renombrar", menu)
        action_rename.triggered.connect(lambda: self.rename_template(item))
        menu.addAction(action_rename)
        
        menu.addSeparator()
        
        action_delete = QAction("🗑️ Eliminar", menu)
        action_delete.triggered.connect(self.delete_template)
        menu.addAction(action_delete)
        
        menu.exec_(self.file_list.mapToGlobal(position))
        
    def show_table_context_menu(self, position):
        """Mostrar menú contextual para la tabla"""
        menu = QMenu(self)
        
        action_add = QAction("➕ Agregar evento", menu)
        action_add.triggered.connect(self.add_table_row)
        menu.addAction(action_add)
        
        if self.table.currentRow() >= 0:
            action_duplicate = QAction("📋 Duplicar fila", menu)
            action_duplicate.triggered.connect(
                lambda: self.duplicate_row(self.table.currentRow())
            )
            menu.addAction(action_duplicate)
            
            action_delete = QAction("🗑️ Eliminar fila", menu)
            action_delete.triggered.connect(
                lambda: self.delete_row(self.table.currentRow())
            )
            menu.addAction(action_delete)
            
            menu.addSeparator()
            
            action_move_up = QAction("⬆ Mover arriba", menu)
            action_move_up.triggered.connect(self.move_row_up)
            menu.addAction(action_move_up)
            
            action_move_down = QAction("⬇ Mover abajo", menu)
            action_move_down.triggered.connect(self.move_row_down)
            menu.addAction(action_move_down)
            
        menu.exec_(self.table.mapToGlobal(position))
        
    def rename_template(self, item):
        """Renombrar una plantilla"""
        old_name = item.text()
        new_name, ok = QInputDialog.getText(
            self,
            "Renombrar Plantilla",
            "Nuevo nombre:",
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            try:
                old_path = Path(item.data(Qt.UserRole))
                if not new_name.endswith('.json'):
                    new_name += '.json'
                new_path = old_path.parent / new_name
                
                old_path.rename(new_path)
                
                # Si es el archivo actual, actualizar referencia
                if str(old_path) == self.current_file:
                    self.current_file = str(new_path)
                    
                self.load_file_list()
                
                QMessageBox.information(self, "Éxito", "Plantilla renombrada correctamente")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al renombrar: {str(e)}")
                
    def setup_shortcuts(self):
        """Configurar atajos de teclado"""
        # Guardar
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_current_template)
        
        # Nueva plantilla
        QShortcut(QKeySequence("Ctrl+N"), self, self.create_new_template)
        
        # Agregar fila
        QShortcut(QKeySequence("Ctrl+Plus"), self, self.add_table_row)
        
        # Eliminar fila
        QShortcut(QKeySequence("Delete"), self, self.delete_table_row)
        
    def apply_and_close(self):
        """Aplicar plantilla seleccionada y cerrar"""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Cambios sin guardar",
                "¿Desea guardar los cambios antes de cerrar?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_current_template()
            elif reply == QMessageBox.Cancel:
                return
             
        
        current_item = self.file_list.currentItem()
        if not current_item or current_item.data(Qt.UserRole) == "NEW":
            QMessageBox.warning(self, "Advertencia", "Seleccione una plantilla para duplicar")
            return   
        
        
        # Emitir datos d
        # e la plantilla actual
        data = self.get_table_data()
        isChecked = self.checkDefaultTemplate.isChecked()
        self.template_selected.emit({"events": data},isChecked)
        #self.template_selected.emit(current_item.data(Qt.UserRole))
        self.accept()
        
    def closeEvent(self, event):
        """Manejar cierre del diálogo"""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Cambios sin guardar",
                "¿Desea guardar los cambios antes de cerrar?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_current_template()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def on_icon_selected(self, icon,row):
        """Manejar icono seleccionado desde el selector"""
        """Manejar cambios en items de la tabla"""
        data = self.get_row_data(row)
        self.table.cellWidget(row, 4).setText(icon['emoji'])
        self.mark_as_modified()
        self.update_preview()
            
# Ejemplo de uso
def main():
    app = QApplication(sys.argv)
    
    # Crear directorio de plantillas de ejemplo
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Crear algunas plantillas de ejemplo
    sample_templates = {
        "futbol.json": [
            {"name": "Gol", "type": "Ataque", "color": "#FFD700", "icon": "⚽", "shortcut": "F1", "enabled": True, "tags": ["importante"]},
            {"name": "Tarjeta", "type": "Disciplina", "color": "#FF0000", "icon": "🟥", "shortcut": "F2", "enabled": True, "tags": []},
            {"name": "Córner", "type": "Jugada", "color": "#2196F3", "icon": "📐", "shortcut": "F3", "enabled": True, "tags": []},
        ],
        "basquet.json": [
            {"name": "Triple", "type": "Ataque", "color": "#FF9800", "icon": "3️⃣", "shortcut": "F1", "enabled": True, "tags": ["puntos"]},
            {"name": "Falta", "type": "Defensa", "color": "#F44336", "icon": "✋", "shortcut": "F2", "enabled": True, "tags": []},
        ]
    }
    
    for filename, events in sample_templates.items():
        file_path = templates_dir / filename
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
    
    # Mostrar diálogo
    dialog = TemplateManagerDialog(str(templates_dir))
    dialog.template_selected.connect(lambda data: print("Plantilla seleccionada:", data))
    
    if dialog.exec_():
        print("Diálogo aceptado")
    else:
        print("Diálogo cancelado")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()