from typing import Dict, Optional
from dataclasses import dataclass, asdict, field,replace
from datetime import datetime
import uuid
@dataclass
class TacticalEvent:
    """Representa un evento táctico en el video."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = 0.0  # Segundos desde inicio del video
    event_name: str = ""  # Nombre del evento, e.g. "pass", "shot"
    event_type: str = ""    # "pass", "shot", "foul", etc.
    #coordinates: Optional[Dict[str, float]] = None  # {"x": 0.5, "y": 0.3} normalizado
    #match_minute: Optional[int] = None  # Minuto real del partido
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    #tags: List[str] = field(default_factory=list)
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