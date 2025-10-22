from typing import List, Optional, Callable
from datetime import datetime

from .tactical_event import TacticalEvent


class TacticalEventManager:
    """Gestor principal para manejar eventos tácticos."""
    
    def __init__(self):
        self.events: List[TacticalEvent] = []
        self.history: List[dict] = []  # Para deshacer/rehacer
        self.history_index = -1
        self.max_history = 50
        
        # Callbacks para notificar cambios
        self.on_event_added: Optional[Callable] = None
        self.on_event_removed: Optional[Callable] = None
        self.on_event_updated: Optional[Callable] = None
        
    # ============= FUNCIONES DE ELIMINACIÓN =============
    
    def remove_event(self, event: TacticalEvent) -> bool:
        """
        Elimina un evento específico de la lista.
        
        Args:
            event: El evento a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no se encontró
        """
        try:
            # Guardar estado para deshacer
            self._save_history()
            
            # Buscar y eliminar por ID (más seguro)
            for i, e in enumerate(self.events):
                if e.id == event.id:
                    removed_event = self.events.pop(i)
                    
                    # Notificar cambio
                    if self.on_event_removed:
                        self.on_event_removed(removed_event)
                    
                    return True
            return False
            
        except Exception as e:
            print(f"Error al eliminar evento: {e}")
            return False
    
    def remove_event_by_id(self, event_id: str) -> Optional[TacticalEvent]:
        """
        Elimina un evento por su ID único.
        
        Args:
            event_id: ID del evento a eliminar
            
        Returns:
            El evento eliminado o None si no se encontró
        """
        self._save_history()
        
        for i, event in enumerate(self.events):
            if event.id == event_id:
                removed = self.events.pop(i)
                
                if self.on_event_removed:
                    self.on_event_removed(removed)
                    
                return removed
        return None
    
    def remove_events_by_criteria(self, **criteria) -> List[TacticalEvent]:
        """
        Elimina eventos que coincidan con los criterios especificados.
        
        Args:
            **criteria: Criterios de búsqueda (event_name="pase", event_type="Ataque", etc.)
            
        Returns:
            Lista de eventos eliminados
        """
        self._save_history()
        
        removed_events = []
        new_events = []
        
        for event in self.events:
            if self._matches_criteria(event, criteria):
                removed_events.append(event)
            else:
                new_events.append(event)
        
        self.events = new_events
        
        # Notificar cambios
        for event in removed_events:
            if self.on_event_removed:
                self.on_event_removed(event)
        
        return removed_events
    
    def remove_events_in_range(self, start_time: float, end_time: float) -> List[TacticalEvent]:
        """
        Elimina todos los eventos dentro de un rango de tiempo.
        """
        self._save_history()
        
        removed = []
        new_events = []
        
        for event in self.events:
            if start_time <= event.event_start <= end_time:
                removed.append(event)
                if self.on_event_removed:
                    self.on_event_removed(event)
            else:
                new_events.append(event)
        
        self.events = new_events
        return removed
    
    # ============= FUNCIONES DE EDICIÓN =============
    
    def update_event(self, event_id: str, **updates) -> bool:
        """
        Actualiza un evento existente con nuevos valores.
        
        Args:
            event_id: ID del evento a actualizar
            **updates: Campos a actualizar y sus nuevos valores
            
        Returns:
            True si se actualizó correctamente, False si no se encontró
        """
        self._save_history()
        
        for event in self.events:
            if event.id == event_id:
                # Guardar estado anterior para comparación
                old_event = event.copy()
                
                # Actualizar campos
                for key, value in updates.items():
                    if hasattr(event, key):
                        setattr(event, key, value)
                
                # Actualizar timestamp de modificación
                event.created_at = datetime.now().isoformat()
                
                # Notificar cambio
                if self.on_event_updated:
                    self.on_event_updated(old_event, event)
                
                return True
        return False
    
    def replace_event(self, event_id: str, new_event: TacticalEvent) -> bool:
        """
        Reemplaza completamente un evento con otro.
        
        Args:
            event_id: ID del evento a reemplazar
            new_event: Nuevo evento que reemplazará al anterior
        """
        self.print_events()
        self._save_history()
        
        for i, event in enumerate(self.events):
            if event.id == event_id:
                old_event = self.events[i]
                new_event.id = event_id  # Mantener el mismo ID
                self.events[i] = new_event
                
                if self.on_event_updated:
                    self.on_event_updated(old_event, new_event)
                
                return True
        return False
    
    def batch_update(self, event_ids: List[str], **updates) -> int:
        """
        Actualiza múltiples eventos a la vez.
        
        Returns:
            Número de eventos actualizados
        """
        self._save_history()
        
        updated_count = 0
        for event_id in event_ids:
            if self.update_event(event_id, **updates):
                updated_count += 1
        
        return updated_count
    
    # ============= FUNCIONES AUXILIARES =============
    
    def _matches_criteria(self, event: TacticalEvent, criteria: dict) -> bool:
        """Verifica si un evento coincide con los criterios dados."""
        for key, value in criteria.items():
            if not hasattr(event, key):
                return False
            
            event_value = getattr(event, key)
            
            # Manejo especial para floats
            if isinstance(value, float) and isinstance(event_value, float):
                if abs(event_value - value) > 0.0001:
                    return False
            elif event_value != value:
                return False
        
        return True
    
    def _save_history(self):
        """Guarda el estado actual para poder deshacer."""
        # Serializar estado actual
        current_state = [event.to_dict() for event in self.events]
        
        # Eliminar estados futuros si estamos en medio del historial
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # Agregar nuevo estado
        self.history.append(current_state)
        self.history_index += 1
        
        # Limitar tamaño del historial
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1
    
    def undo(self) -> bool:
        """Deshacer última operación."""
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.events = [TacticalEvent.from_dict(d) for d in state]
            return True
        return False
    
    def redo(self) -> bool:
        """Rehacer operación deshecha."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            state = self.history[self.history_index]
            self.events = [TacticalEvent.from_dict(d) for d in state]
            return True
        return False
    
    def find_event(self, event_id: str) -> Optional[TacticalEvent]:
        """Busca un evento por ID."""
        for event in self.events:
            if event.id == event_id:
                return event
        return None
    
    def add_event(self, event: TacticalEvent):
        """Agrega un nuevo evento."""
        self._save_history()
        self.events.append(event)
        self.print_events()
        if self.on_event_added:
            self.on_event_added(event)
            
    def print_events(self):
        """Imprime todos los eventos para depuración."""
        for item in self.events:
            #event = 
            print(item.to_dict())
   
 