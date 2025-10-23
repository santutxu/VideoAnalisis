from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from dataclasses import dataclass, asdict

from typing import List, Dict, Any, Optional

@dataclass
class EventDefinition:
    """Definición de un evento"""
    id: str
    name: str
    type: str
    color: str
    icon: str = "📌"
    shortcut: str = ""
    description: str = ""
    enabled: bool = True
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class EventButton(QPushButton):
    """Botón personalizado para eventos"""
    
    right_clicked = pyqtSignal(object)  # Señal para click derecho
    
    def __init__(self, event: EventDefinition, parent=None):
        super().__init__(parent)
        self.event = event
        self.is_selected = False
        self.setup_button()
        
    def setup_button(self):
        """Configurar el botón"""
        # Texto del botón
        button_text = f"{self.event.icon} {self.event.name}"
        self.setText(button_text)
        
        # Tooltip con información adicional
        tooltip_text = f"<b>{self.event.name}</b>"
        if self.event.description:
            tooltip_text += f"<br>{self.event.description}"
        if self.event.shortcut:
            tooltip_text += f"<br><i>Atajo: {self.event.shortcut}</i>"
        if self.event.tags:
            tooltip_text += f"<br>Tags: {', '.join(self.event.tags)}"
        self.setToolTip(tooltip_text)
        
        # Configurar tamaño
        self.setMinimumHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Cursor
        self.setCursor(Qt.PointingHandCursor)
        
        # Aplicar estilo
        self.update_style()
        
        # Habilitar menú contextual
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def update_style(self):
        """Actualizar el estilo del botón"""
        # Convertir color hex a RGB para manipulación
        color = QColor(self.event.color)
        
        # Calcular colores para diferentes estados
        hover_color = color.lighter(110)
        pressed_color = color.darker(110)
        
        # Determinar si usar texto blanco o negro basado en luminancia
        luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
        text_color = "white" if luminance < 0.5 else "black"
        
        # Estilo para estado seleccionado
        border_style = "3px solid #2c3e50" if self.is_selected else "1px solid rgba(0,0,0,0.2)"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.event.color};
                color: {text_color};
                border: {border_style};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: bold;
                text-align: left;
            }}
            
            QPushButton:hover {{
                background-color: {hover_color.name()};
                border: 2px solid rgba(0,0,0,0.3);
            }}
            
            QPushButton:pressed {{
                background-color: {pressed_color.name()};
                padding: 9px 11px 7px 13px;
            }}
            
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
                border: 1px solid #aaaaaa;
            }}
        """)
        
    def set_selected(self, selected: bool):
        """Establecer estado de selección"""
        self.is_selected = selected
        self.update_style()
        
    def show_context_menu(self, position):
        """Mostrar menú contextual"""
        self.right_clicked.emit(self.event)
        
    def mousePressEvent(self, event):
        """Manejar eventos de mouse"""
        if event.button() == Qt.RightButton:
            self.right_clicked.emit(self.event)
        else:
            super().mousePressEvent(event)
