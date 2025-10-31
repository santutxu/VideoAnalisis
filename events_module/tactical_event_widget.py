from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QLabel, QGroupBox, QHeaderView, QMenu, QAction, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush

from .tactical_event import TacticalEvent
from .tactical_event_edit_dialog import TacticalEventEditDialog
import json

from .tactical_event_manager import TacticalEventManager

class TacticalEventWidget(QWidget):
    """
    Panel para visualizar y gestionar eventos tácticos.
    """

    event_selected = pyqtSignal(dict)  # Evento seleccionado
    event_added = pyqtSignal(dict)     # Nuevo evento añadido
    event_deleted = pyqtSignal(str)    # ID del evento eliminado
    
    def __init__(self):
        super().__init__()
        
        self.event_manager = TacticalEventManager()
        self.current_timestamp = 0
        self.load_event_types()
        self._setup_ui()
        
        #self.event_manager.on_event_removed = self.on_event_removed
      
      
    def load_event_types(self):  
        with open('resources/event_types.json', 'r') as file:
            eventes = json.load(file)
            self.EVENT_TYPES = eventes['events']
            
    def _setup_ui(self):
        """Configura la interfaz del panel."""
        self.setMinimumWidth(500)
        layout = QVBoxLayout()
        """
        """
        # Lista de eventos
        events_group = QGroupBox("Eventos Registrados")
        events_layout = QVBoxLayout()
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos", "Defensa", "Ataque", "transicion",])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)
        
        #self.search_line = QLineEdit()
        #self.search_line.setPlaceholderText("🔍 Buscar...")
        #self.search_line.textChanged.connect(self.search_events)
        #filter_layout.addWidget(self.search_line)
        
        events_layout.addLayout(filter_layout)
        
        # Árbol de eventos
        self.events_tree = QTreeWidget()
        self.events_tree.setHeaderLabels(["Incio", "Fin", "Evento","Categoria"])
        self.events_tree.setAlternatingRowColors(True)
        self.events_tree.setSortingEnabled(True)
        
        # Ajustar columnas
        header = self.events_tree.header()
        #header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        #header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        #header.setSectionResizeMode(2, QHeaderView.Interactive)
        #header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        #header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setMinimumWidth(400)
        # Menú contextual
        self.events_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.events_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # Doble click para saltar al evento
        self.events_tree.itemDoubleClicked.connect(self.jump_to_event)
        #self.events_tree.itemClicked.connect(self.select_event)
        events_layout.addWidget(self.events_tree)
        
        # Estadísticas rápidas
        self.stats_label = QLabel("Total: 0 eventos")
        events_layout.addWidget(self.stats_label)
        
        events_group.setLayout(events_layout)
        layout.addWidget(events_group)
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("📊 Exportar")
        action_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("🗑️ Limpiar Todo")
        self.clear_btn.clicked.connect(self.clear_all_events)
        action_layout.addWidget(self.clear_btn)
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
        
    def add_event(self, event: TacticalEvent, loaded=False):
        """Añade un nuevo evento."""
        print(event)
        event_data = {}
        evento = None
 
            
        evento = event

        # Añadir al event manager
        event = self.event_manager.add_event(event)
        
        # Añadir a la lista visual
        self.add_event_to_tree(evento)
        
        # Emitir señal
        self.event_added.emit(evento.to_dict())
        
        # Limpiar formulario
        #self.notes_text.clear()
        
        # Actualizar estadísticas
        self.update_stats()
        
    def add_event_to_tree(self, event: TacticalEvent):
        """Añade un evento al árbol visual."""
        item = QTreeWidgetItem()
        event_name = event.event_name
        starttime = self.format_time3(event.event_start)
        endtime = self.format_time3(event.event_end)
        item.setText(0, starttime)
        item.setText(1, endtime)
        evento_all = self.get_event_def(event_name)
        # Tipo con icono
        event_icons = {
            'pass': '⚽', 'shot': '🥅', 'loss': '❌',
            'recovery': '✅', 'foul': '🟨', 'corner': '⛳',
            'offside': '🚩', 'substitution': '🔄'
        }
        #icon = event_icons.get(event.event_type, '📌')
        #icon = evento_all['icon']
        categoria = event.event_type#evento_all['categoria']
        # Jugador
        item.setText(2, f"{event.event_name.capitalize()}")
        # Jugador
        item.setText(3, categoria)
        
        # Notas
        #item.setText(3, event.notes)
        
        # Guardar referencia al evento
        item.setData(0, Qt.UserRole, event)
        
       
        color1 = evento_all['color']
        color = QColor(color1)
        color2 = QColor(0,0,0)
        #item.setBackground(0, QBrush(color))
        item.setForeground(0, QBrush(color))
        #item.setBackground(1, QBrush(color))
        item.setForeground(1, QBrush(color))
        #item.setBackground(2, QBrush(color))
        item.setForeground(2, QBrush(color))
        item.setForeground(3, QBrush(color))
        item.setTextAlignment(0,0)
        ''' '''
        
        self.events_tree.addTopLevelItem(item)
        
    def refresh_events(self):
        """Actualiza la lista de eventos."""
        self.events_tree.clear()
        
        for event in self.event_manager.events:
            self.add_event_to_tree(event)
            
        self.update_stats()
        
    def jump_to_event(self, item):
        """Salta a la posición del evento seleccionado."""
        event = item.data(0, Qt.UserRole)
        if event:
            self.event_selected.emit(event.to_dict())
            
        
    def apply_filter(self, filter_text):
        """Aplica filtro a la lista de eventos."""
        # Implementar filtrado
        pass
        
    def search_events(self, search_text):
        """Busca eventos por texto."""
        # Implementar búsqueda
        pass
        
    def clear_all_events(self):
        """Elimina todos los eventos."""
        reply = QMessageBox.question(
            self, "Confirmar",
            "¿Eliminar TODOS los eventos? Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.event_manager.events.clear()
            self.events_tree.clear()
            self.update_stats()     
    def update_stats(self):
        """Actualiza las estadísticas mostradas."""
        total = len(self.event_manager.events)
        
        # Contar por tipo
        #stats = self.event_manager.get_zone_stats()
        
        self.stats_label.setText(f"Total: {total} eventos")
        
    def format_time(self, seconds):
        """Formatea segundos a MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    def format_time2(self,milliseconds):
        """Formatear tiempo de milisegundos a MM:SS"""
        seconds = milliseconds / 1000
        minutes = int(seconds // 60)
        hours = int(minutes // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    def format_time3(self,seconds):
        """Formatear tiempo de milisegundos a MM:SS"""
        #seconds = milliseconds / 1000
        minutes = int(seconds // 60)
        hours = int(minutes // 60)
        if minutes >= 60:
            minutes = minutes % 60
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
    def set_current_timestamp(self, timestamp):
        """Actualiza el timestamp actual para nuevos eventos."""
        self.current_timestamp = timestamp
        
    def show_context_menu(self, position):
        """Muestra menú contextual para eventos."""
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
        
    def add_event_of_type(self, event_type):
        print(f"Evento seleccionado: {event_type}")
        
    def get_all_events(self):
        """Devuelve todos los eventos como lista de diccionarios."""
        return [event.to_dict() for event in self.event_manager.events]
    
    def delete_event(self,item):
        event = item.data(0, Qt.UserRole)
        if event:
            reply = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Eliminar '{event.event_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.event_manager.remove_event(event)
                self.refresh_events()
            
            
    def edit_event(self,item):
        evento = item.data(0, Qt.UserRole)
        event = TacticalEvent(
            event_name=evento.event_name,
            event_type=evento.event_type,
            event_start=evento.event_start,
            event_end=evento.event_end,
            event_duration=evento.event_duration,
            #match_minute=evento.match_minute,
            #tags=evento.tags,
            #coordinates=evento.coordinates
        )
        event.id = evento.id
        """Edición rápida de un evento desde la tabla."""
        dialog = TacticalEventEditDialog(event, self)
        if dialog.exec_():
            updated_event = dialog.get_updated_event()
            self.event_manager.replace_event(event.id, updated_event)
            self.refresh_events()
    
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
            self.event_manager.remove_event(event)
            #self.refresh_table()
        
     
    def on_event_removed(self, event: TacticalEvent):
        """Callback cuando se elimina un evento."""
        self.event_deleted.emit(event)   
        
    def get_event_def(self, event_type):
        """Obtiene un evento por su tipo."""
        for event in self.EVENT_TYPES:
            if event['id'] == event_type:
                #evv = self.EVENT_TYPES[event]
                #print(evv)
                return event
        return None
