from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,QDialog,
    QLineEdit,QDoubleSpinBox,QDialogButtonBox,
    QLabel, QGroupBox, QSpinBox
)
from PyQt5.QtCore import Qt
from .tactical_event import TacticalEvent

         
class TacticalEventEditDialog(QDialog):
    """Diálogo para editar un evento táctico."""
    
    def __init__(self, event: TacticalEvent, parent=None):
        super().__init__(parent)
        self.event = event.copy()  # Trabajar con una copia
        self.original_event = event
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"Editar Evento - {self.event.event_name}")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Formulario de edición
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # Campo: Nombre del evento
        #self.name_edit = QLineEdit(self.event.event_name)
        self.name_edit = QLabel()
        self.name_edit.setText(self.event.event_name)
        form_layout.addRow("Nombre del Evento:", self.name_edit)
        
        # Campo: Tipo de evento
        #self.type_combo = QComboBox()
        #self.type_combo.setEditable(True)
        #self.type_combo.addItems(["Ataque", "Defensa", "Transición", "Pausa", "Otro"])
        #self.type_combo.setCurrentText(self.event.event_type)
        self.type_combo = QLabel()
        self.type_combo.setText(self.event.event_type)
        #form_layout.addRow("Nombre del Evento:", self.name_edit)
        form_layout.addRow("Tipo de Evento:", self.type_combo)
        
        # Campo: Tiempo de inicio
        self.start_spin = QDoubleSpinBox()
        self.start_spin.setRange(0, 999999)
        self.start_spin.setDecimals(3)
        self.start_spin.setSuffix(" s")
        self.start_spin.setValue(self.event.event_start)
        form_layout.addRow("Tiempo de Inicio:", self.start_spin)
        
        # Campo: Tiempo de fin
        self.end_spin = QDoubleSpinBox()
        self.end_spin.setRange(0, 999999)
        self.end_spin.setDecimals(3)
        self.end_spin.setSuffix(" s")
        self.end_spin.setValue(self.event.event_end)
        form_layout.addRow("Tiempo de Fin:", self.end_spin)
        
        # Campo: Duración (calculada automáticamente)
        self.duration_label = QLabel()
        self.update_duration()
        form_layout.addRow("Duración:", self.duration_label)
        
        # Campo: Minuto del partido
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 120)
        #self.minute_spin.setValue(self.event.match_minute or 0)
        self.minute_spin.setSpecialValueText("No especificado")
        #form_layout.addRow("Minuto del Partido:", self.minute_spin)
        
        # Campo: Tags
        self.tags_edit = QLineEdit()
        #if self.event.tags:
        #    self.tags_edit.setText(", ".join(self.event.tags))
        self.tags_edit.setPlaceholderText("Separar tags con comas")
        #form_layout.addRow("Tags:", self.tags_edit)
        
        # Campo: Coordenadas
        coords_widget = QWidget()
        coords_layout = QHBoxLayout(coords_widget)
        coords_layout.setContentsMargins(0, 0, 0, 0)
        
        self.coord_x_spin = QDoubleSpinBox()
        self.coord_x_spin.setRange(0, 1)
        self.coord_x_spin.setDecimals(3)
        self.coord_x_spin.setSingleStep(0.01)
        
        self.coord_y_spin = QDoubleSpinBox()
        self.coord_y_spin.setRange(0, 1)
        self.coord_y_spin.setDecimals(3)
        self.coord_y_spin.setSingleStep(0.01)
        '''
        if self.event.coordinates:
            self.coord_x_spin.setValue(self.event.coordinates.get('x', 0))
            self.coord_y_spin.setValue(self.event.coordinates.get('y', 0))
        
        coords_layout.addWidget(QLabel("X:"))
        coords_layout.addWidget(self.coord_x_spin)
        coords_layout.addWidget(QLabel("Y:"))
        coords_layout.addWidget(self.coord_y_spin)
        coords_layout.addStretch()
        '''
        form_layout.addRow("Coordenadas:", coords_widget)
        
        layout.addWidget(form_widget)
        
        # Información adicional (solo lectura)
        info_group = QGroupBox("Información del Sistema")
        info_layout = QFormLayout(info_group)
        
        id_label = QLabel(self.event.id)
        id_label.setStyleSheet("color: #666; font-family: monospace;")
        info_layout.addRow("ID:", id_label)
        
        created_label = QLabel(self.event.created_at)
        created_label.setStyleSheet("color: #666;")
        info_layout.addRow("Creado:", created_label)
        
        layout.addWidget(info_group)
        
        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        # Conectar señales
        self.start_spin.valueChanged.connect(self.update_duration)
        self.end_spin.valueChanged.connect(self.update_duration)
        
    def update_duration(self):
        """Actualiza la etiqueta de duración."""
        duration = self.end_spin.value() - self.start_spin.value()
        self.duration_label.setText(f"{duration:.3f} segundos")
        
    def get_updated_event(self) -> TacticalEvent:
        """Obtiene el evento con los valores actualizados."""
        self.event.event_name = self.name_edit.text()
        self.event.event_type = self.type_combo.text()
        self.event.event_start = self.start_spin.value()
        self.event.event_end = self.end_spin.value()
        self.event.event_duration = str(self.end_spin.value() - self.start_spin.value())
        '''
        # Minuto del partido
        if self.minute_spin.value() > 0:
            self.event.match_minute = self.minute_spin.value()
        else:
            self.event.match_minute = None
        
        # Tags
        tags_text = self.tags_edit.text().strip()
        if tags_text:
            self.event.tags = [tag.strip() for tag in tags_text.split(',')]
        else:
            self.event.tags = []
        
        # Coordenadas
        if self.coord_x_spin.value() > 0 or self.coord_y_spin.value() > 0:
            self.event.coordinates = {
                'x': self.coord_x_spin.value(),
                'y': self.coord_y_spin.value()
            }
        '''
        return self.event
    