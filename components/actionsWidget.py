from PyQt5.QtWidgets import  QWidget, QVBoxLayout, QHBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QSlider, QLabel, QComboBox, QStyle
from PyQt5.QtCore import Qt, pyqtSignal

class ActionsWidget(QWidget):
    event_added = pyqtSignal(dict)  
    
    def __init__(self,event_definitions):
        super().__init__()
        self.event_definitions = event_definitions
        #self.event_manager = event_panel.event_manager
        self.eventos_1 = [
            {"texto":"Repliegue","id":"repliegue","color":"#FF5733","tiempo":"5"},
            {"texto":"detras de Porteria","id":"dporteriae","color":"#33FF57","tiempo":"7"},  
            {"texto":"4x3","id":"4x3","color":"#3357FF","tiempo":"10"}
        ]
        self.eventos_2= [
            {"texto":"Repliegue","id":"repliegue","color":"#FF5733","tiempo":"5"},
            {"texto":"detras de Porteria","id":"dporteriae","color":"#33FF57","tiempo":"7"},  
            {"texto":"4x3","id":"4x3","color":"#3357FF","tiempo":"10"}
        ]
        
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de controles."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        fo_group = QWidget()
        tr_group = QWidget()
        bp_group = QWidget()
        
        fo_layout = QVBoxLayout()
        fd_group = QGroupBox("Fase Defensiva")
        fd_layout = QVBoxLayout()
        tr_layout = QVBoxLayout()
        bp_layout = QVBoxLayout()
        di_group = QGroupBox("Disciplina")
        di_layout = QVBoxLayout()
        
        colums = []
        
        FaseOfensiva = QHBoxLayout()
        FaseDefensiva = QHBoxLayout()
        Transiciones = QHBoxLayout()
        AccionesBolaParada = QHBoxLayout()
        discipline = QHBoxLayout()
        
        for event in self.event_definitions:
            evento = self.event_definitions[event]
            print(evento)
            btn = QPushButton(event)
            btn.setGeometry(10, 10, 40, 30)
            btn.setStyleSheet(f"background-color: {evento['color']}; color: black; border-radius: 5px; padding: 5px; width: 8px; height: 30px;")
            btn.clicked.connect(lambda _, v=evento: self.handle_event(v))
            
            category_name = evento['categoria']
            if category_name == "Defensa" or category_name == "Ataque":
                FaseOfensiva.addWidget(btn) 
            #if category_name == "Ataque":
                #FaseDefensiva.addWidget(btn) 
            if category_name == "transicion" or category_name == "gol":
                Transiciones.addWidget(btn) 
            if category_name == "bolapareda":
                AccionesBolaParada.addWidget(btn) 
            #if category_name == "gol":
            #    discipline.addWidget(btn) 
                
            #colums[category]  = colomn
        fo_group.setLayout(FaseOfensiva)
        #fd_group.setLayout(FaseDefensiva)
        tr_group.setLayout(Transiciones)
        bp_group.setLayout(AccionesBolaParada)
        #di_group.setLayout(discipline)
        
        layout.addWidget(fo_group)
        layout.addWidget(tr_group)
        layout.addWidget(bp_group)
        #layout.addWidget(bp_group)
        #layout.addWidget(di_group)
        self.setLayout(layout)
        
    
    def handle_event(self, event_type):
        #print(f"Evento id seleccionado: {event_type}")
        #evento = self.get_event(event_type)
        print(f"Evento seleccionado: {event_type}")
        self.event_added.emit(event_type)
        # Añadir evento
       
        #self.main_window.quick_event(event_type)
        
      
    def get_event(self, event_id):        
        # Aquí puedes agregar la lógica para manejar el evento seleccionado
        for evento in self.eventos_1:
            if evento['id'] == event_id:
                return evento
        return None 
