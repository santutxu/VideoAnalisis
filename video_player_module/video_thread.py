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
