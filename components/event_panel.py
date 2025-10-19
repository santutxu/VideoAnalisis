"""
Panel lateral para gestión de eventos tácticos
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTreeWidget, QTreeWidgetItem, QComboBox, QLineEdit,
    QLabel, QGroupBox, QCheckBox, QSpinBox, QTextEdit,
    QHeaderView, QMenu, QAction, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QBrush

class EventPanel(QWidget):
    """
    Panel para visualizar y gestionar eventos tácticos.
    """
    
    event_selected = pyqtSignal(dict)  # Evento seleccionado
    event_added = pyqtSignal(dict)     # Nuevo evento añadido
    event_deleted = pyqtSignal(str)    # ID del evento eliminado
    
    def __init__(self, event_manager):
        super().__init__()
        
        self.event_manager = event_manager
        self.current_timestamp = 0
        
        self._setup_ui()
        self._load_event_templates()
        
    def _setup_ui(self):
        """Configura la interfaz del panel."""
        layout = QVBoxLayout()
        
        # Sección de añadir evento
        add_group = QGroupBox("Añadir Eventos")
        add_layout = QVBoxLayout()
        
       
        #self.add_event_btn  = QAction("➕ Añadir Evento", self   )
        self.add_event_btn = QPushButton("➕ Añadir Evento")
        self.add_event_btn.clicked.connect(self.add_event)
        add_layout.addWidget(self.add_event_btn)
        
       
        # Selector de tipo de evento
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Tipo:"))
        
        self.event_type_combo = QComboBox()
        self.event_type_combo.addItems([
            'Pase', 'Tiro', 'Pérdida', 'Recuperación',
            'Falta', 'Córner', 'Fuera de juego', 'Cambio'
        ])
        type_layout.addWidget(self.event_type_combo)
        add_layout.addLayout(type_layout)
        
        # Selector de jugador
        player_layout = QHBoxLayout()
        player_layout.addWidget(QLabel("Jugador:"))
        
        self.player_combo = QComboBox()
        self.player_combo.setEditable(True)
        self.player_combo.addItem("Sin jugador")
        player_layout.addWidget(self.player_combo)
        
        # Botón para añadir jugador
        self.add_player_btn = QPushButton("+")
        self.add_player_btn.setMaximumWidth(30)
        #self.add_player_btn.clicked.connect(self.add_player)
        player_layout.addWidget(self.add_player_btn)
        
        add_layout.addLayout(player_layout)
        """
        # Equipo
        team_layout = QHBoxLayout()
        team_layout.addWidget(QLabel("Equipo:"))
        
        self.team_combo = QComboBox()
        self.team_combo.setEditable(True)
        self.team_combo.addItems(["Local", "Visitante"])
        team_layout.addWidget(self.team_combo)
        
        add_layout.addLayout(team_layout)
        
        # Minuto del partido
        minute_layout = QHBoxLayout()
        minute_layout.addWidget(QLabel("Minuto:"))
        
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 120)
        minute_layout.addWidget(self.minute_spin)
        
        add_layout.addLayout(minute_layout)
        
        # Notas
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(60)
        self.notes_text.setPlaceholderText("Notas adicionales...")
        add_layout.addWidget(self.notes_text)
        
        # Botón de añadir
        self.add_event_btn = QPushButton("➕ Añadir Evento")
        self.add_event_btn.clicked.connect(self.add_event)
        add_layout.addWidget(self.add_event_btn)
        """
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
        
        # Lista de eventos
        events_group = QGroupBox("Eventos Registrados")
        events_layout = QVBoxLayout()
        
        # Filtros
        filter_layout = QHBoxLayout()
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Todos", "Pases", "Tiros", "Faltas", "Por Jugador"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)
        
        self.search_line = QLineEdit()
        self.search_line.setPlaceholderText("🔍 Buscar...")
        self.search_line.textChanged.connect(self.search_events)
        filter_layout.addWidget(self.search_line)
        
        events_layout.addLayout(filter_layout)
        
        # Árbol de eventos
        self.events_tree = QTreeWidget()
        self.events_tree.setHeaderLabels(["Tiempo", "Tipo", "Duracion"])
        self.events_tree.setAlternatingRowColors(True)
        self.events_tree.setSortingEnabled(True)
        
        # Ajustar columnas
        header = self.events_tree.header()
        #header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        #header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        #header.setSectionResizeMode(2, QHeaderView.Interactive)
        #header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
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
        
    def _load_event_templates(self):
        """Carga plantillas de eventos predefinidas."""
        # Aquí se pueden cargar plantillas desde archivo
        pass
        

            
    def add_event(self):
        """Añade un nuevo evento."""
        event_data = {
            'timestamp': self.current_timestamp,
            'event_type': self.event_type_combo.currentText().lower(),
            'player_name': self.player_combo.currentText() if self.player_combo.currentIndex() > 0 else None,
            'team': self.team_combo.currentText(),
            'match_minute': self.minute_spin.value(),
            'notes': self.notes_text.toPlainText()
        }
        
        '''
        Eventos
        * DEFENSA:
        -  

        '''
        
        evento = {
            'timestamp': event_data['timestamp'],
            'event_type': "",
            'player_name': event_data['player_name'],
            'team': event_data['team'],
            'match_minute': event_data['match_minute'],
            'notes': event_data['notes']
        }
        
        # Añadir al event manager
        event = self.event_manager.add_event(**event_data)
        
        # Añadir a la lista visual
        self.add_event_to_tree(event)
        
        # Emitir señal
        self.event_added.emit(event_data)
        
        # Limpiar formulario
        self.notes_text.clear()
        
        # Actualizar estadísticas
        self.update_stats()
        
    def add_event_to_tree(self, event):
        """Añade un evento al árbol visual."""
        item = QTreeWidgetItem()
        
        # Tiempo
        time_str = self.format_time(event.timestamp)
        item.setText(0, time_str)
        evento_all = self.event_manager.get_event_def(event.event_type)
        # Tipo con icono
        event_icons = {
            'pass': '⚽', 'shot': '🥅', 'loss': '❌',
            'recovery': '✅', 'foul': '🟨', 'corner': '⛳',
            'offside': '🚩', 'substitution': '🔄'
        }
        #icon = event_icons.get(event.event_type, '📌')
        icon = evento_all['icon']
        item.setText(1, f"{icon} {event.event_type.capitalize()}")
        
        # Jugador
        item.setText(2, evento_all['time'])
        
        # Notas
        #item.setText(3, event.notes)
        
        # Guardar referencia al evento
        item.setData(0, Qt.UserRole, event)
        
        # Color según tipo
        colors = {
            'pass': QColor(76, 175, 80),
            'shot': QColor(255, 87, 34),
            'loss': QColor(244, 67, 54),
            'recovery': QColor(33, 150, 243),
            'foul': QColor(255, 193, 7)
        }
        
        color = colors.get(event.event_type, QColor(158, 158, 158))
        #item.setBackground(1, QBrush(color.lighter(180)))
        color1 = evento_all['color']
        color2 = QColor(color1)
        item.setBackground(1, QBrush(color2))
        
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
        
    def edit_event(self, item):
        """Edita un evento existente."""
        event = item.data(0, Qt.UserRole)
        if event:
            # Aquí se abriría un diálogo de edición
            pass
            
    def delete_event(self, item):
        """Elimina un evento."""
        event = item.data(0, Qt.UserRole)
        if event:
            reply = QMessageBox.question(
                self, "Confirmar", 
                "¿Eliminar este evento?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Eliminar del manager
                self.event_manager.remove_event(event.id)
                
                # Eliminar del árbol
                index = self.events_tree.indexOfTopLevelItem(item)
                self.events_tree.takeTopLevelItem(index)
                
                # Emitir señal
                self.event_deleted.emit(event.id)
                
                # Actualizar estadísticas
                self.update_stats()
                
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