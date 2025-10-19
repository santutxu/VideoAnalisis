"""
Widget de reproducción de video con OpenCV y PyQt5
"""
from components.video_controller_bar import VideoControlBar 

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont
import cv2
import numpy as np

class VideoThread(QThread):
    """Thread para procesamiento de video sin bloquear la UI."""
    frame_ready = pyqtSignal(np.ndarray)
    position_changed = pyqtSignal(float,int)
    
    def __init__(self):
        super().__init__()
        self.cap = None
        self.is_playing = False
        self.current_position = 0
        self.current_frame = 0
        self.fps = 30
        self.frame_delay = 33  # milliseconds
        
    def load_video(self, path):
        """Carga un video desde archivo."""
        if self.cap:
            self.cap.release()
            
        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_delay = int(1000 / self.fps)
        
    def play(self):
        """Inicia la reproducción."""
        self.is_playing = True
        
    def pause(self):
        """Pausa la reproducción."""
        self.is_playing = False
        
    def seek(self, position):
        """Salta a una posición específica (en segundos)."""
        if self.cap:
            frame_number = int(position * self.fps)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.current_position = position
            
    def run(self):
        """Loop principal del thread."""
        while self.cap:
            if self.is_playing:
                ret, frame = self.cap.read()
                if ret:
                    self.frame_ready.emit(frame)
                    
                    # Actualizar posición
                    frame_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                    time_pos = frame_pos / self.fps
                    self.position_changed.emit(time_pos,int(frame_pos))
                    self.msleep(self.frame_delay)
                else:
                    self.is_playing = False
            else:
                self.msleep(100)

class VideoPlayerWidget(QWidget):
    """
    Widget principal del reproductor de video con capacidades de overlay.
    """
    
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
    
    
    position_changed = pyqtSignal(float,int)
    duration_changed = pyqtSignal(float,float,float)
    
    def __init__(self):
        super().__init__()
        
        self.video_thread = VideoThread()
        self.controls_bar = VideoControlBar()
        self.current_frame = None
        self.current_time = None
        self.total_frames = None
        self.fps = None
        self.duration = 0
        self.is_playing = False
        
        # Overlays para dibujo
        self.zones = []  # Lista de zonas dibujadas
        self.current_drawing = []  # Puntos del polígono actual
        self.is_drawing_mode = False
        self.video_current_position = 0
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Configura la interfaz del reproductor."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label para mostrar el video
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Habilitar eventos de mouse para dibujo
        self.video_label.setMouseTracking(True)
        self.video_label.mousePressEvent = self.mouse_press_event
        self.video_label.mouseMoveEvent = self.mouse_move_event
        self.video_label.mouseReleaseEvent = self.mouse_release_event
        
        layout.addWidget(self.video_label)
        layout.addWidget(self.controls_bar)
        self.setLayout(layout)
        
    def _connect_signals(self):
        """Conecta las señales del thread de video."""
        self.video_thread.frame_ready.connect(self.update_frame)
        self.video_thread.position_changed.connect(self.on_position_update)
        self.controls_bar.playClicked.connect(self.play)
        self.controls_bar.pauseClicked.connect(self.pause)
        self.controls_bar.stopClicked.connect(self.stop)
        self.controls_bar.speedChanged.connect(self.on_speedChanged)
        self.controls_bar.previousFrameClicked.connect(self.on_previus_frame)
        self.controls_bar.nextFrameClicked.connect(self.on_next_frame)
        self.controls_bar.beginningClicked.connect(self.on_beginning_frame)
        self.controls_bar.endClicked.connect(self.on_end_frame)
        #self.controls_bar.volumeChanged.connect(self.update_frame)
        #self.controls_bar.speedChanged.connect(self.update_frame)
        #self.controls_bar.positionChanged.connect(self.update_frame)
        
    def on_previus_frame(self):
        print("previousFrameClicked") 
        
    def on_next_frame(self):
        print("nextFrameClicked")    
        
    def on_beginning_frame(self):
        print("beginningClicked")      
        
    def on_end_frame(self):
        print("endClicked")     
        
    def load_video(self, path):
        """Carga un video desde archivo."""
        self.video_thread.load_video(path)
        
        # Obtener duración
        cap = cv2.VideoCapture(path)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.total_frames = frame_count
        self.duration = frame_count / self.fps
        cap.release()
        
        self.duration_changed.emit(self.duration,frame_count,self.fps)
        
        # Iniciar thread
        if not self.video_thread.isRunning():
            self.video_thread.start()
            
        # Mostrar primer frame
        self.video_thread.seek(0)
        self.video_thread.is_playing = False
        self.update_single_frame()
        self.controls_bar.setDisabled(False)
        
    def update_frame(self, frame):
        """Actualiza el frame mostrado."""
        self.current_frame = frame
        
        # Convertir a QImage
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        
        # Convertir BGR a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        q_image = QImage(frame_rgb.data, width, height, 
                        bytes_per_line, QImage.Format_RGB888)
        
        # Escalar para ajustar al widget
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Dibujar overlays si existen
        if self.zones or self.current_drawing:
            scaled_pixmap = self.draw_overlays(scaled_pixmap)
            
        self.video_label.setPixmap(scaled_pixmap)
        
    def draw_overlays(self, pixmap):
        """Dibuja las zonas y elementos sobre el video."""
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dibujar zonas guardadas
        for zone in self.zones:
            pen = QPen(QColor(zone['color']), 2)
            painter.setPen(pen)
            
            # Dibujar polígono
            points = zone['points']
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                painter.drawLine(p1[0], p1[1], p2[0], p2[1])
                
            # Dibujar nombre de la zona
            if points:
                painter.setFont(QFont("Arial", 12, QFont.Bold))
                center_x = sum(p[0] for p in points) / len(points)
                center_y = sum(p[1] for p in points) / len(points)
                painter.drawText(int(center_x), int(center_y), zone['name'])
        
        # Dibujar polígono en construcción
        if self.current_drawing:
            pen = QPen(QColor(255, 255, 0), 2, Qt.DashLine)
            painter.setPen(pen)
            
            for i in range(len(self.current_drawing) - 1):
                p1 = self.current_drawing[i]
                p2 = self.current_drawing[i + 1]
                painter.drawLine(p1[0], p1[1], p2[0], p2[1])
                
        painter.end()
        return pixmap
        
    def play(self):
        """Inicia la reproducción del video."""
        self.is_playing = True
        self.video_thread.play()
        self.playClicked.emit()
        
    def pause(self):
        """Pausa la reproducción."""
        self.is_playing = False
        self.video_thread.pause()
        self.pauseClicked.emit()
        
    def stop(self):
        """Detiene la reproducción y vuelve al inicio."""
        self.is_playing = False
        self.video_thread.pause()
        self.video_thread.seek(0)
        self.update_single_frame()
        
    def set_position(self, position):
        """Establece la posición de reproducción (en segundos)."""
        self.video_thread.seek(position)
        if not self.is_playing:
            self.update_single_frame()
            
    def get_position(self):
        """Obtiene la posición actual en segundos."""
        return self.video_current_position
        
    def get_duration(self):
        """Obtiene la duración total del video."""
        return self.duration
        
    def set_playback_speed(self, speed):
        """Ajusta la velocidad de reproducción."""
        if speed > 0:
            self.video_thread.frame_delay = int((1000 / self.video_thread.fps) / speed)
            
    def update_single_frame(self):
        """Actualiza un solo frame cuando está pausado."""
        if self.video_thread.cap:
            ret, frame = self.video_thread.cap.read()
            if ret:
                self.update_frame(frame)
                # Retroceder un frame para mantener la posición
                current_pos = self.video_thread.cap.get(cv2.CAP_PROP_POS_FRAMES)
                self.video_thread.cap.set(cv2.CAP_PROP_POS_FRAMES, current_pos - 1)
                
    def on_position_update(self, position, frame_num):
        """Maneja la actualización de posición desde el thread."""
        self.current_time = position
        self.current_frame = frame_num
        self.video_current_position = position
        self.controls_bar.update_frame_info(frame_num)
        self.position_changed.emit(position,frame_num)
        
    def toggle_drawing_mode(self):
        """Activa/desactiva el modo de dibujo de zonas."""
        self.is_drawing_mode = not self.is_drawing_mode
        self.current_drawing = []
        
    def mouse_press_event(self, event):
        """Maneja clicks del mouse para dibujo de zonas."""
        if self.is_drawing_mode and event.button() == Qt.LeftButton:
            # Añadir punto al polígono actual
            pos = (event.x(), event.y())
            self.current_drawing.append(pos)
            
            # Actualizar visualización
            if not self.is_playing:
                self.update_single_frame()
                
        elif event.button() == Qt.RightButton and self.current_drawing:
            # Cerrar polígono y guardar zona
            if len(self.current_drawing) >= 3:
                self.save_current_zone()
                
    def save_current_zone(self):
        """Guarda la zona dibujada actual."""
        if self.current_drawing:
            zone = {
                'name': f"Zona {len(self.zones) + 1}",
                'points': self.current_drawing.copy(),
                'color': '#4CAF50'
            }
            self.zones.append(zone)
            self.current_drawing = []
            
            if not self.is_playing:
                self.update_single_frame()
                
    def mouse_move_event(self, event):
        """Maneja el movimiento del mouse."""
        pass  # Puede usarse para preview de líneas
        
    def mouse_release_event(self, event):
        """Maneja la liberación del botón del mouse."""
        pass
    
    def on_speedChanged(self, speed):
        self.speedChanged.emit(speed)