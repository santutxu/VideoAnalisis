import os
import cv2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from utils.time_utils import format_time

                
class TimelineItem(QGraphicsRectItem):
    """Item del timeline representando un video con thumbnail"""
    item_click= pyqtSignal(int)
    partial_selection_changed = pyqtSignal(float, float) # inicio_ms, fin_ms
    def __init__(self, video_path, x, y, duration_ms, pixels_per_second=10, start_trim=0, end_trim=None):
        # Calcular el ancho basado en la duración
        self.original_duration_ms = duration_ms
        self.start_trim = start_trim # Punto de inicio en ms
        self.end_trim = end_trim if end_trim is not None else duration_ms # Punto final en ms
        self.actual_duration_ms = self.end_trim - self.start_trim
        self.selections = []
        width = (self.actual_duration_ms / 1000) * pixels_per_second
        self.final_end = width
        height = 60
        
        super().__init__(x, y, width, height)
        #super().setY(y)  # Asegurar que esté por encima de otros elementos
        self.video_path = video_path
        self.video_name = os.path.basename(video_path)
        self.pixels_per_second = pixels_per_second
        
        # Estilo del item
        self.normal_color = QColor(100, 150, 200)
        self.selected_color = QColor(150, 200, 250)
        self.active_color = QColor(200, 100, 100)
        self.is_active = False  
        self.acceptHoverEvents = True

        
        # ========== VARIABLES DE SELECCIÓN PARCIAL ==========
        self.is_selecting = False
        self.selection_start_x = 0
        self.selection_end_x = 0
        self.selection_start_time = 0
        self.selection_end_time = 0
        
        # Crear rectángulo de selección (inicialmente invisible)
        self._create_selection_rect()
        
        # Habilitar eventos del mouse
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        
        self._setup_item()
        self._create_ui_elements()
        self.add_thumbnail()
        
    def _setup_item(self):
        """Configurar las propiedades del item"""
        self.setBrush(QBrush(self.normal_color))
        self.setPen(QPen(Qt.black, 2))
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
    def _create_ui_elements(self):
        """Crear elementos UI del item"""
        # Texto con el nombre del video
        
        self.text = QGraphicsTextItem()
        self.text.setParentItem(self)
        self.update_text()
        self.text.setDefaultTextColor(Qt.white)
        
        # Indicador de duración y trim
        duration_text = format_time(self.actual_duration_ms)
        if self.start_trim > 0 or self.end_trim < self.original_duration_ms:
            trim_info = f" [{format_time(self.start_trim)}-{format_time(self.end_trim)}]"
            duration_text += trim_info
            
        self.duration_label = QGraphicsTextItem(duration_text)
        self.duration_label.setParentItem(self)
        self.duration_label.setPos(5, 40)#self.rect().height() - 25
        self.duration_label.setDefaultTextColor(Qt.yellow)
        font = QFont("Arial", 8)
        self.duration_label.setFont(font)
        
        
        # Manijas de redimensionamiento
        self._create_handles()
        #self._create_end_circle()
      
    def create_event_clip(self, evento):
        print  (f"Creating event clip : {evento}")
        
        
    def _create_handles(self):
        """Crear manijas de redimensionamiento"""
        height = self.rect().height()
        width = self.rect().width()
        
        self.left_handle = QGraphicsRectItem(0, 30, 5, 70)
        self.left_handle.setParentItem(self)
        self.left_handle.setBrush(QBrush(Qt.yellow))
        self.left_handle.setCursor(Qt.SizeHorCursor)
        
        self.right_handle = QGraphicsRectItem(width-5, 30, 5, 70)
        self.right_handle.setParentItem(self)
        self.right_handle.setBrush(QBrush(Qt.red))
        self.right_handle.setCursor(Qt.SizeHorCursor)
        x2 = self.right_handle.x()
        x2 = self.right_handle
        
    def _create_end_circle(self):
        circle_x = self.rect().width()
        circle_y = self.rect().height() / 2
        circle_radius = 8
        self.end_circle = QGraphicsEllipseItem(circle_x - circle_radius, circle_y - circle_radius,
                                               circle_radius * 2, circle_radius * 2)
        self.end_circle.setParentItem(self)
        self.end_circle.setBrush(QBrush(Qt.green))
        self.end_circle.setCursor(Qt.SizeAllCursor)
        self.end_circle.setAcceptHoverEvents(True)
        
        
    def calculate_end_position(self):
        local_end_x = self.rect().x() + self.rect().width()
        local_end_y = self.rect().y() / 2   
        
        item_pos = self.scenePos()
        scene_end_x = item_pos.x() + local_end_x
        scene_end_y = item_pos.y() + local_end_y
        #scene_end_x = self.mapToScene(QPointF(local_end_x, 0)).x()
        return QPointF(scene_end_x, scene_end_y)
        
    def update_zoom(self, new_pixels_per_second):
        """Actualizar el item cuando cambia el zoom"""
        """Crear manijas de redimensionamiento"""
        width1 = self.final_end
        self.pixels_per_second = new_pixels_per_second
        new_width = (self.actual_duration_ms / 1000) * new_pixels_per_second
        width2 = new_width - width1
        print(f"Updating zoom for {self.video_name}: new width {new_width}: new height {self.rect().height()}")
        print(f"Updating zoom: new x: {self.x()}, new y: {self.y()}")
       
        # Actualizar el rectángulo
        self.setRect(self.x(), 40, new_width, self.rect().height())
        
        print(f"Creating TimelineItem: x: {super().x()}, y: {super().y()}")
        print(f"Creating TimelineItem: x: {self.rect().x()}, y: {self.rect().y()}, width: {self.rect().width()}, height: {self.rect().height()}")
        width = self.rect().width()
        x = self.rect().x()
        y = self.rect().y()
        w = self.rect().width()
        h = self.rect().height()
        x1 = self.x()
        y1 = self.y()
        left_pos = x
        right_pos = x+w-5
        x2 = self.right_handle
        x3 = self.calculate_end_position()
        # Actualizar posición de la manija derecha
        self.right_handle.setPos(width2, 0)
        
        # Actualizar texto
        self.update_text()
        
    def set_active(self, active):
        """Marcar el item como activo (reproduciéndose)"""
        self.is_active = active
        if active:
            self.setBrush(QBrush(self.active_color))
        elif self.isSelected():
            self.setBrush(QBrush(self.selected_color))
        else:
            self.setBrush(QBrush(self.normal_color))
    
    def add_thumbnail(self):
        """Añadir thumbnail del video al item"""
        try:
            cap = cv2.VideoCapture(self.video_path)
            
            # Saltar al frame del start_trim si es necesario
            if self.start_trim > 0:
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_number = int((self.start_trim / 1000) * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            # Leer varios frames para obtener uno bueno
            for _ in range(5):
                ret, frame = cap.read()
                if not ret:
                    break
                    
            if ret:
                self._process_thumbnail(frame)
                
            cap.release()
        except Exception as e:
            print(f"Error generando thumbnail: {e}")
            
    def _process_thumbnail(self, frame):
        """Procesar y mostrar el thumbnail"""
        height = 50
        aspect_ratio = frame.shape[1] / frame.shape[0]
        width = int(height * aspect_ratio)
        
        max_width = min(int(self.rect().width() - 10), width)
        if max_width < width:
            width = max_width
            height = int(width / aspect_ratio)
        
        thumbnail = cv2.resize(frame, (width, height))
        thumbnail = cv2.cvtColor(thumbnail, cv2.COLOR_BGR2RGB)
        
        h, w, ch = thumbnail.shape
        bytes_per_line = ch * w
        qt_image = QImage(thumbnail.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setParentItem(self)
        pixmap_item.setPos(5, 5)
        pixmap_item.setOpacity(0.3)
        
    def update_text(self):
        """Actualizar el texto mostrado en el item"""
        max_chars = int(self.rect().width() / 8)
        if len(self.video_name) > max_chars and max_chars > 3:
            display_name = self.video_name[:max_chars-3] + "..."
        else:
            display_name = self.video_name
        self.text.setPlainText(display_name)
        self.text.setPos(5, 45)
        
    def on_click(self):
        print(f"Clicked on ")
        
    def itemChange(self, change, value):
        """Manejar cambios en el item"""
        if change == QGraphicsItem.ItemPositionChange:
            new_pos = value
            new_pos.setY(self.y())
            if new_pos.x() < 0:
                new_pos.setX(0)
            return new_pos
        elif change == QGraphicsItem.ItemSelectedChange:
            if not self.is_active:
                if value:
                    self.setBrush(QBrush(self.selected_color))
                else:
                    self.setBrush(QBrush(self.normal_color))
        return super().itemChange(change, value)
    
    def _create_selection_rect(self):
        """Crear el rectángulo de selección parcial"""
        self.selection_rect = QGraphicsRectItem(0, 0, 0, self.rect().height())
        self.selection_rect.setParentItem(self)
        
        # Estilo del rectángulo de selección
        self.selection_rect.setBrush(QBrush(QColor(255, 255, 0, 80))) # Amarillo semi-transparente
        self.selection_rect.setPen(QPen(QColor(255, 200, 0), 2, Qt.DashLine)) # Borde amarillo punteado
        self.selection_rect.setZValue(15) # Por encima de otros elementos
        self.selection_rect.setVisible(False) # Inicialmente oculto
        
        # Etiqueta de tiempo de selección
        self.selection_label = QGraphicsTextItem()
        self.selection_label.setParentItem(self.selection_rect)
        self.selection_label.setDefaultTextColor(Qt.black)
        self.selection_label.setFont(QFont("Arial", 9, QFont.Bold))
        self.selection_label.setZValue(16)
        self.selection_label.setVisible(False)
        
    def mousePressEvent(self, event):
        """Iniciar selección parcial con click izquierdo + Shift"""
        if event.button() == Qt.LeftButton and event.modifiers() & Qt.ShiftModifier:
            # Iniciar selección parcial
            self.is_selecting = True
            
            # Obtener posición local del click
            local_pos = event.pos()
            self.selection_start_x = max(0, min(local_pos.x(), self.rect().width()))
            self.selection_end_x = self.selection_start_x
            
            # Calcular tiempo de inicio
            self.selection_start_time = self._position_to_time(self.selection_start_x)
            
            # Mostrar rectángulo de selección
            self.selection_rect.setVisible(True)
            self._update_selection_rect()
            
            event.accept()
        else:
            # Comportamiento normal
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        """Actualizar selección mientras se arrastra"""
        if self.is_selecting:
            # Obtener posición actual
            local_pos = event.pos()
            self.selection_end_x = max(0, min(local_pos.x(), self.rect().width()))
            
            # Actualizar rectángulo de selección
            self._update_selection_rect()
            
            # Actualizar cursor
            self.setCursor(Qt.CrossCursor)
            
            event.accept()
        else:
            # Si no está seleccionando, mostrar cursor apropiado
            if event.modifiers() & Qt.ShiftModifier:
                self.setCursor(Qt.CrossCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        """Finalizar selección"""
        if self.is_selecting and event.button() == Qt.LeftButton:
            self.is_selecting = False
            
            # Calcular tiempo final
            self.selection_end_time = self._position_to_time(self.selection_end_x)
            
            # Asegurar que start < end
            if self.selection_start_x > self.selection_end_x:
                self.selection_start_x, self.selection_end_x = self.selection_end_x, self.selection_start_x
                self.selection_start_time, self.selection_end_time = self.selection_end_time, self.selection_start_time
            
            # Verificar que la selección sea válida (mínimo 100ms)
            if abs(self.selection_end_time - self.selection_start_time) > 100:
                # Emitir señal con los tiempos seleccionados
                self.partial_selection_changed.emit(
                    self.selection_start_time,
                    self.selection_end_time
                )
                
                # Mostrar información de la selección
                self._show_selection_info()
            else:
                # Selección muy pequeña, ocultar
                self.clear_selection()
                
            # Restaurar cursor
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
            
    def _update_selection_rect(self):
        """Actualizar el rectángulo de selección visual"""
        # Calcular dimensiones del rectángulo
        start_x = min(self.selection_start_x, self.selection_end_x)
        end_x = max(self.selection_start_x, self.selection_end_x)
        width = end_x - start_x
        
        # Actualizar rectángulo
        self.selection_rect.setRect(start_x, 40, width, self.rect().height())
        
        # Actualizar etiqueta con duración de la selección
        if width > 20: # Solo mostrar si hay espacio
            start_time = self._position_to_time(start_x)
            end_time = self._position_to_time(end_x)
            duration = end_time - start_time
            
            # Formato de texto
            duration_text = format_time(duration)
            range_text = f"{format_time(start_time)} - {format_time(end_time)}"
            
            self.selection_label.setPlainText(f"{duration_text}\n{range_text}")
            self.selection_label.setPos(start_x + 5, 5)
            self.selection_label.setVisible(True)
        else:
            self.selection_label.setVisible(False)
            
    def update_selection_rect(self,time_estart, time_end):
        """Actualizar el rectángulo de selección visual"""
        # Calcular dimensiones del rectángulo
        #start_x = min(self.selection_start_x, self.selection_end_x)
        #end_x = max(self.selection_start_x, self.selection_end_x)
        time_estart = time_estart * 1000
        time_end = time_end * 1000
        start_x = self._time_to_position(time_estart)
        end_x = self._time_to_position(time_end)
        width = end_x - start_x
        
        # Actualizar rectángulo
        self.selection_rect.setRect(start_x, 40, width, self.rect().height())
        
        # Actualizar etiqueta con duración de la selección
        if width > 20: # Solo mostrar si hay espacio
            start_time = self._position_to_time(start_x)
            end_time = self._position_to_time(end_x)
            duration = end_time - start_time
            
            # Formato de texto
            duration_text = format_time(duration)
            range_text = f"{format_time(start_time)} - {format_time(end_time)}"
            
            self.selection_label.setPlainText(f"{duration_text}\n{range_text}")
            self.selection_label.setPos(start_x + 5, 5)
            self.selection_label.setVisible(True)
        else:
            self.selection_label.setVisible(False)
            
    def _position_to_time(self, x_position):
        """Convertir posición X local a tiempo en milisegundos"""
        # Proporción de la posición en el ancho total
        ratio = x_position / self.rect().width() if self.rect().width() > 0 else 0
        
        # Calcular tiempo relativo al clip
        relative_time = ratio * self.actual_duration_ms
        
        # Añadir el offset del trim inicial
        absolute_time = self.start_trim + relative_time
        
        return absolute_time
        
    def _time_to_position(self, time_ms):
        """Convertir tiempo en milisegundos a posición X local"""
        # Tiempo relativo al clip
        relative_time = time_ms - self.start_trim
        
        # Proporción del tiempo en la duración total
        ratio = relative_time / self.actual_duration_ms if self.actual_duration_ms > 0 else 0
        
        # Calcular posición X
        x_position = ratio * self.rect().width()
        
        return x_position
        
    def _show_selection_info(self):
        """Mostrar información sobre la selección"""
        duration = self.selection_end_time - self.selection_start_time
        
        # Crear tooltip temporal con información
        tooltip_text = (
            f"Selección:\n"
            f"Inicio: {format_time(self.selection_start_time)}\n"
            f"Fin: {format_time(self.selection_end_time)}\n"
            f"Duración: {format_time(duration)}"
        )
        
        # Actualizar tooltip del rectángulo de selección
        self.selection_rect.setToolTip(tooltip_text)
        
    def clear_selection(self):
        """Limpiar la selección actual"""
        self.selection_rect.setVisible(False)
        self.selection_label.setVisible(False)
        self.selection_start_x = 0
        self.selection_end_x = 0
        self.selection_start_time = 0
        self.selection_end_time = 0
        
    def has_selection(self):
        """Verificar si hay una selección activa"""
        return self.selection_rect.isVisible() and (self.selection_end_x != self.selection_start_x)
        
    def get_selection_range(self):
        """Obtener el rango de tiempo seleccionado"""
        if self.has_selection():
            return {
                'start_ms': self.selection_start_time,
                'end_ms': self.selection_end_time,
                'duration_ms': self.selection_end_time - self.selection_start_time,
                'start_formatted': format_time(self.selection_start_time),
                'end_formatted': format_time(self.selection_end_time),
                'duration_formatted': format_time(self.selection_end_time - self.selection_start_time)
            }
        return None
        
    def set_selection_range(self, start_ms, end_ms):
        """Establecer programáticamente un rango de selección"""
        # Validar que los tiempos estén dentro del clip
        start_ms = max(self.start_trim, min(start_ms, self.end_trim))
        end_ms = max(self.start_trim, min(end_ms, self.end_trim))
        
        # Asegurar que start < end
        if start_ms > end_ms:
            start_ms, end_ms = end_ms, start_ms
            
        # Convertir a posiciones
        self.selection_start_x = self._time_to_position(start_ms)
        self.selection_end_x = self._time_to_position(end_ms)
        self.selection_start_time = start_ms
        self.selection_end_time = end_ms
        
        # Mostrar selección
        self.selection_rect.setVisible(True)
        self._update_selection_rect()
        self._show_selection_info()
        
    def export_selection(self):
        """Crear un nuevo TimelineItem desde la selección"""
        if not self.has_selection():
            return None
            
        # Crear nuevo item con el rango seleccionado
        new_item = TimelineItem(
            self.video_path,
            0, # La posición X será establecida por el Timeline
            40,
            self.original_duration_ms,
            self.pixels_per_second,
            self.selection_start_time, # Nuevo start_trim
            self.selection_end_time # Nuevo end_trim
        )
        
        return new_item
        
    def highlight_selection(self, highlight=True):
        """Resaltar o des-resaltar la selección"""
        if self.has_selection():
            if highlight:
                # Resaltar con color más brillante
                self.selection_rect.setBrush(QBrush(QColor(255, 255, 0, 120)))
                self.selection_rect.setPen(QPen(QColor(255, 200, 0), 3, Qt.SolidLine))
            else:
                # Color normal
                self.selection_rect.setBrush(QBrush(QColor(255, 255, 0, 80)))
                self.selection_rect.setPen(QPen(QColor(255, 200, 0), 2, Qt.DashLine))
