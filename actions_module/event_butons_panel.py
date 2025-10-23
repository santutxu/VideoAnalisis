
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .event_buton import EventDefinition, EventButton
from .event_collapsible_section import CollapsibleSection

class EventButtonPanel(QWidget):
    """Panel principal de botones de eventos organizados por tipo"""
    
    event_clicked = pyqtSignal(object)  # EventDefinition
    event_right_clicked = pyqtSignal(object)  # EventDefinition
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.events: List[EventDefinition] = []
        self.sections: Dict[str, CollapsibleSection] = {}
        self.selected_event: Optional[EventDefinition] = None
        self.selected_button: Optional[EventButton] = None
        self.init_ui()
        
    def init_ui(self):
        """Inicializar la interfaz"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header del panel
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            background-color: #2c3e50;
            border-radius: 8px;
            padding: 10px;
        """)
        header_layout = QVBoxLayout(header_widget)
        
        # Título
        title_layout = QHBoxLayout()
        
        self.title_label = QLabel("🎯 Panel de Eventos")
        self.title_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
        """)
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Botón de refrescar
        btn_refresh = QPushButton("🔄 Refrescar")
        btn_refresh.setStyleSheet("""
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
        """)
        btn_refresh.clicked.connect(self.refresh)
        title_layout.addWidget(btn_refresh)
        
        header_layout.addLayout(title_layout)
        
        # Barra de búsqueda
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar eventos...")
        self.search_input.textChanged.connect(self.filter_events)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        search_layout.addWidget(self.search_input)
        
        # Filtro de visualización
        self.view_combo = QComboBox()
        self.view_combo.addItems(["Vista Completa", "Vista Compacta", "Solo Iconos"])
        self.view_combo.currentTextChanged.connect(self.change_view_mode)
        self.view_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px;
                min-width: 120px;
            }
        """)
        search_layout.addWidget(self.view_combo)
        
        header_layout.addLayout(search_layout)
        
        main_layout.addWidget(header_widget)
        
        # Toolbar de acciones
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Área de scroll para las secciones
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ecf0f1;
                border-radius: 8px;
            }
        """)
        
        # Widget contenedor para las secciones
        self.sections_container = QWidget()
        self.sections_layout = QVBoxLayout(self.sections_container)
        self.sections_layout.setSpacing(10)
        self.sections_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll_area.setWidget(self.sections_container)
        main_layout.addWidget(scroll_area)
        
        # Panel de información del evento seleccionado
        self.info_panel = self.create_info_panel()
        main_layout.addWidget(self.info_panel)
        
    def create_toolbar(self):
        """Crear barra de herramientas"""
        toolbar = QWidget()
        toolbar.setStyleSheet("""
            background-color: #34495e;
            border-radius: 5px;
            padding: 5px;
        """)
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Botones de control de secciones
        btn_expand_all = QPushButton("⬇ Expandir Todo")
        btn_expand_all.clicked.connect(self.expand_all_sections)
        btn_expand_all.setStyleSheet(self.get_toolbar_button_style())
        layout.addWidget(btn_expand_all)
        
        btn_collapse_all = QPushButton("⬆ Colapsar Todo")
        btn_collapse_all.clicked.connect(self.collapse_all_sections)
        btn_collapse_all.setStyleSheet(self.get_toolbar_button_style())
        layout.addWidget(btn_collapse_all)
        
        layout.addStretch()
        
        # Estadísticas
        self.stats_label = QLabel("Total: 0 eventos")
        self.stats_label.setStyleSheet("color: white; font-size: 12px;")
        layout.addWidget(self.stats_label)
        
        return toolbar
        
    def create_info_panel(self):
        """Crear panel de información"""
        panel = QGroupBox("ℹ️ Información del Evento")
        panel.setMaximumHeight(120)
        panel.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QHBoxLayout(panel)
        
        # Información del evento seleccionado
        self.info_text = QLabel("Selecciona un evento para ver su información")
        self.info_text.setStyleSheet("""
            color: #7f8c8d;
            font-size: 12px;
            font-weight: normal;
            padding: 10px;
        """)
        self.info_text.setWordWrap(True)
        layout.addWidget(self.info_text)
        
        # Preview del color
        self.color_preview = QWidget()
        self.color_preview.setFixedSize(60, 60)
        self.color_preview.setStyleSheet("""
            background-color: #ecf0f1;
            border-radius: 8px;
            border: 2px solid #bdc3c7;
        """)
        layout.addWidget(self.color_preview)
        
        return panel
        
    def get_toolbar_button_style(self):
        """Obtener estilo para botones de toolbar"""
        return """
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #1a252f;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1a252f;
                border: 1px solid #3498db;
            }
        """
        
    def load_events(self, events: List[EventDefinition]):
        """Cargar eventos y organizarlos por tipo"""
        self.events = events
        self.refresh()
        
    def refresh(self):
        """Refrescar el panel con los eventos actuales"""
        # Limpiar secciones existentes
        for section in self.sections.values():
            section.clear_buttons()
            self.sections_layout.removeWidget(section)
            section.deleteLater()
        self.sections.clear()
        
        # Agrupar eventos por tipo
        events_by_type = {}
        for event in self.events:
            if not event.enabled:
                continue
                
            if event.type not in events_by_type:
                events_by_type[event.type] = []
            events_by_type[event.type].append(event)
            
        # Crear secciones para cada tipo
        type_colors = {
            "Ataque": "#e74c3c",
            "Defensa": "#3498db",
            "Transición": "#f39c12",
            "General": "#95a5a6",
            "Técnico": "#9b59b6",
            "Táctico": "#27ae60",
            "Pausa": "#34495e"
        }
        
        for event_type, type_events in sorted(events_by_type.items()):
            # Obtener color para el tipo
            section_color = type_colors.get(event_type, "#7f8c8d")
            
            # Crear sección
            section = CollapsibleSection(event_type, section_color)
            
            # Agregar botones a la sección
            for event in type_events:
                button = EventButton(event)
                button.clicked.connect(lambda checked, e=event: self.on_event_clicked(e))
                button.right_clicked.connect(self.on_event_right_clicked)
                section.add_button(button)
                
            self.sections[event_type] = section
            self.sections_layout.addWidget(section)
            
        # Agregar espaciador al final
        self.sections_layout.addStretch()
        
        # Actualizar estadísticas
        total_events = sum(len(events) for events in events_by_type.values())
        self.stats_label.setText(f"Total: {total_events} eventos en {len(events_by_type)} categorías")
        
    def on_event_clicked(self, event: EventDefinition):
        """Manejar click en un evento"""
        self.selected_event = event
        
        # Actualizar selección visual
        for section in self.sections.values():
            for button in section.buttons:
                button.set_selected(button.event.id == event.id)
                if button.event.id == event.id:
                    self.selected_button = button
                    
        # Actualizar panel de información
        self.update_info_panel(event)
        
        # Emitir señal
        self.event_clicked.emit(event)
        
    def on_event_right_clicked(self, event: EventDefinition):
        """Manejar click derecho en un evento"""
        # Crear menú contextual
        menu = QMenu(self)
        
        # Información del evento
        info_action = QAction(f"📌 {event.name}", menu)
        info_action.setEnabled(False)
        menu.addAction(info_action)
        
        menu.addSeparator()
        
        # Acciones
        edit_action = QAction("✏️ Editar evento", menu)
        edit_action.triggered.connect(lambda: self.edit_event(event))
        menu.addAction(edit_action)
        
        duplicate_action = QAction("📋 Duplicar", menu)
        duplicate_action.triggered.connect(lambda: self.duplicate_event(event))
        menu.addAction(duplicate_action)
        
        menu.addSeparator()
        
        disable_action = QAction("❌ Deshabilitar", menu)
        disable_action.triggered.connect(lambda: self.disable_event(event))
        menu.addAction(disable_action)
        
        # Mostrar menú
        menu.exec_(QCursor.pos())
        
        # Emitir señal
        self.event_right_clicked.emit(event)
        
    def update_info_panel(self, event: EventDefinition):
        """Actualizar panel de información con el evento seleccionado"""
        info_html = f"""
        <b style='color: #2c3e50; font-size: 14px;'>{event.icon} {event.name}</b><br>
        <span style='color: #7f8c8d;'>Tipo: {event.type}</span><br>
        """
        
        if event.description:
            info_html += f"<span style='color: #95a5a6;'>{event.description}</span><br>"
            
        if event.shortcut:
            info_html += f"<span style='color: #3498db;'>Atajo: {event.shortcut}</span><br>"
            
        if event.tags:
            info_html += f"<span style='color: #9b59b6;'>Tags: {', '.join(event.tags)}</span>"
            
        self.info_text.setText(info_html)
        
        # Actualizar preview de color
        self.color_preview.setStyleSheet(f"""
            background-color: {event.color};
            border-radius: 8px;
            border: 2px solid {event.color};
        """)
        
    def filter_events(self, search_text: str):
        """Filtrar eventos según texto de búsqueda"""
        search_lower = search_text.lower()
        
        for section in self.sections.values():
            visible_count = 0
            
            for button in section.buttons:
                # Buscar en nombre, descripción y tags
                event = button.event
                match = (search_lower in event.name.lower() or
                        search_lower in event.description.lower() or
                        any(search_lower in tag.lower() for tag in event.tags))
                
                button.setVisible(match)
                if match:
                    visible_count += 1
                    
            # Ocultar sección si no hay botones visibles
            section.setVisible(visible_count > 0)
            
    def change_view_mode(self, mode: str):
        """Cambiar modo de visualización"""
        if mode == "Vista Compacta":
            for section in self.sections.values():
                for button in section.buttons:
                    button.setMinimumHeight(30)
                    button.setStyleSheet(button.styleSheet().replace("padding: 8px 12px", "padding: 4px 8px"))
                    
        elif mode == "Solo Iconos":
            for section in self.sections.values():
                for button in section.buttons:
                    button.setText(button.event.icon)
                    button.setMinimumHeight(40)
                    button.setMaximumWidth(50)
                    
        else:  # Vista Completa
            for section in self.sections.values():
                for button in section.buttons:
                    button.setText(f"{button.event.icon} {button.event.name}")
                    button.setMinimumHeight(40)
                    button.setMaximumWidth(16777215)  # Reset max width
                    
    def expand_all_sections(self):
        """Expandir todas las secciones"""
        for section in self.sections.values():
            section.set_expanded(True)
            
    def collapse_all_sections(self):
        """Colapsar todas las secciones"""
        for section in self.sections.values():
            section.set_expanded(False)
            
    def select_event_by_id(self, event_id: str):
        """Seleccionar un evento por su ID"""
        for event in self.events:
            if event.id == event_id:
                self.on_event_clicked(event)
                break
                
    def add_event(self, event: EventDefinition):
        """Agregar un nuevo evento"""
        self.events.append(event)
        self.refresh()
        
    def remove_event(self, event_id: str):
        """Eliminar un evento"""
        self.events = [e for e in self.events if e.id != event_id]
        self.refresh()
        
    def update_event(self, event_id: str, updated_event: EventDefinition):
        """Actualizar un evento existente"""
        for i, event in enumerate(self.events):
            if event.id == event_id:
                self.events[i] = updated_event
                self.refresh()
                break
                
    def edit_event(self, event: EventDefinition):
        """Editar un evento (placeholder para diálogo de edición)"""
        print(f"Editando evento: {event.name}")
        
    def duplicate_event(self, event: EventDefinition):
        """Duplicar un evento"""
        import uuid
        new_event = EventDefinition(
            id=str(uuid.uuid4()),
            name=f"{event.name} (copia)",
            type=event.type,
            color=event.color,
            icon=event.icon,
            shortcut="",
            description=event.description,
            enabled=event.enabled,
            tags=event.tags.copy() if event.tags else []
        )
        self.add_event(new_event)
        
    def disable_event(self, event: EventDefinition):
        """Deshabilitar un evento"""
        event.enabled = False
        self.refresh()
        
    def get_selected_event(self) -> Optional[EventDefinition]:
        """Obtener el evento actualmente seleccionado"""
        return self.selected_event
        
    def clear_selection(self):
        """Limpiar la selección actual"""
        self.selected_event = None
        self.selected_button = None
        
        for section in self.sections.values():
            for button in section.buttons:
                button.set_selected(False)
                
        self.info_text.setText("Selecciona un evento para ver su información")
        self.color_preview.setStyleSheet("""
            background-color: #ecf0f1;
            border-radius: 8px;
            border: 2px solid #bdc3c7;
        """)