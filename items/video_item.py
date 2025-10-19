import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


import cv2
import numpy as np
from datetime import timedelta
class VideoItem(QListWidgetItem):
    """Item personalizado para la lista de videos"""
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.duration = self.get_video_duration()
        self.fps = self.get_video_fps()
        
        # Mostrar nombre y duración
        duration_str = self.format_time(self.duration)
        self.setText(f"{self.filename}\n[{duration_str}] - {self.fps:.1f} fps")
        #self.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        
    def get_video_duration(self):
        """Obtener la duración del video en milisegundos usando OpenCV"""
        try:
            cap = cv2.VideoCapture(self.filepath)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            
            if fps > 0:
                duration_seconds = frame_count / fps
                return int(duration_seconds * 1000)
            return 5000  # Default 5 segundos
        except:
            return 5000
            
    def get_video_fps(self):
        """Obtener los FPS del video"""
        try:
            cap = cv2.VideoCapture(self.filepath)
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            return fps if fps > 0 else 30.0
        except:
            return 30.0
        
    def format_time(self, milliseconds):
        """Formatear tiempo de milisegundos a HH:MM:SS"""
        seconds = milliseconds / 1000
        return str(timedelta(seconds=int(seconds)))