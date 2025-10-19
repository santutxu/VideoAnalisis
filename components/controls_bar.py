"""
Barra de controles de reproducción
"""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSlider, 
    QLabel, QComboBox, QStyle
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

class ControlsBar(QWidget):
    """
    Barra de controles para la reproducción del video.
    """
    
    # Señales
    play_pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    backward_clicked = pyqtSignal()
    forward_clicked = pyqtSignal()
    speed_changed = pyqtSignal(float)
    volume_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        
        self.is_playing = False
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz de controles."""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Botón retroceder
        self.backward_btn = QPushButton()
        self.backward_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.backward_btn.clicked.connect(self.backward_clicked.emit)
        self.backward_btn.setToolTip("Retroceder 10s")
        layout.addWidget(self.backward_btn)
        
        # Botón play/pause
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_pause_btn.clicked.connect(self._on_play_pause)
        self.play_pause_btn.setToolTip("Reproducir/Pausar (Espacio)")
        layout.addWidget(self.play_pause_btn)
        
        # Botón stop
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        self.stop_btn.setToolTip("Detener")
        layout.addWidget(self.stop_btn)
        
        # Botón adelantar
        self.forward_btn = QPushButton()
        self.forward_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.forward_btn.clicked.connect(self.forward_clicked.emit)
        self.forward_btn.setToolTip("Adelantar 10s")
        layout.addWidget(self.forward_btn)
        
        # Separador
        layout.addSpacing(20)
        
        # Control de velocidad
        layout.addWidget(QLabel("Velocidad:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "0.75x", "1x", "1.25x", "1.5x", "2x"])
        self.speed_combo.setCurrentText("1x")
        self.speed_combo.currentTextChanged.connect(self._on_speed_changed)
        self.speed_combo.setToolTip("Velocidad de reproducción")
        layout.addWidget(self.speed_combo)
        
        # Espaciador
        layout.addStretch()
        
        # Control de volumen
        layout.addWidget(QLabel("🔊"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        self.volume_slider.setToolTip("Volumen")
        layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("70%")
        self.volume_label.setMinimumWidth(35)
        layout.addWidget(self.volume_label)
        
        self.volume_label = QLabel("70%")
        self.volume_label.setMinimumWidth(35)
        layout.addWidget(self.volume_label)
        
        # Conectar señal de volumen para actualizar label
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"{v}%")
        )
        
        self.setLayout(layout)
        
    def _on_play_pause(self):
        """Maneja el click en play/pause."""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_pause_btn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)
            )
        else:
            self.play_pause_btn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay)
            )
            
        self.play_pause_clicked.emit()
        
    def _on_speed_changed(self, speed_text):
        """Maneja el cambio de velocidad."""
        speed = float(speed_text.replace('x', ''))
        self.speed_changed.emit(speed)
        
    def set_playing(self, playing: bool):
        """Establece el estado de reproducción."""
        self.is_playing = playing
        
        if self.is_playing:
            self.play_pause_btn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)
            )
        else:
            self.play_pause_btn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay)
            )