from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from utils.time_utils import format_time

class TimelineRuler(QGraphicsItem):
    """Regla del timeline con marcas de tiempo adaptativas al zoom"""
    
    def __init__(self, width, height=40, pixels_per_second=10):
        super().__init__()
        self.width = width
        self.height = height
        self.pixels_per_second = pixels_per_second
        self.update_interval()
        
    def update_interval(self):
        """Actualizar el intervalo de las marcas según el zoom"""
        if self.pixels_per_second >= 20:
            self.major_interval = 5 # Marcas cada 5 segundos
            self.minor_interval = 1 # Marcas menores cada segundo
        elif self.pixels_per_second >= 10:
            self.major_interval = 10 # Marcas cada 10 segundos
            self.minor_interval = 2 # Marcas menores cada 2 segundos
        elif self.pixels_per_second >= 5:
            self.major_interval = 20 # Marcas cada 20 segundos
            self.minor_interval = 5 # Marcas menores cada 5 segundos
        else:
            self.major_interval = 30 # Marcas cada 30 segundos
            self.minor_interval = 10 # Marcas menores cada 10 segundos
            
    def update_zoom(self, new_pixels_per_second):
        """Actualizar cuando cambia el zoom"""
        self.pixels_per_second = new_pixels_per_second
        self.update_interval()
        self.update()
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def paint(self, painter, option, widget):
        """Dibujar la regla con marcas de tiempo"""
        painter.fillRect(0, 0, self.width, self.height, QColor(40, 40, 40))
        
        painter.setPen(QPen(Qt.white, 1))
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        # Dibujar marcas principales
        for second in range(0, int(self.width / self.pixels_per_second) + 1, self.major_interval):
            x = int(second * self.pixels_per_second)
            
            painter.setPen(QPen(Qt.white, 2))
            painter.drawLine(x, self.height - 10, x, self.height)
            
            time_str = format_time(second * 1000)
            painter.drawText(x - 20, 5, 50, 20, Qt.AlignCenter, time_str)
            
            # Marcas secundarias
            if second + self.major_interval <= self.width / self.pixels_per_second:
                painter.setPen(QPen(Qt.gray, 1))
                for sub_second in range(self.minor_interval, self.major_interval, self.minor_interval):
                    sub_x = int((second + sub_second) * self.pixels_per_second)
                    if sub_x < self.width:
                        painter.drawLine(sub_x, self.height - 5, sub_x, self.height)

