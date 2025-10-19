from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
import uuid


@dataclass
class TacticalEvent:
    """Representa un evento táctico en el video."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = 0.0  # Segundos desde inicio del video
    event_name: str = ""  # Nombre del evento, e.g. "pass", "shot"
    event_type: str = ""    # "pass", "shot", "foul", etc.
    coordinates: Optional[Dict[str, float]] = None  # {"x": 0.5, "y": 0.3} normalizado
    match_minute: Optional[int] = None  # Minuto real del partido
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    event_duration: Optional[str] = None 
    event_start: float = 0.0
    event_end: float = 0.0
    
    
    def to_dict(self) -> Dict:
        """Convierte el evento a diccionario para serialización."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TacticalEvent':
        """Crea un evento desde un diccionario."""
        return cls(**data)
    
    
    
    def copy(self) -> 'TacticalEvent':
        """Crear una copia del evento."""
        return replace(self)
    
class EventManager:
    
    EVENT_TYPES = {        'pinicial': {'id':'pinicial','name':'P.Inicio','icon': '🟨', 'color': '#FFC107', 'categoria': 'Defensa','time':'10'},
        'acciond': {'id':'acciond','name':'Accion Def','icon': '📊', 'color': '#FFC107', 'categoria': 'Defensa','time':'10'},
        'desajuste':{'id':'desajuste','name':'Desajuste','icon': '❗', 'color': '#FFC107', 'categoria': 'Defensa','time':'10'},
        'contruccion': {'id':'contruccion','name':'Construccion','icon': '🔄', 'color': "#FF6A07", 'categoria': 'Ataque','time':'10'},
        'finalizacion': {'id':'finalizacion','name':'Finalizacion','icon': '🎯', 'color': '#FF6A07', 'categoria': 'Ataque','time':'5'},
        'perdida': {'id':'perdida','name':'Perdida','icon': '🎯', 'color': '#FF6A07', 'categoria': 'Ataque','time':'5'},
        'repliegue': {'id':'repliegue','name':'Repliegue','icon': '↩️', 'color': '#2196F3', 'categoria': 'transicion','time':'5'},
        'contra':   {'id':'contra','name':'Contraataque','icon': '⚡', 'color': '#2196F3', 'categoria': 'transicion','time':'5'},
        'p_lan':   {'id':'p_lanzado','name':'P.L','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'p_rec':   {'id':'p_rec','name':'P.R.','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'fd_lan':   {'id':'fd_lan','name':'F.D.L','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'fd_rec':   {'id':'fd_rec','name':'F.D.R','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'fa_lan':   {'id':'fa_lan','name':'Falta.L','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'fa_rec':   {'id':'fa_rec','name':'Falta.R','icon': '⚡', 'color': '#006A07', 'categoria': 'bolapareda','time':'5'},
        'gol':   {'id':'gol','name':'GOL','icon': '⚡', 'color': "#E620E6", 'categoria': 'gol','time':'5'},
        'gol_rec':   {'id':'gol_rec','name':'GOL R','icon': '⚡', 'color': '#E620E6', 'categoria': 'gol','time':'5'},
    }
        
    def __init__(self, video_duration: float = 0.0):
        """
        Inicializa el gestor de eventos.
        
        Args:
            video_duration: Duración total del video en segundos
        """
        self.events: List[TacticalEvent] = []
        self.video_duration = video_duration
        #self.event_types = EVENT_TYPES.copy()
        
    def add_event(self, 
                  timestamp: float,
                  event_name: str,
                  event_type: str,
                  coordinates: Optional[Dict[str, float]] = None,
                  match_minute: Optional[int] = None,
                  event_duration: Optional[str] = None,
                  event_start: Optional[float] = 0.0,
                  event_end: Optional[float] = 0.0,
                  tags: Optional[List[str]] = None) -> TacticalEvent:
        """
        Añade un nuevo evento táctico.
        
        Returns:
            El evento creado
        """
        if event_type not in self.EVENT_TYPES:
            # Si el tipo no existe, añadirlo como personalizado
            self.EVENT_TYPES[event_type] = {
                'icon': '📌',
                'color': '#9E9E9E',
                'category': 'custom'
            }
            
        event = TacticalEvent(
            timestamp=timestamp,
            event_type=event_type,
            event_name=event_name,
            #player_name=player_name,
            #team=team,
            #zone_id=zone_id,
            #zone_name=zone_name,
            coordinates=coordinates,
            #notes=notes,
            match_minute=match_minute,
            tags=tags or [],
            event_start= match_minute,
            event_end=timestamp,
            event_duration= event_duration
        )
        
        self.events.append(event)
        self.events.sort(key=lambda e: e.timestamp)  # Mantener orden cronológico
        
        return event
    
    
    def get_event_def(self, event_type):
        """Obtiene un evento por su tipo."""
        for event in self.EVENT_TYPES:
            if event == event_type:
                evv = self.EVENT_TYPES[event]
                print(evv)
                return evv
        return None
    
    def get_events(self) -> List[TacticalEvent]:
        """Devuelve todos los eventos."""
        return self.events
    
    def delete_event_from_list(self,item):
        for event in self.events:
            getattr(event, key, None) == value 
        self.events.remove(event) 
        
    # MÉTODO 3: Eliminar por ID específico
    def remove_by_id(self, event_id: str) -> bool:
        """
        Elimina un evento por su ID único.
        """
        for i, event in enumerate(self.events):
            if event.id == event_id:
                removed_event = self.events.pop(i)
                print(f"Evento eliminado por ID: {removed_event.id}")
                return True
        return False