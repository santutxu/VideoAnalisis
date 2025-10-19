from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime
import uuid
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout,QFormLayout,QDialog,QApplication,
    QTreeWidget, QTreeWidgetItem, QComboBox, QLineEdit,QDoubleSpinBox,QDialogButtonBox,
    QLabel, QGroupBox, QCheckBox, QSpinBox, QTextEdit,QTableWidget,QTableWidgetItem,
    QHeaderView, QMenu, QAction, QInputDialog, QMessageBox,QMainWindow
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QBrush
import sys
@dataclass
class TacticalEvent:
    """Representa un evento táctico en el video."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = 0.0  # Segundos desde inicio del video
    event_name: str = ""  # Nombre del evento, e.g. "pass", "shot"
    event_type: str = ""    # "pass", "shot", "foul", etc.
    coordinates: Optional[Dict[str, float]] = None  # {"x": 0.5, "y": 0.3} normalizado
    match_minute: Optional[int] = None  # Minuto real del partido
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    event_duration: Optional[str] = None 
    event_start: float = 0.0
    event_end: float = 0.0
    
    
    def to_dict(self) -> Dict:
        """Convierte el evento a diccionario para serialización."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TacticalEvent':
        """Crea un evento desde un diccionario."""
        return cls(**data)
    
    
    
    def copy(self) -> 'TacticalEvent':
        """Crear una copia del evento."""
        return replace(self)

class TacticalEventManager:
    """Gestor principal para manejar eventos tácticos."""
    
    def __init__(self):
        self.events: List[TacticalEvent] = []
        self.history: List[dict] = []  # Para deshacer/rehacer
        self.history_index = -1
        self.max_history = 50
        
        # Callbacks para notificar cambios
        self.on_event_added: Optional[Callable] = None
        self.on_event_removed: Optional[Callable] = None
        self.on_event_updated: Optional[Callable] = None
        
    # ============= FUNCIONES DE ELIMINACIÓN =============
    
    def remove_event(self, event: TacticalEvent) -> bool:
        """
        Elimina un evento específico de la lista.
        
        Args:
            event: El evento a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no se encontró
        """
        try:
            # Guardar estado para deshacer
            self._save_history()
            
            # Buscar y eliminar por ID (más seguro)
            for i, e in enumerate(self.events):
                if e.id == event.id:
                    removed_event = self.events.pop(i)
                    
                    # Notificar cambio
                    if self.on_event_removed:
                        self.on_event_removed(removed_event)
                    
                    return True
            return False
            
        except Exception as e:
            print(f"Error al eliminar evento: {e}")
            return False
    
    def remove_event_by_id(self, event_id: str) -> Optional[TacticalEvent]:
        """
        Elimina un evento por su ID único.
        
        Args:
            event_id: ID del evento a eliminar
            
        Returns:
            El evento eliminado o None si no se encontró
        """
        self._save_history()
        
        for i, event in enumerate(self.events):
            if event.id == event_id:
                removed = self.events.pop(i)
                
                if self.on_event_removed:
                    self.on_event_removed(removed)
                    
                return removed
        return None
    
    def remove_events_by_criteria(self, **criteria) -> List[TacticalEvent]:
        """
        Elimina eventos que coincidan con los criterios especificados.
        
        Args:
            **criteria: Criterios de búsqueda (event_name="pase", event_type="Ataque", etc.)
            
        Returns:
            Lista de eventos eliminados
        """
        self._save_history()
        
        removed_events = []
        new_events = []
        
        for event in self.events:
            if self._matches_criteria(event, criteria):
                removed_events.append(event)
            else:
                new_events.append(event)
        
        self.events = new_events
        
        # Notificar cambios
        for event in removed_events:
            if self.on_event_removed:
                self.on_event_removed(event)
        
        return removed_events
    
    def remove_events_in_range(self, start_time: float, end_time: float) -> List[TacticalEvent]:
        """
        Elimina todos los eventos dentro de un rango de tiempo.
        """
        self._save_history()
        
        removed = []
        new_events = []
        
        for event in self.events:
            if start_time <= event.event_start <= end_time:
                removed.append(event)
                if self.on_event_removed:
                    self.on_event_removed(event)
            else:
                new_events.append(event)
        
        self.events = new_events
        return removed
    
    # ============= FUNCIONES DE EDICIÓN =============
    
    def update_event(self, event_id: str, **updates) -> bool:
        """
        Actualiza un evento existente con nuevos valores.
        
        Args:
            event_id: ID del evento a actualizar
            **updates: Campos a actualizar y sus nuevos valores
            
        Returns:
            True si se actualizó correctamente, False si no se encontró
        """
        self._save_history()
        
        for event in self.events:
            if event.id == event_id:
                # Guardar estado anterior para comparación
                old_event = event.copy()
                
                # Actualizar campos
                for key, value in updates.items():
                    if hasattr(event, key):
                        setattr(event, key, value)
                
                # Actualizar timestamp de modificación
                event.created_at = datetime.now().isoformat()
                
                # Notificar cambio
                if self.on_event_updated:
                    self.on_event_updated(old_event, event)
                
                return True
        return False
    
    def replace_event(self, event_id: str, new_event: TacticalEvent) -> bool:
        """
        Reemplaza completamente un evento con otro.
        
        Args:
            event_id: ID del evento a reemplazar
            new_event: Nuevo evento que reemplazará al anterior
        """
        self._save_history()
        
        for i, event in enumerate(self.events):
            if event.id == event_id:
                old_event = self.events[i]
                new_event.id = event_id  # Mantener el mismo ID
                self.events[i] = new_event
                
                if self.on_event_updated:
                    self.on_event_updated(old_event, new_event)
                
                return True
        return False
    
    def batch_update(self, event_ids: List[str], **updates) -> int:
        """
        Actualiza múltiples eventos a la vez.
        
        Returns:
            Número de eventos actualizados
        """
        self._save_history()
        
        updated_count = 0
        for event_id in event_ids:
            if self.update_event(event_id, **updates):
                updated_count += 1
        
        return updated_count
    
    # ============= FUNCIONES AUXILIARES =============
    
    def _matches_criteria(self, event: TacticalEvent, criteria: dict) -> bool:
        """Verifica si un evento coincide con los criterios dados."""
        for key, value in criteria.items():
            if not hasattr(event, key):
                return False
            
            event_value = getattr(event, key)
            
            # Manejo especial para floats
            if isinstance(value, float) and isinstance(event_value, float):
                if abs(event_value - value) > 0.0001:
                    return False
            elif event_value != value:
                return False
        
        return True
    
    def _save_history(self):
        """Guarda el estado actual para poder deshacer."""
        # Serializar estado actual
        current_state = [event.to_dict() for event in self.events]
        
        # Eliminar estados futuros si estamos en medio del historial
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # Agregar nuevo estado
        self.history.append(current_state)
        self.history_index += 1
        
        # Limitar tamaño del historial
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1
    
    def undo(self) -> bool:
        """Deshacer última operación."""
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.events = [TacticalEvent.from_dict(d) for d in state]
            return True
        return False
    
    def redo(self) -> bool:
        """Rehacer operación deshecha."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            state = self.history[self.history_index]
            self.events = [TacticalEvent.from_dict(d) for d in state]
            return True
        return False
    
    def find_event(self, event_id: str) -> Optional[TacticalEvent]:
        """Busca un evento por ID."""
        for event in self.events:
            if event.id == event_id:
                return event
        return None
    
    def add_event(self, event: TacticalEvent):
        """Agrega un nuevo evento."""
        self._save_history()
        self.events.append(event)
        
        if self.on_event_added:
            self.on_event_added(event)
            
class TacticalEventEditDialog(QDialog):
    """Diálogo para editar un evento táctico."""
    
    def __init__(self, event: TacticalEvent, parent=None):
        super().__init__(parent)
        self.event = event.copy()  # Trabajar con una copia
        self.original_event = event
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"Editar Evento - {self.event.event_name}")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Formulario de edición
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # Campo: Nombre del evento
        self.name_edit = QLineEdit(self.event.event_name)
        form_layout.addRow("Nombre del Evento:", self.name_edit)
        
        # Campo: Tipo de evento
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItems(["Ataque", "Defensa", "Transición", "Pausa", "Otro"])
        self.type_combo.setCurrentText(self.event.event_type)
        form_layout.addRow("Tipo de Evento:", self.type_combo)
        
        # Campo: Tiempo de inicio
        self.start_spin = QDoubleSpinBox()
        self.start_spin.setRange(0, 999999)
        self.start_spin.setDecimals(3)
        self.start_spin.setSuffix(" s")
        self.start_spin.setValue(self.event.event_start)
        form_layout.addRow("Tiempo de Inicio:", self.start_spin)
        
        # Campo: Tiempo de fin
        self.end_spin = QDoubleSpinBox()
        self.end_spin.setRange(0, 999999)
        self.end_spin.setDecimals(3)
        self.end_spin.setSuffix(" s")
        self.end_spin.setValue(self.event.event_end)
        form_layout.addRow("Tiempo de Fin:", self.end_spin)
        
        # Campo: Duración (calculada automáticamente)
        self.duration_label = QLabel()
        self.update_duration()
        form_layout.addRow("Duración:", self.duration_label)
        
        # Campo: Minuto del partido
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 120)
        self.minute_spin.setValue(self.event.match_minute or 0)
        self.minute_spin.setSpecialValueText("No especificado")
        form_layout.addRow("Minuto del Partido:", self.minute_spin)
        
        # Campo: Tags
        self.tags_edit = QLineEdit()
        if self.event.tags:
            self.tags_edit.setText(", ".join(self.event.tags))
        self.tags_edit.setPlaceholderText("Separar tags con comas")
        form_layout.addRow("Tags:", self.tags_edit)
        
        # Campo: Coordenadas
        coords_widget = QWidget()
        coords_layout = QHBoxLayout(coords_widget)
        coords_layout.setContentsMargins(0, 0, 0, 0)
        
        self.coord_x_spin = QDoubleSpinBox()
        self.coord_x_spin.setRange(0, 1)
        self.coord_x_spin.setDecimals(3)
        self.coord_x_spin.setSingleStep(0.01)
        
        self.coord_y_spin = QDoubleSpinBox()
        self.coord_y_spin.setRange(0, 1)
        self.coord_y_spin.setDecimals(3)
        self.coord_y_spin.setSingleStep(0.01)
        
        if self.event.coordinates:
            self.coord_x_spin.setValue(self.event.coordinates.get('x', 0))
            self.coord_y_spin.setValue(self.event.coordinates.get('y', 0))
        
        coords_layout.addWidget(QLabel("X:"))
        coords_layout.addWidget(self.coord_x_spin)
        coords_layout.addWidget(QLabel("Y:"))
        coords_layout.addWidget(self.coord_y_spin)
        coords_layout.addStretch()
        
        form_layout.addRow("Coordenadas:", coords_widget)
        
        layout.addWidget(form_widget)
        
        # Información adicional (solo lectura)
        info_group = QGroupBox("Información del Sistema")
        info_layout = QFormLayout(info_group)
        
        id_label = QLabel(self.event.id)
        id_label.setStyleSheet("color: #666; font-family: monospace;")
        info_layout.addRow("ID:", id_label)
        
        created_label = QLabel(self.event.created_at)
        created_label.setStyleSheet("color: #666;")
        info_layout.addRow("Creado:", created_label)
        
        layout.addWidget(info_group)
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        # Conectar señales
        self.start_spin.valueChanged.connect(self.update_duration)
        self.end_spin.valueChanged.connect(self.update_duration)
        
    def update_duration(self):
        """Actualiza la etiqueta de duración."""
        duration = self.end_spin.value() - self.start_spin.value()
        self.duration_label.setText(f"{duration:.3f} segundos")
        
    def get_updated_event(self) -> TacticalEvent:
        """Obtiene el evento con los valores actualizados."""
        self.event.event_name = self.name_edit.text()
        self.event.event_type = self.type_combo.currentText()
        self.event.event_start = self.start_spin.value()
        self.event.event_end = self.end_spin.value()
        self.event.event_duration = str(self.end_spin.value() - self.start_spin.value())
        
        # Minuto del partido
        if self.minute_spin.value() > 0:
            self.event.match_minute = self.minute_spin.value()
        else:
            self.event.match_minute = None
        
        # Tags
        tags_text = self.tags_edit.text().strip()
        if tags_text:
            self.event.tags = [tag.strip() for tag in tags_text.split(',')]
        else:
            self.event.tags = []
        
        # Coordenadas
        if self.coord_x_spin.value() > 0 or self.coord_y_spin.value() > 0:
            self.event.coordinates = {
                'x': self.coord_x_spin.value(),
                'y': self.coord_y_spin.value()
            }
        
        return self.event
    
    
class TacticalEventListWidget(QWidget):
    """Widget de lista de eventos con funciones de edición y eliminación."""
    
    event_selected = pyqtSignal(TacticalEvent)
    event_deleted = pyqtSignal(TacticalEvent)
    event_updated = pyqtSignal(TacticalEvent, TacticalEvent)  # old, new
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = TacticalEventManager()
        self.selected_event: Optional[TacticalEvent] = None
        self.init_ui()
        
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
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Nombre", "Tipo", "Inicio", "Fin", "Duración", "Minuto", "Tags", "Acciones"
        ])
        
        # Configurar tabla
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Ajustar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        
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
            minute_text = f"{event.match_minute}'" if event.match_minute else "-"
            self.table.setItem(row, 5, QTableWidgetItem(minute_text))
            
            # Tags
            tags_text = ", ".join(event.tags) if event.tags else "-"
            self.table.setItem(row, 6, QTableWidgetItem(tags_text))
            
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
            
            self.table.setCellWidget(row, 7, actions_widget)
            
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
        
        if event.coordinates:
            info += f"<b>Coordenadas:</b> X={event.coordinates['x']:.3f}, Y={event.coordinates['y']:.3f}<br>"
        
        if event.tags:
            info += f"<b>Tags:</b> {', '.join(event.tags)}<br>"
            
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
    
    

# ============= APLICACIÓN DE DEMOSTRACIÓN =============

class DemoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_demo_data()
        
    def init_ui(self):
        self.setWindowTitle("Demo - Gestión de Eventos Tácticos")
        self.setGeometry(100, 100, 1200, 700)
        
        # Widget central
        self.event_list = TacticalEventListWidget()
        self.setCentralWidget(self.event_list)
        
        # Conectar señales
        self.event_list.event_selected.connect(self.on_event_selected)
        self.event_list.event_deleted.connect(self.on_event_deleted)
        self.event_list.event_updated.connect(self.on_event_updated)
        
        # Crear menú
        self.create_menu()
        
    def create_menu(self):
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("Archivo")
        
        add_action = QAction("Agregar Evento de Prueba", self)
        add_action.triggered.connect(self.add_test_event)
        file_menu.addAction(add_action)
        
        # Menú de prueba de eliminación
        test_menu = menubar.addMenu("Pruebas")
        
        test_delete_action = QAction("Probar Eliminación por Criterios", self)
        test_delete_action.triggered.connect(self.test_delete_by_criteria)
        test_menu.addAction(test_delete_action)
        
    def load_demo_data(self):
        """Carga datos de demostración."""
        demo_events = [
            TacticalEvent(
                event_name="finalizacion",
                event_type="Ataque",
                event_start=645.0666666666667,
                event_end=650.0666666666667,
                event_duration="5",
                match_minute=22,
                tags=["gol", "importante"],
                coordinates={"x": 0.8, "y": 0.5}
            ),
            TacticalEvent(
                event_name="pase",
                event_type="Construcción",
                event_start=640.0,
                event_end=642.0,
                event_duration="2",
                match_minute=21,
                tags=["preciso"]
            ),
            TacticalEvent(
                event_name="recuperación",
                event_type="Defensa",
                event_start=635.0,
                event_end=637.0,
                event_duration="2",
                match_minute=21,
                tags=["presión alta"]
            ),
        ]
        
        for event in demo_events:
            self.event_list.add_event(event)
            
    def add_test_event(self):
        """Agrega un evento de prueba."""
        event = TacticalEvent(
            event_name=f"Evento {datetime.now().strftime('%H:%M:%S')}",
            event_type="Prueba",
            event_start=100.0,
            event_end=105.0,
            event_duration="5"
        )
        self.event_list.add_event(event)
        
    def test_delete_by_criteria(self):
        """Prueba la eliminación por criterios."""
        # Esta es la información que proporcionaste
        event_info = {
            'event_duration': '5',
            'event_end': 650.0666666666667,
            'event_name': 'finalizacion',
            'event_start': 645.0666666666667,
            'event_type': 'Ataque'
        }
        
        success = self.event_list.delete_event_by_info(event_info)
        
        if success:
            QMessageBox.information(self, "Éxito", "Evento eliminado por criterios")
        else:
            QMessageBox.warning(self, "No encontrado", "No se encontró evento con esos criterios")
            
    def on_event_selected(self, event: TacticalEvent):
        print(f"Evento seleccionado: {event.event_name}")
        
    def on_event_deleted(self, event: TacticalEvent):
        print(f"Evento eliminado: {event.event_name}")
        
    def on_event_updated(self, old_event: TacticalEvent, new_event: TacticalEvent):
        print(f"Evento actualizado: {old_event.event_name} -> {new_event.event_name}")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = DemoApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()