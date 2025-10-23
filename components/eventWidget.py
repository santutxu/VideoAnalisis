"""
Panel lateral para gestión de eventos tácticos
"""
from core.event_manager import EventManager
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout,
    QTreeWidget, QTreeWidgetItem, QComboBox, QLineEdit,
    QLabel, QGroupBox, QCheckBox, QSpinBox, QTextEdit,
    QHeaderView, QMenu, QAction, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QBrush

class EventWidget(QWidget):
    """
    Panel para visualizar y gestionar eventos tácticos.
    """
    
    event_selected = pyqtSignal(dict)  # Evento seleccionado
    event_added = pyqtSignal(dict)     # Nuevo evento añadido
    event_deleted = pyqtSignal(str)    # ID del evento eliminado
    
    def __init__(self):
        super().__init__()
        
        self.event_manager = EventManager()
        self.current_timestamp = 0
        
        self._setup_ui()
        
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
        
    def add_event(self, event, loaded=False):
        """Añade un nuevo evento."""
        print(event)
        event_data = {}
        evento = None
        if loaded:
            event_data = {
                'timestamp': event['timestamp'],
                'event_name': event['event_name'],
                'event_type': event['event_type'],
                'match_minute': event['match_minute'],
                'event_duration': event['event_duration']
            }
            evento = {
                'event_start': event['match_minute'],
                'event_end': event['timestamp'],
                'event_name':  event['event_name'],
                'event_type': event['event_type'],
                'event_duration': event['event_duration']
            }
        else:
            event_data = {
                'timestamp': event['event_end'],
                'event_name': event['event_name'],
                'event_type': event['event_type'],
                'match_minute': event['event_start'],
                'event_duration': event['event_duration']
            }
            evento = event

        # Añadir al event manager
        event = self.event_manager.add_event(**event_data)
        
        # Añadir a la lista visual
        self.add_event_to_tree(evento)
        
        # Emitir señal
        self.event_added.emit(evento)
        
        # Limpiar formulario
        #self.notes_text.clear()
        
        # Actualizar estadísticas
        self.update_stats()
        
    def add_event_to_tree(self, event):
        """Añade un evento al árbol visual."""
        item = QTreeWidgetItem()
        
        starttime = self.format_time(event['event_start'])
        endtime = self.format_time(event['event_end'])
        item.setText(0, starttime)
        item.setText(1, endtime)
        evento_all = self.event_manager.get_event_def(event['event_name'])
        # Tipo con icono
        event_icons = {
            'pass': '⚽', 'shot': '🥅', 'loss': '❌',
            'recovery': '✅', 'foul': '🟨', 'corner': '⛳',
            'offside': '🚩', 'substitution': '🔄'
        }
        #icon = event_icons.get(event.event_type, '📌')
        icon = evento_all['icon']
        categoria = evento_all['categoria']
        # Jugador
        item.setText(2, f"{icon} {event['event_name'].capitalize()}")
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
            self.event_selected.emit(event)
            
        
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
        return [event.to_dict() for event in self.event_manager.get_events()]
    
    def delete_event(self,item):
        event = item.data(0, Qt.UserRole)
        if event:
            self.event_manager.delete_event_from_list(event)
            print(event)
        
        
        
        