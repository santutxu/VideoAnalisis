from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class CutLine(QGraphicsLineItem):
    """Línea indicadora para corte de video"""
    
    def __init__(self, height):
        super().__init__(0, 0, 0, height)
        self.setPen(QPen(Qt.yellow, 2, Qt.DashLine))
        self.setZValue(99)
        self.setVisible(False)
        