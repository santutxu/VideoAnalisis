from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,QTableWidget,QTableWidgetItem,
    QMenu, QAction, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Optional
from datetime import datetime
import uuid
from events_module.tactical_event import TacticalEvent
from events_module.tactical_event_edit_dialog import TacticalEventEditDialog
from .tactical_event_manager import TacticalEventManager

class TacticalEventListWidget(QWidget):
    """Widget de lista de eventos con funciones de edición y eliminación."""
    EVENT_TYPES = {        'pinicial': {'id':'pinicial','name':'P.Inicio','icon': '🟨', 'color': '#FFC107', 'categoria': 'Defensa','time':'10'},
        'acciond': {'id':'acciond','name':'Accion Def','icon': '📊', 'color': '#FFC107', 'categoria': 'Defensa','time':'10'},
        'desajuste':{'id':'desajuste','name':'Desajuste','icon': '❗', 'color': '#FFC107', 'categoria': 'Defensa','time':'10'},
        'contruccion': {'id':'contruccion','name':'Construccion','icon': '🔄', 'color': "#FF6A07", 'categoria': 'Ataque','time':'10'},
        'finalizacion': {'id':'finalizacion','name':'Finalizacion','icon': '🎯', 'color': '#FF6A07', 'categoria': 'Ataque','time':'5'},
        'perdida': {'id':'perdida','name':'Perdida','icon': '🎯', 'color': '#FF6A07', 'categoria': 'Ataque','time':'5'},
        'repliegue': {'id':'repliegue','name':'Repliegue','icon': '↩️', 'color': '#2196F3', 'categoria': 'transicion','time':'5'},
        'contra':   {'id':'contra','name':'Contraataque','icon': '⚡', 'color': '#2196F3', 'categoria': 'transicion','time':'5'},
        'p_lan':   {'id':'p_lanzado','name':'P.L','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'p_rec':   {'id':'p_rec','name':'P.R.','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'fd_lan':   {'id':'fd_lan','name':'F.D.L','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'fd_rec':   {'id':'fd_rec','name':'F.D.R','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'fa_lan':   {'id':'fa_lan','name':'Falta.L','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'fa_rec':   {'id':'fa_rec','name':'Falta.R','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'gol':   {'id':'gol','name':'GOL','icon': '⚡', 'color': "#E620E6", 'categoria': 'gol','time':'5'},
        'gol_rec':   {'id':'gol_rec','name':'GOL R','icon': '⚡', 'color': '#E620E6', 'categoria': 'gol','time':'5'},
    }
    event_selected = pyqtSignal(TacticalEvent)
    event_deleted = pyqtSignal(TacticalEvent)
    event_updated = pyqtSignal(TacticalEvent, TacticalEvent)  # old, new
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = TacticalEventManager()
        self.selected_event: Optional[TacticalEvent] = None
        self.init_ui()
        self.setup_context_menu()
        
        # Conectar callbacks del manager
        self.manager.on_event_removed = self.on_event_removed
        self.manager.on_event_updated = self.on_event_updated
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        
        # Botón Editar
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_edit.setEnabled(False)
        self.btn_edit.clicked.connect(self.edit_selected_event)
        self.btn_edit.setStyleSheet("""
            QPushButton {
                background: #f39c12;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e67e22;
            }
            QPushButton:disabled {
                background: #bdc3c7;
            }
        """)
        toolbar_layout.addWidget(self.btn_edit)
        
        # Botón Eliminar
        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self.delete_selected_event)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c0392b;
            }
            QPushButton:disabled {
                background: #bdc3c7;
            }
        """)
        toolbar_layout.addWidget(self.btn_delete)
        
        # Botón Duplicar
        self.btn_duplicate = QPushButton("📋 Duplicar")
        self.btn_duplicate.setEnabled(False)
        self.btn_duplicate.clicked.connect(self.duplicate_selected_event)
        self.btn_duplicate.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:disabled {
                background: #bdc3c7;
            }
        """)
        toolbar_layout.addWidget(self.btn_duplicate)
        
        toolbar_layout.addStretch()
        
        # Botones Deshacer/Rehacer
        self.btn_undo = QPushButton("↶ Deshacer")
        self.btn_undo.clicked.connect(self.undo)
        self.btn_undo.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        toolbar_layout.addWidget(self.btn_undo)
        
        self.btn_redo = QPushButton("↷ Rehacer")
        self.btn_redo.clicked.connect(self.redo)
        self.btn_redo.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        toolbar_layout.addWidget(self.btn_redo)
        
        layout.addWidget(toolbar)
        
        # Tabla de eventos
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Nombre", "Tipo", "Inicio", "Fin", "Duración", "Acciones"
        ])
        
        # Configurar tabla
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
                # Habilitar menú contextual
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        # Ajustar columnas
        header = self.table.horizontalHeader()
        #header.setSectionResizeMode(0, QHeaderView.Stretch)
        #header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        layout.addWidget(self.table)
        
        # Panel de información
        self.info_panel = QTextEdit()
        self.info_panel.setReadOnly(True)
        self.info_panel.setMaximumHeight(100)
        self.info_panel.setPlaceholderText("Selecciona un evento para ver detalles...")
        layout.addWidget(self.info_panel)
        
    def add_event(self, event: TacticalEvent):
        """Agrega un evento a la lista."""
        self.manager.add_event(event)
        self.refresh_table()
        
    def refresh_table(self):
        """Actualiza la tabla con los eventos actuales."""
        self.table.setRowCount(len(self.manager.events))
        
        for row, event in enumerate(self.manager.events):
            # Nombre
            self.table.setItem(row, 0, QTableWidgetItem(event.event_name))
            
            # Tipo
            self.table.setItem(row, 1, QTableWidgetItem(event.event_type))
            
            # Inicio
            self.table.setItem(row, 2, QTableWidgetItem(f"{event.event_start:.2f}s"))
            
            # Fin
            self.table.setItem(row, 3, QTableWidgetItem(f"{event.event_end:.2f}s"))
            
            # Duración
            duration = event.event_end - event.event_start
            self.table.setItem(row, 4, QTableWidgetItem(f"{duration:.2f}s"))
            
            # Minuto
            #minute_text = f"{event.match_minute}'" if event.match_minute else "-"
            #self.table.setItem(row, 5, QTableWidgetItem(minute_text))
            
            # Tags
            #tags_text = ", ".join(event.tags) if event.tags else "-"
            #self.table.setItem(row, 6, QTableWidgetItem(tags_text))
            
            # Botones de acción rápida
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            btn_quick_edit = QPushButton("✏️")
            btn_quick_edit.setToolTip("Edición rápida")
            btn_quick_edit.setFixedSize(25, 25)
            btn_quick_edit.clicked.connect(lambda checked, e=event: self.quick_edit_event(e))
            actions_layout.addWidget(btn_quick_edit)
            
            btn_quick_delete = QPushButton("🗑️")
            btn_quick_delete.setToolTip("Eliminar")
            btn_quick_delete.setFixedSize(25, 25)
            btn_quick_delete.clicked.connect(lambda checked, e=event: self.quick_delete_event(e))
            actions_layout.addWidget(btn_quick_delete)
            
            self.table.setCellWidget(row, 5, actions_widget)
            
            # Guardar referencia al evento en la fila
            self.table.item(row, 0).setData(Qt.UserRole, event.id)
            
    def on_selection_changed(self):
        """Maneja el cambio de selección en la tabla."""
        selected_rows = self.table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            event_id = self.table.item(row, 0).data(Qt.UserRole)
            self.selected_event = self.manager.find_event(event_id)
            
            # Habilitar botones
            self.btn_edit.setEnabled(True)
            self.btn_delete.setEnabled(True)
            self.btn_duplicate.setEnabled(True)
            
            # Mostrar información detallada
            self.show_event_info(self.selected_event)
            self.create_single_item_menu(row)
            
            # Emitir señal
            self.event_selected.emit(self.selected_event)
        else:
            self.selected_event = None
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_duplicate.setEnabled(False)
            self.info_panel.clear()
            
    def show_event_info(self, event: TacticalEvent):
        """Muestra información detallada del evento."""
        info = f"""
        <b>ID:</b> {event.id}<br>
        <b>Nombre:</b> {event.event_name}<br>
        <b>Tipo:</b> {event.event_type}<br>
        <b>Tiempo:</b> {event.event_start:.3f}s - {event.event_end:.3f}s<br>
        <b>Duración:</b> {event.event_end - event.event_start:.3f}s<br>
        <b>Creado:</b> {event.created_at}<br>
        """
        '''
        if event.coordinates:
            info += f"<b>Coordenadas:</b> X={event.coordinates['x']:.3f}, Y={event.coordinates['y']:.3f}<br>"
        
        if event.tags:
            info += f"<b>Tags:</b> {', '.join(event.tags)}<br>"
        '''    
        self.info_panel.setHtml(info)
        
    def edit_selected_event(self):
        """Abre el diálogo de edición para el evento seleccionado."""
        if not self.selected_event:
            return
            
        dialog = TacticalEventEditDialog(self.selected_event, self)
        if dialog.exec_():
            updated_event = dialog.get_updated_event()
            
            # Actualizar en el manager
            success = self.manager.replace_event(self.selected_event.id, updated_event)
            
            if success:
                self.refresh_table()
                QMessageBox.information(self, "Éxito", "Evento actualizado correctamente")
            else:
                QMessageBox.warning(self, "Error", "No se pudo actualizar el evento")
                
    def delete_selected_event(self):
        """Elimina el evento seleccionado con confirmación."""
        if not self.selected_event:
            return
            
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el evento '{self.selected_event.event_name}'?\n"
            f"Tiempo: {self.selected_event.event_start:.2f}s - {self.selected_event.event_end:.2f}s",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.manager.remove_event(self.selected_event)
            
            if success:
                self.refresh_table()
                self.selected_event = None
                QMessageBox.information(self, "Éxito", "Evento eliminado correctamente")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el evento")
                
    def quick_edit_event(self, event: TacticalEvent):
        """Edición rápida de un evento desde la tabla."""
        dialog = TacticalEventEditDialog(event, self)
        if dialog.exec_():
            updated_event = dialog.get_updated_event()
            self.manager.replace_event(event.id, updated_event)
            self.refresh_table()
            
    def quick_delete_event(self, event: TacticalEvent):
        """Eliminación rápida de un evento desde la tabla."""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar '{event.event_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.manager.remove_event(event)
            self.refresh_table()
            
    def duplicate_selected_event(self):
        """Duplica el evento seleccionado."""
        if not self.selected_event:
            return
            
        # Crear copia con nuevo ID
        new_event = self.selected_event.copy()
        new_event.id = str(uuid.uuid4())
        new_event.event_name = f"{new_event.event_name} (copia)"
        new_event.created_at = datetime.now().isoformat()
        
        # Abrir diálogo de edición para la copia
        dialog = TacticalEventEditDialog(new_event, self)
        if dialog.exec_():
            duplicated_event = dialog.get_updated_event()
            self.manager.add_event(duplicated_event)
            self.refresh_table()
            
    def undo(self):
        """Deshacer última operación."""
        if self.manager.undo():
            self.refresh_table()
            QMessageBox.information(self, "Deshacer", "Operación deshecha")
        else:
            QMessageBox.information(self, "Deshacer", "No hay operaciones para deshacer")
            
    def redo(self):
        """Rehacer operación."""
        if self.manager.redo():
            self.refresh_table()
            QMessageBox.information(self, "Rehacer", "Operación rehecha")
        else:
            QMessageBox.information(self, "Rehacer", "No hay operaciones para rehacer")
            
    def on_event_removed(self, event: TacticalEvent):
        """Callback cuando se elimina un evento."""
        self.event_deleted.emit(event)
        
    def on_event_updated(self, old_event: TacticalEvent, new_event: TacticalEvent):
        """Callback cuando se actualiza un evento."""
        self.event_updated.emit(old_event, new_event)
        
    def delete_event_by_info(self, event_info: dict) -> bool:
        """
        Elimina un evento basándose en información parcial.
        
        Args:
            event_info: Diccionario con información del evento
            
        Returns:
            True si se eliminó, False si no se encontró
        """
        removed_events = self.manager.remove_events_by_criteria(**event_info)
        
        if removed_events:
            self.refresh_table()
            return True
        return False
    
    def setup_context_menu(self):
        """Configura el menú contextual."""
        self.context_menu = QMenu(self)
        
        # Estilo del menú
        self.context_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #3498db;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: #ddd;
                margin: 5px 10px;
            }
            QMenu::icon {
                margin-right: 8px;
            }
        """)
            
    def show_context_menu(self, position):
        """Muestra menú contextual para eventos."""
        self.context_menu.clear()
        selected_rows = set()
        
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
            
        
        num_selected = len(selected_rows)
        
        
        if num_selected == 0:
            # Menú para área vacía
            self.create_empty_area_menu()
        #elif num_selected == 1:
            # Menú para un solo elemento
            #self.create_single_item_menu(list(selected_rows)[0])
        else:
            # Menú para múltiples elementos
            self.create_multi_item_menu(selected_rows)
            
        # Mostrar menú
        self.context_menu.exec_(self.table.mapToGlobal(position))
        
        
        '''
        item = self.events_tree.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        
        # Ir al evento
        jump_action = QAction("▶️ Ir al evento", self)
        jump_action.triggered.connect(lambda: self.jump_to_event(item))
        menu.addAction(jump_action)
        
        menu.addSeparator()
        
        # Editar
        edit_action = QAction("✏️ Editar", self)
        edit_action.triggered.connect(lambda: self.edit_event(item))
        menu.addAction(edit_action)
        
        # Eliminar
        delete_action = QAction("🗑️ Eliminar", self)
        delete_action.triggered.connect(lambda: self.delete_event(item))
        menu.addAction(delete_action)
        
        menu.exec_(self.events_tree.mapToGlobal(position))
        '''
    
    def create_single_item_menu(self, row):
        """Crea menú contextual para un solo elemento."""
        event_id = self.table.item(row, 1).data(Qt.UserRole)
        event = self.manager.find_event(event_id)
        
        if not event:
            return
            
        # === Sección: Acciones principales ===
        action_edit = QAction("✏️ Editar evento", self)
        #action_edit.triggered.connect(lambda: self.edit_event(event))
        self.context_menu.addAction(action_edit)
        
        action_duplicate = QAction("📋 Duplicar", self)
        #action_duplicate.triggered.connect(lambda: self.duplicate_event(event))
        self.context_menu.addAction(action_duplicate)
        
        action_delete = QAction("🗑️ Eliminar", self)
        #action_delete.triggered.connect(lambda: self.delete_event(event))
        self.context_menu.addAction(action_delete)
        
        self.context_menu.addSeparator()
        
        # === Sección: Navegación ===
        action_goto = QAction(f"⏱️ Ir al tiempo ({event.event_start:.2f}s)", self)
        #action_goto.triggered.connect(lambda: self.goto_time.emit(event.event_start))
        #self.context_menu.addAction(action_goto)
        
        action_play_segment = QAction("▶️ Reproducir segmento", self)
        #action_play_segment.triggered.connect(lambda: self.play_segment(event))
        #self.context_menu.addAction(action_play_segment)
        
        self.context_menu.addSeparator()
        
        # === Sección: Edición rápida ===
        quick_edit_menu = QMenu("⚡ Edición rápida", self)
        
        # Cambiar tipo
        type_menu = QMenu("Cambiar tipo", quick_edit_menu)
        for event_type in ["Ataque", "Defensa", "Transición", "Pausa", "Otro"]:
            action = QAction(event_type, type_menu)
            #action.triggered.connect(lambda checked, t=event_type: self.quick_change_type(event, t))
            if event.event_type == event_type:
                action.setCheckable(True)
                action.setChecked(True)
            type_menu.addAction(action)
        quick_edit_menu.addMenu(type_menu)
        
        # Agregar/Editar tags
        action_tags = QAction("🏷️ Editar tags...", quick_edit_menu)
        #action_tags.triggered.connect(lambda: self.edit_tags(event))
        quick_edit_menu.addAction(action_tags)
        
        # Agregar nota
        action_note = QAction("📝 Agregar/Editar nota...", quick_edit_menu)
        #action_note.triggered.connect(lambda: self.edit_note(event))
        quick_edit_menu.addAction(action_note)
        
        # Ajustar tiempo
        action_adjust_time = QAction("⏰ Ajustar tiempo...", quick_edit_menu)
        #action_adjust_time.triggered.connect(lambda: self.adjust_time(event))
        quick_edit_menu.addAction(action_adjust_time)
        
        self.context_menu.addMenu(quick_edit_menu)
        
        self.context_menu.addSeparator()
        
        # === Sección: Copiar información ===
        copy_menu = QMenu("📋 Copiar", self)
        
        action_copy_all = QAction("Todo", copy_menu)
        #action_copy_all.triggered.connect(lambda: self.copy_event_info(event, "all"))
        copy_menu.addAction(action_copy_all)
        
        action_copy_name = QAction(f"Nombre: {event.event_name}", copy_menu)
        #action_copy_name.triggered.connect(lambda: self.copy_to_clipboard(event.event_name))
        copy_menu.addAction(action_copy_name)
        
        action_copy_time = QAction(f"Tiempo: {event.event_start:.2f}s", copy_menu)
        #action_copy_time.triggered.connect(lambda: self.copy_to_clipboard(f"{event.event_start:.2f}"))
        copy_menu.addAction(action_copy_time)
        
        action_copy_json = QAction("Como JSON", copy_menu)
        #action_copy_json.triggered.connect(lambda: self.copy_event_as_json(event))
        copy_menu.addAction(action_copy_json)
        
        self.context_menu.addMenu(copy_menu)
        
        # === Sección: Marcadores y colores ===
        marker_menu = QMenu("🎨 Marcador", self)
        
        colors = [
            ("🔴 Rojo", "#e74c3c"),
            ("🟡 Amarillo", "#f39c12"),
            ("🟢 Verde", "#27ae60"),
            ("🔵 Azul", "#3498db"),
            ("🟣 Morado", "#9b59b6"),
            ("⚪ Sin color", None)
        ]
        
        for color_name, color_value in colors:
            action = QAction(color_name, marker_menu)
            #action.triggered.connect(lambda checked, c=color_value: self.set_event_color(event, c))
            marker_menu.addAction(action)
            
        self.context_menu.addMenu(marker_menu)
        
        self.context_menu.addSeparator()
        
        # === Sección: Exportar ===
        export_menu = QMenu("💾 Exportar", self)
        
        action_export_single = QAction("Este evento", export_menu)
        #action_export_single.triggered.connect(lambda: self.export_events([event]))
        export_menu.addAction(action_export_single)
        
        action_export_video_clip = QAction("🎬 Clip de video", export_menu)
        #action_export_video_clip.triggered.connect(lambda: self.export_video_clip(event))
        export_menu.addAction(action_export_video_clip)
        
        self.context_menu.addMenu(export_menu)
        
        # === Sección: Información ===
        self.context_menu.addSeparator()
        
        action_properties = QAction("ℹ️ Propiedades...", self)
        #action_properties.triggered.connect(lambda: self.show_event_properties(event))
        self.context_menu.addAction(action_properties)
        
    def create_multi_item_menu(self, selected_rows):
        """Crea menú contextual para múltiples elementos."""
        num_selected = len(selected_rows)
        
        # Título informativo
        title_action = QAction(f"📌 {num_selected} eventos seleccionados", self)
        title_action.setEnabled(False)
        self.context_menu.addAction(title_action)
        
        self.context_menu.addSeparator()
        
        # === Acciones en lote ===
        action_edit_batch = QAction("✏️ Editar seleccionados...", self)
        action_edit_batch.triggered.connect(self.edit_selected_events)
        self.context_menu.addAction(action_edit_batch)
        
        action_delete_batch = QAction("🗑️ Eliminar seleccionados", self)
        action_delete_batch.triggered.connect(self.delete_selected_events)
        self.context_menu.addAction(action_delete_batch)
        
        self.context_menu.addSeparator()
        
        # === Operaciones en lote ===
        batch_menu = QMenu("⚡ Operaciones en lote", self)
        
        # Cambiar tipo de todos
        type_menu = QMenu("Cambiar tipo a todos", batch_menu)
        for event_type in ["Ataque", "Defensa", "Transición", "Pausa", "Otro"]:
            action = QAction(event_type, type_menu)
            action.triggered.connect(lambda checked, t=event_type: self.batch_change_type(selected_rows, t))
            type_menu.addAction(action)
        batch_menu.addMenu(type_menu)
        
        # Agregar tag a todos
        action_add_tag = QAction("🏷️ Agregar tag...", batch_menu)
        action_add_tag.triggered.connect(lambda: self.batch_add_tag(selected_rows))
        batch_menu.addAction(action_add_tag)
        
        # Ajustar tiempo
        action_shift_time = QAction("⏰ Desplazar tiempo...", batch_menu)
        action_shift_time.triggered.connect(lambda: self.batch_shift_time(selected_rows))
        batch_menu.addAction(action_shift_time)
        
        self.context_menu.addMenu(batch_menu)
        
        self.context_menu.addSeparator()
        
        # === Agrupar/Combinar ===
        action_group = QAction("🔗 Agrupar eventos", self)
        action_group.triggered.connect(lambda: self.group_events(selected_rows))
        self.context_menu.addAction(action_group)
        
        action_merge = QAction("🔀 Combinar en uno", self)
        action_merge.triggered.connect(lambda: self.merge_events(selected_rows))
        self.context_menu.addAction(action_merge)
        
        self.context_menu.addSeparator()
        
        # === Exportar ===
        action_export = QAction(f"💾 Exportar {num_selected} eventos", self)
        action_export.triggered.connect(lambda: self.export_selected_events())
        self.context_menu.addAction(action_export)
        
        # === Análisis ===
        self.context_menu.addSeparator()
        
        action_stats = QAction("📊 Ver estadísticas", self)
        action_stats.triggered.connect(lambda: self.show_selection_stats(selected_rows))
        self.context_menu.addAction(action_stats)
        
    def create_empty_area_menu(self):
        """Crea menú contextual para área vacía."""
        action_add = QAction("➕ Agregar nuevo evento", self)
        action_add.triggered.connect(self.add_new_event)
        self.context_menu.addAction(action_add)
        
        action_paste = QAction("📋 Pegar", self)
        action_paste.setEnabled(self.clipboard_event is not None)
        action_paste.triggered.connect(self.paste_event)
        self.context_menu.addAction(action_paste)
        
        self.context_menu.addSeparator()
        
        action_import = QAction("📥 Importar eventos...", self)
        action_import.triggered.connect(self.import_events)
        self.context_menu.addAction(action_import)
        
        self.context_menu.addSeparator()
        
        # Vista
        view_menu = QMenu("👁️ Vista", self)
        
        action_expand = QAction("Expandir todo", view_menu)
        action_expand.triggered.connect(self.expand_all)
        view_menu.addAction(action_expand)
        
        action_collapse = QAction("Contraer todo", view_menu)
        action_collapse.triggered.connect(self.collapse_all)
        view_menu.addAction(action_collapse)
        
        self.context_menu.addMenu(view_menu)
        
        # Ordenar
        sort_menu = QMenu("↕️ Ordenar por", self)
        
        sort_options = [
            ("Tiempo de inicio", "start"),
            ("Tiempo de fin", "end"),
            ("Duración", "duration"),
            ("Nombre", "name"),
            ("Tipo", "type")
        ]
        
        for name, key in sort_options:
            action = QAction(name, sort_menu)
            action.triggered.connect(lambda checked, k=key: self.sort_by(k))
            sort_menu.addAction(action)
            
        self.context_menu.addMenu(sort_menu)
        

