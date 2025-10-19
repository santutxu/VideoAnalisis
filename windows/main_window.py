from components.video_player import VideoPlayerWidget
from components.controls_bar import ControlsBar
from components.video_controller_bar import VideoControlBar 
from components.timeline import Timeline
from components.event_panel import EventPanel
from components.eventWidget import EventWidget
from components.actionsWidget import ActionsWidget
from items.video_item import VideoItem
from core.project_manager import ProjectManager
from utils import time_to_position, position_to_time, format_time, format_time_long
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMenuBar, QMenu, QAction, QToolBar, QPushButton, QLabel, QSlider,
    QStatusBar, QDockWidget, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QSettings, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence, QIcon



class MainWindow(QMainWindow):
    """
    Ventana principal que integra todos los componentes de la aplicación.
    """
    
    def __init__(self):
        super().__init__()
        
        # Gestores principales
        self.project_manager = ProjectManager()
        #self.event_manager = EventManager()
        
        # Estado de la aplicación
        self.current_video_path = None
        self.is_playing = False
        self.current_position = 0.0
        self.current_second = 0
        self.current_frame =0
        # Configurar ventana
        self.setWindowTitle("Video Tactics Analyzer - Análisis Táctico Deportivo")
        self.setGeometry(100, 100, 1400, 900)
        
        # Cargar configuración guardada
        self.settings = QSettings()
        # Crear interfaz
        self._create_widgets()
        self._create_menus()
        #self._create_toolbars()
        self._create_statusbar()
        self._setup_layout()
        self._connect_signals()
        
        
    def _create_widgets(self):
        """Crea los widgets principales de la aplicación."""
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.video_player = VideoPlayerWidget()    
        #self.controls_bar = ControlsBar()
        self.controls_bar = VideoControlBar()
        
        ''' '''
        # Control de zoom
        self.timeline_label = QLabel("🎬 Timeline")
        self.timeline_label.setStyleSheet("QLabel { font-weight: bold; font-size: 14px; padding: 5px; }")
        self.zoom_label = QLabel("Zoom:")
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(0)
        self.zoom_slider.setMaximum(100)
        self.zoom_slider.setValue(30)
        self.zoom_slider.setMaximumWidth(200)
        
        self.zoom_value_label = QLabel("30%")
        self.zoom_value_label.setMinimumWidth(40)
        
        # Botones de zoom
        self.zoom_in_button = QPushButton("🔍+")
        self.zoom_out_button = QPushButton("🔍-")
        self.zoom_fit_button = QPushButton("🔍 Ajustar")
        self.zoom_in_button.setMaximumWidth(40)
        self.zoom_out_button.setMaximumWidth(40)
        self.zoom_fit_button.setMaximumWidth(80)
        
        # Botón de corte
        self.cut_button = QPushButton("✂ Cortar Video")
        self.cut_button.setCheckable(True)
        self.cut_button.setMaximumWidth(120)
        self.cut_button.setStyleSheet("""
            QPushButton:checked {
                background-color: #ff6b6b;
                color: white;
            }
        """)
        self.timeline = Timeline()
        self.event_panel = EventWidget()
        
        self.actiosns_panel= ActionsWidget(self.event_panel.event_manager.EVENT_TYPES)
        
        self.event_dock = QDockWidget("Panel de Eventos Tácticos", self)
        self.event_dock.setWidget(self.event_panel)
        #self.event_dock.setWidget(self.video_list)
        self.event_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.event_dock)
    
    def _create_menus(self):
        """Crea el menú de la aplicación."""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        # Nuevo proyecto
        new_action = QAction(QIcon("resources/icons/new.png"), "&Nuevo Proyecto", self)
        new_action.setShortcut(QKeySequence.New)
        #new_action.triggered.connect(self.import_videos)
        file_menu.addAction(new_action)
        
        # Abrir video
        open_action = QAction(QIcon("resources/icons/open.png"), "&Abrir Proyecto", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_project)
        file_menu.addAction(open_action)
        
        # Guardar proyecto
        save_action = QAction(QIcon("resources/icons/save.png"), "&Guardar Proyecto", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        #video
        video_menu = menubar.addMenu("&Video")
        
        # Abrir video
        import_action = QAction(QIcon("resources/icons/open.png"), "&Abrir Video", self)
        import_action.setShortcut(QKeySequence.Open)
        import_action.triggered.connect(self._open_video)
        video_menu.addAction(import_action)
        
        # Exportar
        export_menu = file_menu.addMenu("&Exportar")
        
        export_json = QAction("Exportar a JSON", self)
        #export_json.triggered.connect(lambda: self.export_data('json'))
        export_menu.addAction(export_json)
        
        export_csv = QAction("Exportar a CSV", self)
        export_csv.triggered.connect(lambda: self.export_data('csv'))
        export_menu.addAction(export_csv)
        
        export_pdf = QAction("Generar Reporte PDF", self)
        #export_pdf.triggered.connect(lambda: self.export_data('pdf'))
        export_menu.addAction(export_pdf)
        
        export_clips = QAction("Generar Clips de Video", self)
        #export_clips.triggered.connect(self.export_clips)
        #export_menu.addAction(export_clips)
        
        file_menu.addSeparator()
        
        # Salir
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Edición
        #edit_menu = menubar.addMenu("&Edición")
        
        # Cortar video
        cut_action = QAction(QIcon("resources/icons/cut.png"), "&Cortar Segmento", self)
        cut_action.setShortcut("Ctrl+X")
        #cut_action.triggered.connect(self.cut_segment)
        #edit_menu.addAction(cut_action)
        
        # Menú Vista
        view_menu = menubar.addMenu("&Vista")
        
        # Toggle panel de eventos
        view_menu.addAction(self.event_dock.toggleViewAction())
        
        # Menú Herramientas
        #tools_menu = menubar.addMenu("&Herramientas")
        
        # Configuración
        #settings_action = QAction("&Configuración", self)
        #settings_action.triggered.connect(self.show_settings)
        #tools_menu.addAction(settings_action)
   
   
    def _create_toolbars(self):
        """Crea las barras de herramientas."""
        
        # Toolbar principal
        main_toolbar = self.addToolBar("Principal")
        main_toolbar.setMovable(False)
        
        # Acciones de archivo
        main_toolbar.addAction(QIcon("resources/icons/open.png"), "Abrir Video", self._open_video)
        #main_toolbar.addAction(QIcon("resources/icons/save.png"), "Guardar", self.save_project)
        main_toolbar.addSeparator()
        
        # Controles de reproducción (se añaden desde controls_bar)
        main_toolbar.addWidget(self.controls_bar)
        main_toolbar.addSeparator()
        
        # Toolbar de eventos tácticos
        tactics_toolbar = self.addToolBar("Tácticas")
        tactics_toolbar.setMovable(False)
        
        # Eventos rápidos
     
 
    def _create_statusbar(self):
        """Crea la barra de estado."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Mostrar información del video
        self.status_label = ("Sin video cargado")
        #self.statusbar.addWidget(self.status_label)
        
        # Posición actual
        self.position_label = ("00:00:00 / 00:00:00")
        #self.statusbar.addPermanentWidget(self.position_label)
        
    def _setup_layout(self):
        """Configura el layout principal de la aplicación."""
        main_layout = QVBoxLayout()
        
        # Splitter para video y timeline
        splitter = QSplitter(Qt.Vertical)
        # Añadir video player
        splitter.addWidget(self.video_player)
        
        
        # Añadir timeline
        timeline_controls_layout = QHBoxLayout()
        timeline_controls_layout.addWidget(self.zoom_label)
        timeline_controls_layout.addWidget(self.zoom_slider)
        timeline_controls_layout.addWidget(self.zoom_value_label)
        timeline_controls_layout.addWidget(self.zoom_out_button)
        timeline_controls_layout.addWidget(self.zoom_in_button)
        timeline_controls_layout.addWidget(self.zoom_fit_button)
        timeline_controls_layout.addSpacing(20)
        timeline_controls_layout.addWidget(self.cut_button)
        timeline_controls_layout.addStretch()
        
        # Layout del timeline
        timeline_layout = QVBoxLayout()
        #timeline_layout.addWidget(self.timeline_label)
        timeline_layout.addLayout(timeline_controls_layout)
        timeline_layout.addWidget(self.timeline)
        #addLayouttimeline_layout.addWidget(self.actiosns_panel)
        
        timeline_widget = QWidget()
        timeline_widget.setLayout(timeline_layout)
        splitter.addWidget(timeline_widget)
        splitter.addWidget(self.actiosns_panel)
        splitter.setSizes([800, 100,100])
        
        
        main_layout.addWidget(splitter)
        
        self.central_widget.setLayout(main_layout)   
      
    def _connect_signals(self):
        """Conecta las señales entre widgets."""
        # video_player signals
        #self.video_player.position_changed  .connect(self.controls_bar.update_position)
        self.video_player.duration_changed .connect(self.set_duration)
        
        # Timeline signals
        self.timeline.video_selected.connect(self.play_from_timeline)
        self.timeline.timeline_changed.connect(self.on_timeline_changed)
        self.timeline.playhead_moved.connect(self.on_playhead_moved)
        self.video_player.position_changed.connect(self.update_timeline_playhead)
        
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.zoom_fit_button.clicked.connect(self.zoom_fit)
        self.cut_button.toggled.connect(self.on_cut_mode_toggled)
        
        # Event panel signals
        self.event_panel.event_selected.connect(self.jump_to_event)
        self.event_panel.event_added.connect(self.on_event_added)
        self.event_panel.event_deleted.connect(self.on_event_deleted)
        
        # actionsWidget signals
        self.actiosns_panel.event_added.connect(self.on_sction_event_added)
        self.video_player.speedChanged.connect(self.on_speedChanged)
    # Menu actions
    
    def isVideoLoaded(self):
        return self.current_video_path is not None
    
    # acciones de video_player
    def _open_video(self):
        """Abre un archivo de video."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir Video",
            "",
            "Videos (*.mp4 *.avi *.mov *.mkv *.flv);;Todos los archivos (*.*)"
        )
        
        if file_path:
            self.current_video_path = file_path
            self.video_player.load_video(file_path)
            item = VideoItem(file_path)
            self.timeline.add_video(file_path, item.duration)
            self.timeline.set_playhead_position(0)
            
    def set_duration(self, duration, total_frames,fps):
        """Establece la duración total del video."""
        self.controls_bar.set_video_info(total_frames,fps)
        
    
    # acciones de timeline
    def play_from_timeline(self, video_path):
        #self.video_player.load_video(video_path)
        #self.video_player.play()
        filename = os.path.basename(video_path)
        self.statusbar.showMessage(f"Reproduciendo: {filename}", 3000)
        
    def on_timeline_changed(self):
        item_count = len(self.timeline.timeline_items)
        if item_count > 0:
            self.statusbar.showMessage(f"Timeline: {item_count} clips", 2000)
            
    def on_playhead_moved(self, x):
        #print(f"Playhead moved to: {seconds:.2f}s")
        seconds = (x / self.timeline.pixels_per_second) 
        if not self.video_player.is_playing:
            self.video_player.set_position(seconds)
            self.timeline.set_playhead_position(x)
            self.controls_bar.update_time_labels2(seconds)
        
                
    def update_timeline_playhead(self, seconds, frame):
        self.current_second =seconds
        self.current_frame =frame
        x_position = seconds * self.timeline.pixels_per_second
        self.timeline.set_playhead_position(x_position)
        self.timeline.actualize_data(seconds, frame)
        
       # Métodos de funcionalidad
    def on_zoom_changed(self, value):
        self.zoom_value_label.setText(f"{value}%")
        self.timeline.set_zoom(value)
        
    def zoom_in(self):
        current = self.zoom_slider.value()
        self.zoom_slider.setValue(min(100, current + 10))
        
    def zoom_out(self):
        value = self.zoom_slider.value()
        current = self.zoom_slider.value()
        self.zoom_slider.setValue(max(0, current - 10))
        
    def zoom_fit(self):
        self.zoom_slider.setValue(30)
        
    def on_cut_mode_toggled(self, checked):
        self.timeline.enable_cut_mode(checked)
        if checked:
            self.statusbar.showMessage("Modo CORTE activado - Click en un video para dividirlo", 0)
        else:
            self.statusbar.showMessage("Modo corte desactivado", 2000)
    # acciones de event panel
     
    def jump_to_event(self, event):
        """Salta a la posición del evento seleccionado."""
        if event:
            start_time = event['event_start']
            end_time = event['event_end']
            self.video_player.set_position(start_time)
            self.statusbar.showMessage(f"Saltando a evento: {event['event_type']} en {event['event_start']:.2f}s", 3000)
            self.update_timeline_playhead(start_time)
            self.timeline.add_event_selection(start_time,end_time)
        
    def on_event_added(self, event):
        #print(f"Nuevo evento en {event.timestamp:.2f}s")
        self.timeline.add_event_clip(event)    
          
    def on_event_deleted(self, event):
        print(f"Nuevo evento en {event.timestamp:.2f}s")
        self.timeline.event_deleted(event)     
        
    # acciones actionsWidget
    def on_sction_event_added(self, event):
        position_end = self.current_second
        position_start = position_end - float(event['time'])
        print(f"Nueva accion evento en {event}")
        new_event = {
            'event_start': position_start,
            'event_end': position_end,
            'event_name': event['id'],
            'event_type': event['categoria'],
            'event_duration': event['time']
        }
        self.event_panel.add_event(new_event)
    
    def on_speedChanged(self, speed):
        print(f"Cambiando velocidad a: {speed}x")
        self.video_player.set_playback_speed(speed)
    
    def _save_project(self):
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, 
            "Save File", "", "All Files(*.vta);", options = options)
        video_path = self.current_video_path
        events = self.event_panel.get_all_events()
        print(f"Guardando proyecto con video: {video_path} y {len(events)} eventos")
        for event in events:
            print(f"Evento: {event}")
        project_data = self.project_manager.create_project_data(video_path, events,[],0,12000,30,15,1)
        self.project_manager.save_project(fileName,project_data)
        
        
    def _open_project(self):    
        
        """Abre un archivo de video."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir projecto",
            "",
            "Todos los archivos (*.vta)"
        )
        
        if file_path:
            print(f"Abriendo proyecto: {file_path}")
            project_data = self.project_manager.load_project(file_path)
            if project_data[0] == True:
                video =project_data[2].get('video', None)
                video_path = video.get('path', None)
                events = project_data[2].get('moments', [])
                self.import_project_data(video_path,events)
          
          
    def import_project_data(self, video_path, events):      
        if video_path:
            self.current_video_path = video_path
            self.video_player.load_video(video_path)
            item = VideoItem(video_path)
            self.timeline.add_video(video_path, item.duration)
            for event in events:
                self.event_panel.add_event(event, loaded=True)
                self.on_event_added(event)
        '''
    def zoom_label(self):
        print("zoom_label")
        
    def zoom_slider(self):
        print("zoom_slider")
        
    def zoom_value_label(self):
        print("zoom_value_label")
        
    def zoom_out_button(self):
        print("zoom_out_button")
    def zoom_in_button(self):
        print("zoom_in_button")
        
    def zoom_fit_button(self):
        print("zoom_fit_button")
        
    def cut_button(self):
        print("cut_button")
        
    def timeline_label(self):
        print("timeline_label")
    '''