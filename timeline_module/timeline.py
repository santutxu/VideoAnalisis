from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .timeline_item import TimelineItem
from .timeline_ruler import TimelineRuler
from .timeline_playhead_line import PlayheadLine
from .timeline_cutline import CutLine

class Timeline(QGraphicsView):
    """Widget del timeline mejorado con zoom y corte"""
    
    video_selected = pyqtSignal(str)
    timeline_changed = pyqtSignal()
    zoom_changed = pyqtSignal(int)
    playhead_moved = pyqtSignal(float)  # Emitir tiempo en segundos
    def __init__(self):
        super().__init__()
        self._setup_scene()
        self._setup_timeline_properties()
        self._create_timeline_elements()
        
        self.timeline_items = []
        self.next_available_x = 0
        self.current_active_item = None
        self.cut_mode = False
        self.current_time = 0.0
        self.current_frame = 0
        
        # Configuración de auto-scroll
        self.auto_scroll_config = {
            'enabled': True,
            'margin': 30,           # Píxeles de margen
            'smooth': True,          # Scroll suave animado
            'center_on_play': True,  # Centrar al iniciar reproducción
            'follow_during_play': True  # Seguir durante reproducción
        }
        
        # Animación para smooth scroll
        self.scroll_animation = QPropertyAnimation(self.horizontalScrollBar(), b"value")
        self.scroll_animation.setDuration(200)  # 200ms de duración
        self.scroll_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def _setup_scene(self):
        """Configurar la escena"""
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setMinimumHeight(150)
        self.setMaximumHeight(250)
        
    def _setup_timeline_properties(self):
        """Configurar propiedades del timeline"""
        self.min_pixels_per_second = 2
        self.max_pixels_per_second = 50
        self.pixels_per_second = 10
        self.timeline_duration = 1200
        self.timeline_width = self.timeline_duration * self.max_pixels_per_second
        self.timeline_height = 80
        
        self.scene.setSceneRect(0, 0, self.timeline_width, self.timeline_height + 30)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        
        
    def _reset_timeline_properties(self, mseconds, pps):
        seconds = mseconds / 1000
        duration = seconds * 0.2
        """Configurar propiedades del timeline"""
        print("Resetting timeline properties")
        print("seconds {mseconds} pps {pps}")
        self.min_pixels_per_second = 2
        self.max_pixels_per_second = 50
        self.pixels_per_second = pps
        self.timeline_duration = duration
        timeline_width = self.timeline_duration * self.max_pixels_per_second
        self.timeline_width = self.timeline_duration * self.max_pixels_per_second
        self.timeline_height = 80
        
        self.scene.setSceneRect(0, 0, self.timeline_width, self.timeline_height + 30)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    def _create_timeline_elements(self):
        """Crear elementos del timeline"""
        # Regla
        self.ruler = TimelineRuler(self.timeline_width, 30, self.pixels_per_second)
        self.scene.addItem(self.ruler)
        self.ruler.setPos(0, 0)
        
        # Fondo
        self.timeline_bg = QGraphicsRectItem(0, 30, self.timeline_width, self.timeline_height)
        self.timeline_bg.setBrush(QBrush(QColor(60, 60, 60)))
        self.timeline_bg.setPen(QPen(Qt.NoPen))
        self.scene.addItem(self.timeline_bg)
        
        # Líneas de guía
        self.guide_lines = []
        self.update_guide_lines()
        
        # Playhead
        self.playhead = PlayheadLine(self.timeline_height + 30)
        self.scene.addItem(self.playhead)
        self.playhead.setPos(0, 0)
        
        # Línea de corte
        self.cut_line = CutLine(self.timeline_height + 30)
        self.scene.addItem(self.cut_line)
    def _reset_timeline_elements(self, mseconds, pps):
        seconds = mseconds / 1000
        duration = seconds * 0.2
        """Crear elementos del timeline"""
        timeline_width = self.timeline_duration * self.max_pixels_per_second
        # Regla
        self.ruler = TimelineRuler(timeline_width, 30, self.pixels_per_second)
        self.scene.addItem(self.ruler)
        self.ruler.setPos(0, 0)
        
        # Fondo
        self.timeline_bg = QGraphicsRectItem(0, 30, timeline_width, self.timeline_height)
        self.timeline_bg.setBrush(QBrush(QColor(60, 60, 60)))
        self.timeline_bg.setPen(QPen(Qt.NoPen))
        self.scene.addItem(self.timeline_bg)
        
        # Líneas de guía
        self.guide_lines = []
        self.reset_guide_lines(duration)
        
        # Playhead
        self.playhead = PlayheadLine(self.timeline_height + 30)
        self.scene.addItem(self.playhead)
        self.playhead.setPos(0, 0)
        
        # Línea de corte
        self.cut_line = CutLine(self.timeline_height + 30)
        self.scene.addItem(self.cut_line)
        
    def update_guide_lines(self):
        """Actualizar las líneas de guía según el zoom"""
        # Eliminar líneas existentes
        for line in self.guide_lines:
            self.scene.removeItem(line)
        self.guide_lines.clear()
        
        # Determinar intervalo según zoom
        if self.pixels_per_second >= 20:
            interval = 5
        elif self.pixels_per_second >= 10:
            interval = 10
        elif self.pixels_per_second >= 5:
            interval = 20
        else:
            interval = 30
            
        # Crear nuevas líneas
        pen = QPen(QColor(80, 80, 80), 1, Qt.DashLine)
        for second in range(0, int(self.timeline_duration) + 1, interval):
            x = second * self.pixels_per_second
            if x <= self.timeline_width:
                line = self.scene.addLine(x, 30, x, self.timeline_height + 30, pen)
                line.setZValue(-1)
                self.guide_lines.append(line)
    def reset_guide_lines(self,duration):
        """Actualizar las líneas de guía según el zoom"""
        # Eliminar líneas existentes
        for line in self.guide_lines:
            self.scene.removeItem(line)
        self.guide_lines.clear()
        
        # Determinar intervalo según zoom
        if self.pixels_per_second >= 20:
            interval = 5
        elif self.pixels_per_second >= 10:
            interval = 10
        elif self.pixels_per_second >= 5:
            interval = 20
        else:
            interval = 30
            
        # Crear nuevas líneas
        pen = QPen(QColor(80, 80, 80), 1, Qt.DashLine)
        for second in range(0, int(duration) + 1, interval):
            x = second * self.pixels_per_second
            if x <= self.timeline_width:
                line = self.scene.addLine(x, 30, x, self.timeline_height + 30, pen)
                line.setZValue(-1)
                self.guide_lines.append(line)
    
    def set_zoom(self, value):
        """Establecer el nivel de zoom (0-100)"""
        zoom_range = self.max_pixels_per_second - self.min_pixels_per_second
        self.pixels_per_second = self.min_pixels_per_second + (value / 100) * zoom_range
        
        self.ruler.update_zoom(self.pixels_per_second)
        self.update_guide_lines()
        
        for item in self.timeline_items:
            item.update_zoom(self.pixels_per_second)
            
        self.reorganize_timeline()
        self.scene.update()
        
    def enable_cut_mode(self, enabled):
        """Activar/desactivar modo de corte"""
        self.cut_mode = enabled
        if enabled:
            self.setCursor(Qt.SplitHCursor)
            #self.cut_line.setVisible(True)
        else:
            self.setCursor(Qt.ArrowCursor)
            #self.cut_line.setVisible(False)
            
    def add_video(self, video_path, duration_ms, start_trim=0, end_trim=None):
        """Añadir un video al timeline automáticamente"""
        
        self.clear_timeline()
        
        self.timeline_duration = duration_ms / 1000
        self._reset_timeline_properties(duration_ms, self.pixels_per_second)
        self._reset_timeline_elements(duration_ms, self.pixels_per_second)
        
        
        x_pos = self.next_available_x
        
        item = TimelineItem(video_path, x_pos, 40, duration_ms, 
                           self.pixels_per_second, start_trim, end_trim)
        self.scene.addItem(item)
        self.timeline_items.append(item)
        self.set_active_item(item)
        
        item_width = (item.actual_duration_ms / 1000) * self.pixels_per_second
        self.next_available_x = x_pos + item_width + 0
        
        self.ensureVisible(item)

        #self.timeline_duration = 1200
        #self.timeline_width = self.timeline_duration * self.max_pixels_per_second
        self.timeline_changed.emit()
        self.scene.update()
        return item
        
    def split_item_at_position(self, item, split_x):
        """Dividir un item en la posición especificada"""
        if not isinstance(item, TimelineItem):
            return
            
        item_start_x = item.x()
        relative_x = split_x - item_start_x
        split_time_ms = (relative_x / self.pixels_per_second) * 1000 + item.start_trim
        
        if split_time_ms <= item.start_trim or split_time_ms >= item.end_trim:
            return
            
        # Crear dos nuevos items
        item1 = TimelineItem(
            item.video_path, 
            item_start_x, 
            40,
            item.original_duration_ms,
            self.pixels_per_second,
            item.start_trim,
            split_time_ms
        )
        
        item2_x = item_start_x + relative_x + 5
        item2 = TimelineItem(
            item.video_path,
            item2_x,
            40,
            item.original_duration_ms,
            self.pixels_per_second,
            split_time_ms,
            item.end_trim
        )
        
        # Remover el item original
        self.scene.removeItem(item)
        self.timeline_items.remove(item)
        
        # Añadir los nuevos items
        self.scene.addItem(item1)
        self.scene.addItem(item2)
        self.timeline_items.append(item1)
        self.timeline_items.append(item2)
        
        self.reorganize_timeline()
        self.timeline_changed.emit()
        
        return item1, item2
        
    def mouseMoveEvent(self, event):
        """Manejar movimiento del mouse"""
        super().mouseMoveEvent(event)
        
        if self.cut_mode:
            scene_pos = self.mapToScene(event.pos())
            self.cut_line.setPos(scene_pos.x(), 0)
            
    def mousePressEvent(self, event):
        """Detectar click en items del timeline"""
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            
            if self.cut_mode:
                item = self.scene.itemAt(scene_pos, QTransform())
                if isinstance(item, TimelineItem):
                    self.split_item_at_position(item, scene_pos.x())
                elif isinstance(item.parentItem(), TimelineItem):
                    self.split_item_at_position(item.parentItem(), scene_pos.x())
                self.enable_cut_mode(False)
            else:
                super().mousePressEvent(event)
                
                item = self.scene.itemAt(scene_pos, QTransform())
                if isinstance(item, TimelineItem):
                    self.set_active_item(item)
                    self.video_selected.emit(item.video_path)
                elif isinstance(item.parentItem(), TimelineItem):
                    self.set_active_item(item.parentItem())
                    self.video_selected.emit(item.parentItem().video_path)
                
                #self.set_playhead_position(scene_pos.x())
                self.playhead_moved.emit(scene_pos.x())
        else:
            super().mousePressEvent(event)
            
    def set_active_item(self, item):
        """Establecer el item activo"""
        if self.current_active_item:
            self.current_active_item.set_active(False)
        
        if item:
            item.set_active(True)
            self.current_active_item = item
            
    def set_playhead_position(self, x):
        """Establecer la posición del playhead"""
        x = max(0, min(x, self.timeline_width))
        self.playhead.setPos(x, 0)
        self.auto_scroll_to_playhead(x)
            
    def actualize_data(self, seconds, frame):
        """Establecer la posición del playhead"""
        self.current_frame = frame
        self.current_time = seconds
        
    def get_playhead_time(self):
        """Obtener el tiempo actual del playhead en segundos"""
        return self.playhead.x() / self.pixels_per_second
        
    def clear_timeline(self):
        """Limpiar todos los items del timeline"""
        for item in self.timeline_items:
            self.scene.removeItem(item)
        self.timeline_items.clear()
        self.next_available_x = 0
        self.current_active_item = None
        
    def remove_selected_items(self):
        """Eliminar items seleccionados del timeline"""
        items_to_remove = []
        for item in self.timeline_items:
            if item.isSelected():
                items_to_remove.append(item)
                self.scene.removeItem(item)
                
        for item in items_to_remove:
            self.timeline_items.remove(item)
            
        if items_to_remove:
            self.reorganize_timeline()
            self.timeline_changed.emit()
            
    def reorganize_timeline(self):
        """Reorganizar items en el timeline después de cambios"""
        if not self.timeline_items:
            self.next_available_x = 0
            return
            
        self.timeline_items.sort(key=lambda item: item.x())
        
        last_item = self.timeline_items[-1]
        item_width = (last_item.actual_duration_ms / 1000) * self.pixels_per_second
        self.next_available_x = last_item.x() + item_width + 0
        
    def add_event_clip(self, evento):
        """Añadir un clip de evento al timeline"""
        print(f"Adding event clip to timeline: {evento}")
        if not self.current_active_item:
            print("No active video item to attach event.")
            return
            
        event_item = self.current_active_item.create_event_clip(evento)
        if event_item:
            self.scene.addItem(event_item)
            self.timeline_changed.emit()
    
        
    def auto_scroll_to_playhead(self, x_position):
        """Auto-scroll mejorado con animación suave"""
        
        # Si el auto-scroll está deshabilitado, salir
        if not self.auto_scroll_config['enabled']:
            return
            
        # Obtener información del viewport
        viewport_rect = self.viewport().rect()
        scene_rect = self.mapToScene(viewport_rect).boundingRect()
        
        visible_left = scene_rect.left()
        visible_right = scene_rect.right()
        visible_center = (visible_left + visible_right) / 2
        visible_width = visible_right - visible_left
        
        margin = self.auto_scroll_config['margin']
        
        # Determinar si necesitamos hacer scroll
        need_scroll = False
        target_scroll = self.horizontalScrollBar().value()
        
        # ========== ESTRATEGIAS DE AUTO-SCROLL ==========
        
        # Estrategia 1: Mantener en el tercio central
        if self._use_thirds_strategy():
            third_width = visible_width / 3
            left_third = visible_left + third_width
            right_third = visible_right - third_width
            
            if x_position < left_third or x_position > right_third:
                need_scroll = True
                # Centrar el playhead
                target_center = x_position
                
        # Estrategia 2: Scroll por páginas
        elif self._use_page_strategy():
            if x_position > visible_right - margin:
                need_scroll = True
                # Avanzar una "página"
                target_center = x_position + visible_width / 2
            elif x_position < visible_left + margin:
                need_scroll = True
                # Retroceder una "página"
                target_center = x_position - visible_width / 2
                
        # Estrategia 3: Seguimiento suave (default)
        else:
            # Zona de activación del scroll (márgenes)
            left_trigger = visible_left + margin
            right_trigger = visible_right - margin
            
            if x_position > right_trigger:
                need_scroll = True
                # Calcular cuánto scroll necesitamos
                overflow = x_position - right_trigger
                target_center = visible_center + overflow + margin / 2
                
            elif x_position < left_trigger:
                need_scroll = True
                # Calcular cuánto scroll necesitamos
                underflow = left_trigger - x_position
                target_center = visible_center - underflow - margin / 2
        
        # Ejecutar scroll si es necesario
        if need_scroll:
            if self.auto_scroll_config['smooth']:
                self._smooth_scroll_to(target_center)
            else:
                self.centerOn(target_center, self.timeline_height / 2)
    
    def _smooth_scroll_to(self, x_center):
        """Realizar scroll suave animado a una posición"""
        # Calcular el valor del scrollbar necesario
        viewport_width = self.viewport().width()
        target_scroll = int(x_center - viewport_width / 2)
        
        # Limitar al rango válido
        max_scroll = self.horizontalScrollBar().maximum()
        target_scroll = max(0, min(target_scroll, max_scroll))
        
        # Animar el scroll
        self.scroll_animation.stop()
        self.scroll_animation.setStartValue(self.horizontalScrollBar().value())
        self.scroll_animation.setEndValue(target_scroll)
        self.scroll_animation.start()
    
    def _use_thirds_strategy(self):
        """Determinar si usar estrategia de tercios"""
        # Usar durante reproducción para mantener vista adelante
        return hasattr(self, 'is_playing') and self.is_playing
    
    def _use_page_strategy(self):
        """Determinar si usar estrategia de páginas"""
        # Usar cuando se navega manualmente con teclas
        return hasattr(self, 'keyboard_navigation') and self.keyboard_navigation
    
    
    def add_event_selection(self, start_time_ms, end_time_ms):
        """Añadir un evento de selección al timeline"""
        if not self.current_active_item:
            print("No active video item to attach selection event.")
            return
        event  =self.current_active_item
        event_item = self.current_active_item.update_selection_rect(start_time_ms, end_time_ms)
        if event_item:
            self.scene.addItem(event_item)
            self.timeline_changed.emit()