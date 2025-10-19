"""
Barra de controles de reproducción
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, 
    QLabel, QComboBox, QStyle
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
class VideoControlBar(QWidget):
    """Barra de control de video profesional con diseño moderno"""
    
    # Señales personalizadas
    playClicked = pyqtSignal()
    pauseClicked = pyqtSignal()
    stopClicked = pyqtSignal()
    previousFrameClicked = pyqtSignal()
    nextFrameClicked = pyqtSignal()
    beginningClicked = pyqtSignal()
    endClicked = pyqtSignal()
    volumeChanged = pyqtSignal(int)
    speedChanged = pyqtSignal(float)
    positionChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_playing = False
        self.total_frames = 0
        self.current_frame = 0
        self.fps = 30
        self.duration = 0
        self.init_ui()
        self.apply_styles()
        self.setDisabled(True)
        
    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(5)
        
        # === BARRA DE PROGRESO ===
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)
        
        # Tiempo actual
        self.current_time_label = QLabel("00:00:00")
        self.current_time_label.setObjectName("timeLabel")
        self.current_time_label.setMinimumWidth(70)
        #progress_layout.addWidget(self.current_time_label)
        
        # Slider de progreso
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setObjectName("progressSlider")
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(100)
        self.progress_slider.sliderPressed.connect(self.on_slider_pressed)
        self.progress_slider.sliderMoved.connect(self.on_slider_moved)
        self.progress_slider.sliderReleased.connect(self.on_slider_released)
        #progress_layout.addWidget(self.progress_slider, 1)
        
        # Tiempo total
        self.total_time_label = QLabel("00:00:00")
        self.total_time_label.setObjectName("timeLabel")
        self.total_time_label.setMinimumWidth(70)
        #progress_layout.addWidget(self.total_time_label)
        
        #main_layout.addLayout(progress_layout)
        
        # === CONTROLES PRINCIPALES ===
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(0)
        
        # Grupo izquierdo - Controles de reproducción
        left_controls = QHBoxLayout()
        left_controls.setSpacing(2)
        
        # Botón ir al inicio
        self.btn_beginning = self.create_control_button("⏮", "Ir al inicio", "controlButton")
        self.btn_beginning.clicked.connect(self.on_beginning_clicked)
        #left_controls.addWidget(self.btn_beginning)
        
        # Botón frame anterior
        self.btn_previous = self.create_control_button("⏪", "Frame anterior", "controlButton")
        self.btn_previous.clicked.connect(self.on_previous_clicked)
        left_controls.addWidget(self.btn_previous)
        
        # Botón Play/Pause (más grande)
        self.btn_play_pause = self.create_control_button("▶", "Reproducir", "playButton")
        self.btn_play_pause.clicked.connect(self.on_play_pause_clicked)
        left_controls.addWidget(self.btn_play_pause)
        
        # Botón Stop
        self.btn_stop = self.create_control_button("⏹", "Detener", "controlButton")
        self.btn_stop.clicked.connect(self.on_stop_clicked)
        left_controls.addWidget(self.btn_stop)
        
        # Botón frame siguiente
        self.btn_next = self.create_control_button("⏩", "Frame siguiente", "controlButton")
        self.btn_next.clicked.connect(self.on_next_clicked)
        left_controls.addWidget(self.btn_next)
        
        # Botón ir al final
        self.btn_end = self.create_control_button("⏭", "Ir al final", "controlButton")
        self.btn_end.clicked.connect(self.on_end_clicked)
        #left_controls.addWidget(self.btn_end)
        
        controls_layout.addLayout(left_controls)
        
        # Espaciador central
        controls_layout.addStretch()
        
        # Grupo central - Información
        center_info = QHBoxLayout()
        center_info.setSpacing(15)
        
        # Frame actual
        frame_widget = QWidget()
        frame_layout = QHBoxLayout(frame_widget)
        frame_layout.setContentsMargins(10, 0, 10, 0)
        frame_layout.setSpacing(5)
        
        frame_icon = QLabel("🎬")
        frame_layout.addWidget(frame_icon)
        
        self.frame_label = QLabel("Frame: 0 / 0")
        self.frame_label.setObjectName("infoLabel")
        frame_layout.addWidget(self.current_time_label)
        #frame_layout.addWidget(self.frame_label)
        
        center_info.addWidget(frame_widget)
        
        # FPS
        fps_widget = QWidget()
        fps_layout = QHBoxLayout(fps_widget)
        fps_layout.setContentsMargins(10, 0, 10, 0)
        fps_layout.setSpacing(5)
        
        fps_icon = QLabel("📊")
        fps_layout.addWidget(fps_icon)
        
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setObjectName("infoLabel")
        fps_layout.addWidget(self.total_time_label)
        #ps_layout.addWidget(self.fps_label)
        
        center_info.addWidget(fps_widget)
        
        controls_layout.addLayout(center_info)
        
        # Espaciador
        controls_layout.addStretch()
        
        # Grupo derecho - Controles adicionales
        right_controls = QHBoxLayout()
        right_controls.setSpacing(10)
        
        # Control de velocidad
        speed_widget = QWidget()
        speed_layout = QHBoxLayout(speed_widget)
        speed_layout.setContentsMargins(5, 0, 5, 0)
        speed_layout.setSpacing(5)
        
        speed_icon = QLabel("⚡")
        speed_layout.addWidget(speed_icon)
        
        self.speed_combo = QComboBox()
        self.speed_combo.setObjectName("speedCombo")
        self.speed_combo.addItems(["0.25x", "0.5x", "0.75x", "1x", "1.25x", "1.5x", "2x"])
        self.speed_combo.setCurrentText("1x")
        self.speed_combo.currentTextChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.speed_combo)
        
        right_controls.addWidget(speed_widget)
        
        # Control de volumen
        volume_widget = QWidget()
        volume_layout = QHBoxLayout(volume_widget)
        volume_layout.setContentsMargins(5, 0, 5, 0)
        volume_layout.setSpacing(5)
        
        self.btn_volume = QPushButton("🔊")
        self.btn_volume.setObjectName("volumeButton")
        self.btn_volume.setCheckable(True)
        self.btn_volume.setFixedSize(30, 30)
        self.btn_volume.clicked.connect(self.on_volume_clicked)
        volume_layout.addWidget(self.btn_volume)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("70%")
        self.volume_label.setObjectName("volumeLabel")
        self.volume_label.setMinimumWidth(35)
        volume_layout.addWidget(self.volume_label)
        
        right_controls.addWidget(volume_widget)
        
        # Botón de pantalla completa
        self.btn_fullscreen = self.create_control_button("⛶", "Pantalla completa", "fullscreenButton")
        right_controls.addWidget(self.btn_fullscreen)
        
        controls_layout.addLayout(right_controls)
        
        main_layout.addLayout(controls_layout)
        
    def create_control_button(self, text, tooltip, object_name):
        """Crear un botón de control con estilo consistente"""
        btn = QPushButton(text)
        btn.setObjectName(object_name)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        
        if object_name == "playButton":
            btn.setFixedSize(45, 45)
        elif object_name == "fullscreenButton":
            btn.setFixedSize(35, 35)
        else:
            btn.setFixedSize(35, 35)
            
        return btn
        
    def apply_styles(self):
        """Aplicar estilos CSS modernos"""
        self.setStyleSheet("""
            /* Contenedor principal */
            VideoControlBar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #34495e);
                border-radius: 10px;
                border: 1px solid #1a252f;
            }
            
            /* Etiquetas de tiempo */
            #timeLabel {
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial;
                font-size: 13px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.3);
                padding: 5px 10px;
                border-radius: 5px;
            }
            
            /* Etiquetas de información */
            #infoLabel {
                color: #bdc3c7;
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
            }
            
            /* Slider de progreso */
            #progressSlider::groove:horizontal {
                height: 8px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1a252f, stop: 1 #2c3e50);
                border-radius: 4px;
                border: 1px solid #16202a;
            }
            
            #progressSlider::handle:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
                border: 2px solid #ecf0f1;
            }
            
            #progressSlider::handle:horizontal:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5dade2, stop: 1 #3498db);
                border: 2px solid #ffffff;
            }
            
            #progressSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                border-radius: 4px;
            }
            
            /* Botones de control */
            #controlButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #34495e, stop: 1 #2c3e50);
                color: #ecf0f1;
                border: 1px solid #1a252f;
                border-radius: 5px;
                font-size: 16px;
            }
            
            #controlButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4a5f7f, stop: 1 #34495e);
                border: 1px solid #3498db;
            }
            
            #controlButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #1a252f);
            }
            
            /* Botón Play/Pause */
            #playButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #27ae60, stop: 1 #229954);
                color: white;
                border: 2px solid #1e8449;
                border-radius: 22px;
                font-size: 20px;
                font-weight: bold;
            }
            
            #playButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2ecc71, stop: 1 #27ae60);
                border: 2px solid #27ae60;
            }
            
            #playButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #229954, stop: 1 #1e8449);
            }
            
            /* Botón de volumen */
            #volumeButton {
                background: transparent;
                border: none;
                font-size: 18px;
            }
            
            #volumeButton:hover {
                background: rgba(52, 152, 219, 0.2);
                border-radius: 15px;
            }
            
            #volumeButton:checked {
                color: #e74c3c;
            }
            
            /* Slider de volumen */
            #volumeSlider::groove:horizontal {
                height: 4px;
                background: #34495e;
                border-radius: 2px;
            }
            
            #volumeSlider::handle:horizontal {
                background: #3498db;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            
            #volumeSlider::sub-page:horizontal {
                background: #3498db;
                border-radius: 2px;
            }
            
            /* Etiqueta de volumen */
            #volumeLabel {
                color: #95a5a6;
                font-size: 11px;
            }
            
            /* ComboBox de velocidad */
            #speedCombo {
                background: #34495e;
                color: #ecf0f1;
                border: 1px solid #2c3e50;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                min-width: 70px;
            }
            
            #speedCombo:hover {
                background: #4a5f7f;
                border: 1px solid #3498db;
            }
            
            #speedCombo::drop-down {
                border: none;
                width: 20px;
            }
            
            #speedCombo::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ecf0f1;
                margin-right: 5px;
            }
            
            #speedCombo QAbstractItemView {
                background: #34495e;
                color: #ecf0f1;
                selection-background-color: #3498db;
                border: 1px solid #2c3e50;
            }
            
            /* Botón pantalla completa */
            #fullscreenButton {
                background: transparent;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 5px;
                font-size: 18px;
            }
            
            #fullscreenButton:hover {
                background: rgba(52, 152, 219, 0.2);
                border: 1px solid #3498db;
            }
        """)
        
    # === MÉTODOS DE CONTROL ===
    
    def on_play_pause_clicked(self):
        """Manejar click en play/pause"""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.btn_play_pause.setText("⏸")
            self.btn_play_pause.setToolTip("Pausar")
            self.playClicked.emit()
        else:
            self.btn_play_pause.setText("▶")
            self.btn_play_pause.setToolTip("Reproducir")
            self.pauseClicked.emit()
            
    def on_stop_clicked(self):
        """Manejar click en stop"""
        self.is_playing = False
        self.btn_play_pause.setText("▶")
        self.btn_play_pause.setToolTip("Reproducir")
        self.stopClicked.emit()
        
    def on_previous_clicked(self):
        """Manejar click en frame anterior"""
        self.previousFrameClicked.emit()
        
    def on_next_clicked(self):
        """Manejar click en frame siguiente"""
        self.nextFrameClicked.emit()
        
    def on_beginning_clicked(self):
        """Manejar click en ir al inicio"""
        self.beginningClicked.emit()
        
    def on_end_clicked(self):
        """Manejar click en ir al final"""
        self.endClicked.emit()
        
    def on_volume_clicked(self):
        """Manejar click en botón de volumen (mute/unmute)"""
        if self.btn_volume.isChecked():
            self.btn_volume.setText("🔇")
            self.volume_slider.setValue(0)
        else:
            self.btn_volume.setText("🔊")
            self.volume_slider.setValue(70)
            
    def on_volume_changed(self, value):
        """Manejar cambio de volumen"""
        self.volume_label.setText(f"{value}%")
        
        if value == 0:
            self.btn_volume.setText("🔇")
            self.btn_volume.setChecked(True)
        elif value < 33:
            self.btn_volume.setText("🔈")
            self.btn_volume.setChecked(False)
        elif value < 66:
            self.btn_volume.setText("🔉")
            self.btn_volume.setChecked(False)
        else:
            self.btn_volume.setText("🔊")
            self.btn_volume.setChecked(False)
            
        self.volumeChanged.emit(value)
        
    def on_speed_changed(self, text):
        """Manejar cambio de velocidad"""
        speed = float(text.replace('x', ''))
        self.speedChanged.emit(speed)
        
    def on_slider_pressed(self):
        """Manejar cuando se presiona el slider"""
        pass
        
    def on_slider_moved(self, position):
        """Manejar movimiento del slider"""
        if self.total_frames > 0:
            frame = int((position / 100) * self.total_frames)
            self.update_frame_info(frame)
            self.positionChanged.emit(frame)
            
    def on_slider_released(self):
        """Manejar cuando se suelta el slider"""
        pass
        
    # === MÉTODOS DE ACTUALIZACIÓN ===
    
    def set_video_info(self, total_frames, fps):
        """Establecer información del video"""
        self.total_frames = total_frames
        self.total_frames2 = total_frames
        self.video_info = {'total_frames': total_frames, 'fps': fps}
        self.fps = fps
        self.duration = total_frames / fps if fps > 0 else 0
        
        # Actualizar slider
        self.progress_slider.setMaximum(100)
        
        # Actualizar labels
        self.update_time_labels()
        self.fps_label.setText(f"FPS: {fps:.1f}")
        
    def update_frame_info(self, frame_number):
        """Actualizar información del frame actual"""
        self.current_frame = frame_number
        
        # Actualizar slider sin triggear señales
        self.progress_slider.blockSignals(True)
        print(self.total_frames)
        #print(self.video_info)
        if self.total_frames > 0:
            progress = int((frame_number / self.total_frames) * 100)
            self.progress_slider.setValue(progress)
        self.progress_slider.blockSignals(False)
        
        # Actualizar labels
        self.update_time_labels()
        #self.frame_label.setText(f"Frame: {frame_number:,} / {self.total_frames:,}")
        self.total_time_label.setText(f"{frame_number:,} ")
        #self.update_frame_info(frame_number)
        
    def update_time_labels(self):
        """Actualizar las etiquetas de tiempo"""
        if self.fps > 0:
            current_time = self.current_frame / self.fps
            total_time = self.total_frames / self.fps
            current_frame = self.total_frames
            current_str = self.format_time(current_time)
            total_str = self.format_time(total_time)
            
            self.total_time_label.setText(f"Frame: {self.current_frame:,}")
            self.current_time_label.setText(current_str)
        
    def update_time_labels2(self,seconds):
        time = self.format_time(seconds)
        """Actualizar las etiquetas de tiempo"""
        self.current_time_label.setText(time)
            
    def format_time(self, seconds):
        """Formatear tiempo en HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
    def reset(self):
        """Resetear todos los controles"""
        self.is_playing = False
        self.current_frame = 0
        self.total_frames