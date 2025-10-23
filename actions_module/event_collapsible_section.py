"""
Panel lateral para gestión de eventos tácticos
"""
from core.event_manager import EventManager
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .event_buton import EventButton
class CollapsibleSection(QWidget):
    """Sección colapsable para agrupar eventos por tipo"""
    
    def __init__(self, title: str, color: str = "#3498db", parent=None):
        super().__init__(parent)
        self.title = title
        self.color = color
        self.is_expanded = True
        self.buttons = []
        self.init_ui()
        
    def init_ui(self):
        """Inicializar la interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header de la sección
        self.header = QWidget()
        self.header.setFixedHeight(35)
        self.header.setCursor(Qt.PointingHandCursor)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Icono de expandir/colapsar
        self.arrow_label = QLabel()
        self.update_arrow()
        header_layout.addWidget(self.arrow_label)
        
        # Título de la sección
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: white;
        """)
        header_layout.addWidget(self.title_label)
        
        # Contador de eventos
        self.count_label = QLabel("0")
        self.count_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.count_label)
        
        header_layout.addStretch()
        
        # Estilo del header
        self.header.setStyleSheet(f"""
            QWidget {{
                background-color: {self.color};
                border-radius: 5px;
            }}
        """)
        
        layout.addWidget(self.header)
        
        # Contenedor de botones
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(5)
        
        # Frame para el contenido con borde
        self.content_frame = QFrame()
        self.content_frame.setFrameStyle(QFrame.Box)
        self.content_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f8f9fa;
                margin-top: 0px;
            }
        """)
        
        frame_layout = QVBoxLayout(self.content_frame)
        frame_layout.setContentsMargins(5, 5, 5, 5)
        frame_layout.addWidget(self.content_widget)
        
        layout.addWidget(self.content_frame)
        
        # Conectar evento de click en el header
        self.header.mousePressEvent = self.toggle_section
        
    def toggle_section(self, event):
        """Expandir o colapsar la sección"""
        if event.button() == Qt.LeftButton:
            self.is_expanded = not self.is_expanded
            self.content_frame.setVisible(self.is_expanded)
            self.update_arrow()
            
            # Animación suave
            if self.is_expanded:
                self.animate_expand()
            else:
                self.animate_collapse()
                
    def animate_expand(self):
        """Animación de expansión"""
        self.animation = QPropertyAnimation(self.content_frame, b"maximumHeight")
        self.animation.setDuration(200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(self.content_frame.sizeHint().height())
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()
        
    def animate_collapse(self):
        """Animación de colapso"""
        self.animation = QPropertyAnimation(self.content_frame, b"maximumHeight")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.content_frame.height())
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()
        
    def update_arrow(self):
        """Actualizar el icono de flecha"""
        arrow = "▼" if self.is_expanded else "▶"
        self.arrow_label.setText(arrow)
        self.arrow_label.setStyleSheet("color: white; font-size: 12px;")
        
    def add_button(self, button: EventButton):
        """Agregar un botón a la sección"""
        self.buttons.append(button)
        self.content_layout.addWidget(button)
        self.update_count()
        
    def clear_buttons(self):
        """Limpiar todos los botones"""
        for button in self.buttons:
            self.content_layout.removeWidget(button)
            button.deleteLater()
        self.buttons.clear()
        self.update_count()
        
    def update_count(self):
        """Actualizar el contador de eventos"""
        count = len(self.buttons)
        self.count_label.setText(str(count))
        self.count_label.setVisible(count > 0)
        
    def set_expanded(self, expanded: bool):
        """Establecer estado de expansión"""
        self.is_expanded = expanded
        self.content_frame.setVisible(expanded)
        self.update_arrow()