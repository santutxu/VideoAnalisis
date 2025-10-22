from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

       
class PlayheadHandle(QGraphicsEllipseItem):
    """Círculo controlador del playhead en la parte superior"""
    
    # Señales
    position_changed = pyqtSignal(float) # Nueva posición en píxeles
    dragging_started = pyqtSignal()
    dragging_finished = pyqtSignal()
    
    def __init__(self, radius=10, parent=None):
        # Crear círculo centrado
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        
        
        self.radius = radius
        self.is_dragging = False
        self.drag_start_pos = None
        self.timeline_width = 0 # Se establecerá desde el timeline
        
        # Estilo del círculo
        self._setup_appearance()
        
        # Habilitar interacción
        self.setFlag(QGraphicsItem.ItemIsMovable, False) # Movimiento manual controlado
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.OpenHandCursor)
        self.setZValue(101) # Por encima de todo
        
        # Tooltip
        self.setToolTip("Arrastrar para navegar")
        
    def _setup_appearance(self):
        """Configurar la apariencia del círculo"""
        # Gradiente radial para efecto 3D
        gradient = QRadialGradient(0, 0, self.radius)
        gradient.setColorAt(0, QColor(255, 100, 100)) # Centro: rojo claro
        gradient.setColorAt(0.5, QColor(220, 50, 50)) # Medio: rojo
        gradient.setColorAt(1, QColor(180, 30, 30)) # Borde: rojo oscuro
        
        self.normal_gradient = gradient
        
        # Gradiente para hover
        hover_gradient = QRadialGradient(0, 0, self.radius)
        hover_gradient.setColorAt(0, QColor(255, 150, 150))
        hover_gradient.setColorAt(0.5, QColor(255, 80, 80))
        hover_gradient.setColorAt(1, QColor(200, 50, 50))
        
        self.hover_gradient = hover_gradient
        
        # Gradiente para dragging
        drag_gradient = QRadialGradient(0, 0, self.radius)
        drag_gradient.setColorAt(0, QColor(255, 200, 200))
        drag_gradient.setColorAt(0.5, QColor(255, 100, 100))
        drag_gradient.setColorAt(1, QColor(220, 70, 70))
        
        self.drag_gradient = drag_gradient
        
        # Aplicar estilo inicial
        self.setBrush(QBrush(self.normal_gradient))
        self.setPen(QPen(QColor(150, 30, 30), 2))
        
        # Añadir sombra
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.shadow.setOffset(2, 2)
        self.setGraphicsEffect(self.shadow)
        
    def set_timeline_bounds(self, width):
        """Establecer los límites del timeline"""
        self.timeline_width = width
        
    def hoverEnterEvent(self, event):
        """Cuando el mouse entra"""
        if not self.is_dragging:
            self.setBrush(QBrush(self.hover_gradient))
            self.setPen(QPen(QColor(180, 50, 50), 3))
            self.setCursor(Qt.OpenHandCursor)
            self.shadow.setBlurRadius(15)
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """Cuando el mouse sale"""
        if not self.is_dragging:
            self.setBrush(QBrush(self.normal_gradient))
            self.setPen(QPen(QColor(150, 30, 30), 2))
            self.shadow.setBlurRadius(10)
        super().hoverLeaveEvent(event)
        
    def mousePressEvent(self, event):
        """Iniciar arrastre"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_pos = event.scenePos()
            self.setCursor(Qt.ClosedHandCursor)
            self.setBrush(QBrush(self.drag_gradient))
            self.setPen(QPen(QColor(200, 60, 60), 3))
            self.shadow.setBlurRadius(20)
            self.dragging_started.emit()
            event.accept()
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        """Arrastrar el playhead"""
        if self.is_dragging and event.buttons() & Qt.LeftButton:
            # Calcular nueva posición
            new_x = event.scenePos().x()
            
            # Limitar a los bounds del timeline
            new_x = max(0, min(new_x, self.timeline_width))
            
            # Emitir nueva posición
            self.position_changed.emit(new_x)
            
            event.accept()
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        """Terminar arrastre"""
        if self.is_dragging and event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.setCursor(Qt.OpenHandCursor)
            self.setBrush(QBrush(self.hover_gradient))
            self.setPen(QPen(QColor(180, 50, 50), 3))
            self.shadow.setBlurRadius(15)
            self.dragging_finished.emit()
            event.accept()
        else:
            super().mouseReleaseEvent(event)
