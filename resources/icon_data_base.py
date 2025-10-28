
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class IconData:
    """Datos de un icono"""
    emoji: str
    name: str
    category: str
    keywords: List[str]
    
    
    
class IconDatabase:
    """Base de datos de iconos organizados por categorías"""
    
    @staticmethod
    def get_icons() -> Dict[str, List[IconData]]:
        return {
            "⚽ Deportes": [
                IconData("⚽", "Fútbol", "Deportes", ["balón", "soccer", "gol"]),
                IconData("🏀", "Baloncesto", "Deportes", ["basket", "canasta"]),
                IconData("🏈", "Fútbol Americano", "Deportes", ["rugby", "nfl"]),
                IconData("⚾", "Béisbol", "Deportes", ["baseball", "bate"]),
                IconData("🎾", "Tenis", "Deportes", ["raqueta", "pelota"]),
                IconData("🏐", "Voleibol", "Deportes", ["voley", "red"]),
                IconData("🏉", "Rugby", "Deportes", ["oval", "rugby"]),
                IconData("🎱", "Billar", "Deportes", ["pool", "bola"]),
                IconData("🏓", "Ping Pong", "Deportes", ["tenis mesa", "paddle"]),
                IconData("🏸", "Bádminton", "Deportes", ["raqueta", "volante"]),
                IconData("🏒", "Hockey", "Deportes", ["puck", "hielo"]),
                IconData("🏑", "Hockey Campo", "Deportes", ["stick", "césped"]),
                IconData("🥍", "Lacrosse", "Deportes", ["red", "palo"]),
                IconData("🏏", "Cricket", "Deportes", ["bate", "wicket"]),
                IconData("⛳", "Golf", "Deportes", ["hoyo", "bandera"]),
                IconData("🏹", "Tiro con Arco", "Deportes", ["flecha", "diana"]),
                IconData("🎿", "Esquí", "Deportes", ["nieve", "montaña"]),
                IconData("🏂", "Snowboard", "Deportes", ["nieve", "tabla"]),
                IconData("🤿", "Buceo", "Deportes", ["snorkel", "agua"]),
                IconData("🥊", "Boxeo", "Deportes", ["guante", "ring"]),
                IconData("🥋", "Artes Marciales", "Deportes", ["karate", "judo"]),
                IconData("🤸", "Gimnasia", "Deportes", ["acrobacia", "voltereta"]),
                IconData("🤽", "Waterpolo", "Deportes", ["agua", "piscina"]),
                IconData("🤾", "Handball", "Deportes", ["balonmano", "mano"]),
                IconData("⛸️", "Patinaje", "Deportes", ["hielo", "patín"]),
            ],
            
            "🎯 Acciones": [
                IconData("🎯", "Objetivo", "Acciones", ["diana", "meta", "target"]),
                IconData("▶️", "Play", "Acciones", ["reproducir", "inicio"]),
                IconData("⏸️", "Pausa", "Acciones", ["pausar", "detener"]),
                IconData("⏹️", "Stop", "Acciones", ["parar", "fin"]),
                IconData("⏪", "Retroceder", "Acciones", ["atrás", "rebobinar"]),
                IconData("⏩", "Avanzar", "Acciones", ["adelante", "forward"]),
                IconData("⏮️", "Anterior", "Acciones", ["previo", "back"]),
                IconData("⏭️", "Siguiente", "Acciones", ["next", "próximo"]),
                IconData("🔄", "Repetir", "Acciones", ["loop", "ciclo"]),
                IconData("🔀", "Aleatorio", "Acciones", ["random", "mezclar"]),
                IconData("➡️", "Derecha", "Acciones", ["right", "siguiente"]),
                IconData("⬅️", "Izquierda", "Acciones", ["left", "anterior"]),
                IconData("⬆️", "Arriba", "Acciones", ["up", "subir"]),
                IconData("⬇️", "Abajo", "Acciones", ["down", "bajar"]),
                IconData("↩️", "Volver", "Acciones", ["return", "regresar"]),
                IconData("↪️", "Adelante", "Acciones", ["forward", "avanzar"]),
                IconData("⤴️", "Subir", "Acciones", ["ascender", "elevar"]),
                IconData("⤵️", "Bajar", "Acciones", ["descender", "caer"]),
                IconData("🔁", "Bucle", "Acciones", ["repetir", "ciclo"]),
                IconData("🔂", "Repetir Uno", "Acciones", ["single", "uno"]),
            ],
            
            "⚠️ Alertas": [
                IconData("⚠️", "Advertencia", "Alertas", ["warning", "precaución"]),
                IconData("⛔", "Prohibido", "Alertas", ["stop", "no"]),
                IconData("🚫", "No Permitido", "Alertas", ["forbidden", "prohibir"]),
                IconData("❌", "Error", "Alertas", ["mal", "incorrecto"]),
                IconData("❗", "Importante", "Alertas", ["exclamación", "atención"]),
                IconData("❓", "Pregunta", "Alertas", ["duda", "question"]),
                IconData("💢", "Colisión", "Alertas", ["impacto", "choque"]),
                IconData("⚡", "Rápido", "Alertas", ["velocidad", "lightning"]),
                IconData("🔥", "Fuego", "Alertas", ["caliente", "hot"]),
                IconData("💥", "Explosión", "Alertas", ["boom", "impacto"]),
                IconData("🚨", "Sirena", "Alertas", ["alarma", "emergencia"]),
                IconData("📢", "Anuncio", "Alertas", ["megáfono", "noticia"]),
                IconData("🔔", "Campana", "Alertas", ["notificación", "aviso"]),
                IconData("📍", "Marcador", "Alertas", ["ubicación", "pin"]),
                IconData("🚩", "Bandera", "Alertas", ["flag", "señal"]),
                IconData("⭕", "Círculo Rojo", "Alertas", ["marca", "destacar"]),
                IconData("🔴", "Rojo", "Alertas", ["red", "punto"]),
                IconData("🟡", "Amarillo", "Alertas", ["yellow", "precaución"]),
                IconData("🟢", "Verde", "Alertas", ["green", "ok"]),
            ],
            
            "✅ Estados": [
                IconData("✅", "Correcto", "Estados", ["check", "bien"]),
                IconData("✔️", "Check", "Estados", ["marca", "ok"]),
                IconData("❎", "Casilla Marcada", "Estados", ["checkbox", "selección"]),
                IconData("☑️", "Verificado", "Estados", ["checked", "confirmado"]),
                IconData("✳️", "Nuevo", "Estados", ["new", "estrella"]),
                IconData("💚", "Positivo", "Estados", ["bueno", "favorable"]),
                IconData("💔", "Roto", "Estados", ["break", "fallo"]),
                IconData("💯", "Perfecto", "Estados", ["100", "excelente"]),
                IconData("🎖️", "Medalla", "Estados", ["premio", "logro"]),
                IconData("🏆", "Trofeo", "Estados", ["victoria", "ganador"]),
                IconData("🥇", "Oro", "Estados", ["primero", "gold"]),
                IconData("🥈", "Plata", "Estados", ["segundo", "silver"]),
                IconData("🥉", "Bronce", "Estados", ["tercero", "bronze"]),
                IconData("🏅", "Medalla", "Estados", ["premio", "reconocimiento"]),
                IconData("🎗️", "Cinta", "Estados", ["ribbon", "causa"]),
                IconData("🏵️", "Roseta", "Estados", ["decoración", "honor"]),
            ],
            
            "📊 Análisis": [
                IconData("📊", "Gráfico Barras", "Análisis", ["estadística", "chart"]),
                IconData("📈", "Gráfico Subida", "Análisis", ["crecimiento", "up"]),
                IconData("📉", "Gráfico Bajada", "Análisis", ["caída", "down"]),
                IconData("📐", "Regla", "Análisis", ["medida", "ángulo"]),
                IconData("📏", "Regla Recta", "Análisis", ["medir", "distancia"]),
                IconData("🔬", "Microscopio", "Análisis", ["investigación", "detalle"]),
                IconData("🔭", "Telescopio", "Análisis", ["observar", "lejos"]),
                IconData("🎬", "Claqueta", "Análisis", ["video", "acción"]),
                IconData("🎥", "Cámara", "Análisis", ["grabar", "filmar"]),
                IconData("📹", "Videocámara", "Análisis", ["recording", "video"]),
                IconData("📷", "Cámara Foto", "Análisis", ["captura", "foto"]),
                IconData("🔍", "Lupa", "Análisis", ["buscar", "zoom"]),
                IconData("🔎", "Lupa Derecha", "Análisis", ["búsqueda", "investigar"]),
                IconData("🗂️", "Archivos", "Análisis", ["organizar", "carpetas"]),
                IconData("📁", "Carpeta", "Análisis", ["folder", "directorio"]),
                IconData("📂", "Carpeta Abierta", "Análisis", ["open", "archivos"]),
                IconData("📝", "Nota", "Análisis", ["escribir", "memo"]),
                IconData("📋", "Portapapeles", "Análisis", ["clipboard", "lista"]),
                IconData("📌", "Chincheta", "Análisis", ["pin", "fijar"]),
                IconData("📎", "Clip", "Análisis", ["adjuntar", "unir"]),
            ],
            
            "👥 Personas": [
                IconData("👤", "Persona", "Personas", ["usuario", "jugador"]),
                IconData("👥", "Personas", "Personas", ["grupo", "equipo"]),
                IconData("🏃", "Corredor", "Personas", ["correr", "atletismo"]),
                IconData("🚶", "Caminando", "Personas", ["caminar", "andar"]),
                IconData("🧍", "De Pie", "Personas", ["parado", "standing"]),
                IconData("💪", "Músculo", "Personas", ["fuerza", "poder"]),
                IconData("🦵", "Pierna", "Personas", ["patada", "leg"]),
                IconData("🦶", "Pie", "Personas", ["foot", "pisada"]),
                IconData("👏", "Aplausos", "Personas", ["celebrar", "clap"]),
                IconData("🙌", "Manos Arriba", "Personas", ["celebración", "victoria"]),
                IconData("🤝", "Apretón Manos", "Personas", ["acuerdo", "saludo"]),
                IconData("👍", "Pulgar Arriba", "Personas", ["bien", "like"]),
                IconData("👎", "Pulgar Abajo", "Personas", ["mal", "dislike"]),
                IconData("✊", "Puño", "Personas", ["fuerza", "lucha"]),
                IconData("🤚", "Mano Levantada", "Personas", ["stop", "parar"]),
                IconData("✋", "Mano", "Personas", ["alto", "cinco"]),
            ],
            
            "🎮 Controles": [
                IconData("🎮", "Control", "Controles", ["gamepad", "juego"]),
                IconData("🕹️", "Joystick", "Controles", ["control", "arcade"]),
                IconData("⚙️", "Engranaje", "Controles", ["configuración", "settings"]),
                IconData("🔧", "Llave", "Controles", ["herramienta", "ajuste"]),
                IconData("🔨", "Martillo", "Controles", ["construir", "arreglar"]),
                IconData("⚒️", "Martillo y Pico", "Controles", ["trabajo", "minería"]),
                IconData("🛠️", "Herramientas", "Controles", ["tools", "reparar"]),
                IconData("🔩", "Tornillo", "Controles", ["ajustar", "fijar"]),
                IconData("⚖️", "Balanza", "Controles", ["equilibrio", "justicia"]),
                IconData("🔗", "Cadena", "Controles", ["link", "enlace"]),
                IconData("⛓️", "Cadenas", "Controles", ["unir", "conectar"]),
                IconData("🧲", "Imán", "Controles", ["atraer", "magnetismo"]),
                IconData("🔓", "Abierto", "Controles", ["unlock", "abrir"]),
                IconData("🔒", "Cerrado", "Controles", ["lock", "seguro"]),
                IconData("🔑", "Llave", "Controles", ["key", "acceso"]),
            ],
            
            "🌟 Símbolos": [
                IconData("⭐", "Estrella", "Símbolos", ["star", "favorito"]),
                IconData("🌟", "Estrella Brillante", "Símbolos", ["destacado", "especial"]),
                IconData("✨", "Destellos", "Símbolos", ["magia", "brillo"]),
                IconData("💫", "Estrella Fugaz", "Símbolos", ["rápido", "cometa"]),
                IconData("☀️", "Sol", "Símbolos", ["día", "luz"]),
                IconData("🌙", "Luna", "Símbolos", ["noche", "oscuro"]),
                IconData("💡", "Bombilla", "Símbolos", ["idea", "luz"]),
                IconData("🔦", "Linterna", "Símbolos", ["luz", "iluminar"]),
                IconData("🕐", "Reloj", "Símbolos", ["tiempo", "hora"]),
                IconData("⏰", "Alarma", "Símbolos", ["despertar", "tiempo"]),
                IconData("⏱️", "Cronómetro", "Símbolos", ["timer", "contar"]),
                IconData("⏲️", "Timer", "Símbolos", ["cuenta", "tiempo"]),
                IconData("🎰", "Máquina", "Símbolos", ["casino", "suerte"]),
                IconData("🎲", "Dado", "Símbolos", ["azar", "juego"]),
                IconData("🧭", "Brújula", "Símbolos", ["dirección", "navegación"]),
                IconData("🗺️", "Mapa", "Símbolos", ["ubicación", "geografía"]),
                IconData("🧩", "Puzzle", "Símbolos", ["rompecabezas", "pieza"]),
                IconData("♟️", "Peón", "Símbolos", ["ajedrez", "estrategia"]),
            ],
            
            "🔢 Números": [
                IconData("0️⃣", "Cero", "Números", ["0", "zero"]),
                IconData("1️⃣", "Uno", "Números", ["1", "primero"]),
                IconData("2️⃣", "Dos", "Números", ["2", "segundo"]),
                IconData("3️⃣", "Tres", "Números", ["3", "tercero"]),
                IconData("4️⃣", "Cuatro", "Números", ["4", "cuarto"]),
                IconData("5️⃣", "Cinco", "Números", ["5", "quinto"]),
                IconData("6️⃣", "Seis", "Números", ["6", "sexto"]),
                IconData("7️⃣", "Siete", "Números", ["7", "séptimo"]),
                IconData("8️⃣", "Ocho", "Números", ["8", "octavo"]),
                IconData("9️⃣", "Nueve", "Números", ["9", "noveno"]),
                IconData("🔟", "Diez", "Números", ["10", "décimo"]),
                IconData("#️⃣", "Numeral", "Números", ["hashtag", "número"]),
                IconData("💰", "Dinero", "Números", ["money", "bolsa"]),
                IconData("💵", "Dólar", "Números", ["billete", "cash"]),
                IconData("💴", "Yen", "Números", ["japón", "moneda"]),
                IconData("💶", "Euro", "Números", ["europa", "moneda"]),
                IconData("💷", "Libra", "Números", ["uk", "moneda"]),
            ],
            
            "🏥 Médico": [
                IconData("🏥", "Hospital", "Médico", ["clínica", "salud"]),
                IconData("🚑", "Ambulancia", "Médico", ["emergencia", "urgencia"]),
                IconData("💊", "Píldora", "Médico", ["medicina", "medicamento"]),
                IconData("💉", "Jeringa", "Médico", ["inyección", "vacuna"]),
                IconData("🩹", "Vendaje", "Médico", ["curita", "herida"]),
                IconData("🩺", "Estetoscopio", "Médico", ["doctor", "médico"]),
                IconData("🌡️", "Termómetro", "Médico", ["temperatura", "fiebre"]),
                IconData("🧬", "ADN", "Médico", ["genética", "ciencia"]),
                IconData("🦴", "Hueso", "Médico", ["esqueleto", "fractura"]),
                IconData("🫀", "Corazón", "Médico", ["órgano", "cardio"]),
                IconData("🫁", "Pulmones", "Médico", ["respiración", "órgano"]),
                IconData("🧠", "Cerebro", "Médico", ["mente", "órgano"]),
                IconData("🦷", "Diente", "Médico", ["dental", "muela"]),
                IconData("👁️", "Ojo", "Médico", ["vista", "ver"]),
                IconData("👂", "Oreja", "Médico", ["oído", "escuchar"]),
            ]
        }

class IconList:
    """Lista plana de todos los iconos"""
    
    def __init__(self):
        self.icons: List[IconData] = []
        categories = IconDatabase.get_icons()
        for cat_icons in categories.values():
            self.icons.extend(cat_icons)
            
    def find_icon_by_name(self, name: str) -> Optional[IconData]:
        for icon in self.icons:
            if icon.name == name:
                return icon
        return None
    def get_all_icons(self) -> List[IconData]:
        return self.icons
