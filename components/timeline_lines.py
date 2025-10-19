from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

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

class CutLine(QGraphicsLineItem):
    """Línea indicadora para corte de video"""
    
    def __init__(self, height):
        super().__init__(0, 0, 0, height)
        self.setPen(QPen(Qt.yellow, 2, Qt.DashLine))
        self.setZValue(99)
        self.setVisible(False)
        
        
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

class PlayheadLine2(QGraphicsLineItem):
    """Línea indicadora de posición actual con control draggable"""
    
    # Señales
    position_changed = pyqtSignal(float) # Posición en píxeles
    time_changed = pyqtSignal(float) # Tiempo en segundos
    
    def __init__(self, height, pixels_per_second=10):
        super().__init__(0, 0, 0, height)
        
        self.height = height
        self.pixels_per_second = pixels_per_second
        self.current_position = 0
        self.timeline_width = 0
        
        # Estilo de la línea
        self.setPen(QPen(QColor(255, 50, 50), 2))
        self.setZValue(100)
        
        # Crear el círculo controlador
        self.handle = PlayheadHandle(radius=12)
        self.handle.setParentItem(self)
        self.handle.setPos(0, -12) # Posicionarlo arriba de la línea
        
        # Conectar señales del handle
        self.handle.position_changed.connect(self.on_handle_moved)
        self.handle.dragging_started.connect(self.on_dragging_started)
        self.handle.dragging_finished.connect(self.on_dragging_finished)
        
        # Crear etiqueta de tiempo
        self.time_label = QGraphicsTextItem("00:00")
        self.time_label.setParentItem(self)
        self.time_label.setDefaultTextColor(Qt.white)
        self.time_label.setFont(QFont("Arial", 9, QFont.Bold))
        self.time_label.setPos(-20, -30) # Encima del círculo
        self.time_label.setZValue(102)
        
        # Fondo para la etiqueta
        self.label_bg = QGraphicsRectItem(-25, -32, 50, 18)
        self.label_bg.setParentItem(self)
        self.label_bg.setBrush(QBrush(QColor(0, 0, 0, 180)))
        self.label_bg.setPen(QPen(Qt.NoPen))
        self.label_bg.setZValue(101)
        
        # Añadir efecto de resplandor a la línea
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(5)
        self.glow.setColor(QColor(255, 100, 100, 150))
        self.glow.setOffset(0, 0)
        self.setGraphicsEffect(self.glow)
        
    def set_timeline_bounds(self, width):
        """Establecer los límites del timeline"""
        self.timeline_width = width
        self.handle.set_timeline_bounds(width)
        
    def set_pixels_per_second(self, pixels_per_second):
        """Actualizar la escala de tiempo"""
        self.pixels_per_second = pixels_per_second
        self.update_time_label()
        
    def on_handle_moved(self, new_x):
        """Manejar cuando se mueve el handle"""
        # Actualizar posición del playhead
        self.setPos(new_x, 0)
        self.current_position = new_x
        
        # Actualizar etiqueta de tiempo
        self.update_time_label()
        
        # Emitir señales
        self.position_changed.emit(new_x)
        time_seconds = new_x / self.pixels_per_second if self.pixels_per_second > 0 else 0
        self.time_changed.emit(time_seconds)
        
    def on_dragging_started(self):
        """Cuando empieza el arrastre"""
        # Hacer la línea más visible
        self.setPen(QPen(QColor(255, 100, 100), 3))
        self.glow.setBlurRadius(10)
        self.glow.setColor(QColor(255, 150, 150, 200))
        
    def on_dragging_finished(self):
        """Cuando termina el arrastre"""
        # Restaurar estilo normal
        self.setPen(QPen(QColor(255, 50, 50), 2))
        self.glow.setBlurRadius(5)
        self.glow.setColor(QColor(255, 100, 100, 150))
        
    def update_time_label(self):
        """Actualizar la etiqueta de tiempo"""
        time_seconds = self.current_position / self.pixels_per_second if self.pixels_per_second > 0 else 0
        time_str = self.format_time(time_seconds)
        self.time_label.setPlainText(time_str)
        
        # Ajustar posición de la etiqueta para que no se salga del timeline
        label_x = -20
        if self.current_position < 30:
            label_x = 10
        elif self.current_position > self.timeline_width - 30:
            label_x = -50
            
        self.time_label.setPos(label_x, -30)
        self.label_bg.setPos(label_x - 5, -32)
        
    def format_time(self, seconds):
        """Formatear segundos a MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
        
    def set_position(self, x):
        """Establecer la posición programáticamente"""
        # Limitar a los bounds
        x = max(0, min(x, self.timeline_width))
        
        # Actualizar posición
        self.setPos(x, 0)
        self.current_position = x
        
        # Actualizar etiqueta
        self.update_time_label()
        
    def animate_to_position(self, target_x, duration=200):
        """Animar el playhead a una nueva posición"""
        # Crear animación
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPointF(target_x, 0))
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Actualizar durante la animación
        self.animation.valueChanged.connect(lambda: self.update_time_label())
        self.animation.finished.connect(lambda: setattr(self, 'current_position', target_x))
        
        self.animation.start()

class CutLine2(QGraphicsLineItem):
    """Línea indicadora para corte de video"""
    def __init__(self, height):
        super().__init__(0, 0, 0, height)
        self.setPen(QPen(Qt.yellow, 2, Qt.DashLine))
        self.setZValue(99)
        self.setVisible(False)