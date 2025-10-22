from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .timeline_playhead_handle import PlayheadHandle


class PlayheadLine(QGraphicsLineItem):
    """Línea indicadora de posición actual de reproducción"""
    # Señales
    position_changed = pyqtSignal(float) # Posición en píxeles
    time_changed = pyqtSignal(float) # Tiempo en segundos
    
    def __init__(self, height):
        super().__init__(0, 0, 0, height)
        
        pixels_per_second=10
        self.height = height
        self.pixels_per_second = pixels_per_second
        self.current_position = 0
        self.timeline_width = 0
        self.setPen(QPen(Qt.red, 2))
        self.setZValue(100)
        # Crear el círculo controlador
        self.handle = PlayheadHandle(radius=12)
        self.handle.setParentItem(self)
        self.handle.setPos(0, -2) # Posicionarlo arriba de la línea
        
        # Conectar señales del handle