from datetime import timedelta
import datetime

def addSecs(tm, secs):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate.time()

def format_time(milliseconds):
    """Formatear tiempo de milisegundos a MM:SS"""
    seconds = milliseconds / 1000
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def format_time2(milliseconds):
    """Formatear tiempo de milisegundos a MM:SS"""
    seconds = milliseconds / 1000
    minutes = int(seconds // 60)
    hours = int(minutes // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_time_long(milliseconds):
    """Formatear tiempo de milisegundos a HH:MM:SS"""
    seconds = milliseconds / 1000
    return str(timedelta(seconds=int(seconds)))


def position_to_time(self, x_position):
    """Convertir posición X local a tiempo en milisegundos"""
    # Proporción de la posición en el ancho total
    ratio = x_position / self.rect().width() if self.rect().width() > 0 else 0
    
    # Calcular tiempo relativo al clip
    relative_time = ratio * self.actual_duration_ms
    
    # Añadir el offset del trim inicial
    absolute_time = self.start_trim + relative_time
    
    return absolute_time
    
def time_to_position(self, time_ms):
    """Convertir tiempo en milisegundos a posición X local"""
    # Tiempo relativo al clip
    relative_time = time_ms - self.start_trim
    
    # Proporción del tiempo en la duración total
    ratio = relative_time / self.actual_duration_ms if self.actual_duration_ms > 0 else 0
    
    # Calcular posición X
    x_position = ratio * self.rect().width()
    
