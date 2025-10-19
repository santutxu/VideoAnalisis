"""
Gestor de proyectos de análisis
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, Any
import zipfile
import tempfile
import shutil


import json
import os
from datetime import datetime
from typing import Dict, Optional, Any
import zipfile
import tempfile
import shutil

class ProjectManager:
    """Gestor de proyectos para guardar y cargar el estado completo de la aplicación"""
    
    def __init__(self):
        self.project_file = None
        self.is_modified = False
        self.project_data = {}
        
    def create_project_data(self, video_path, moments_list, moment_types, current_frame, 
                           total_frames, fps, volume, speed, notes=""):
        """Crear estructura de datos del proyecto"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "video": {
                "path": video_path,
                "filename": os.path.basename(video_path) if video_path else "",
                "total_frames": total_frames,
                "fps": fps,
                "duration": total_frames / fps if fps > 0 else 0,
                "current_frame": current_frame,
                "last_position": current_frame
            },
            "settings": {
                "volume": volume,
                "speed": speed,
                "loop": False
            },
            "moment_types": moment_types,
            "moments": moments_list,
            "project_notes": notes,
            "metadata": {
                "total_moments": len(moments_list),
                "session_time": 0,
                "last_opened": datetime.now().isoformat()
            }
        }
        
    def save_project(self, file_path, project_data):
        """Guardar proyecto en archivo JSON"""
        try:
            # Actualizar timestamp
            project_data["last_modified"] = datetime.now().isoformat()
            
            # Crear copia de seguridad si el archivo existe
            if os.path.exists(file_path):
                backup_path = f"{file_path}.backup"
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(file_path, backup_path)
            
            # Guardar proyecto
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            self.project_file = file_path
            self.is_modified = False
            return True, "Proyecto guardado correctamente"
            
        except Exception as e:
            # Restaurar backup si falla
            if os.path.exists(f"{file_path}.backup"):
                os.rename(f"{file_path}.backup", file_path)
            return False, f"Error al guardar proyecto: {str(e)}"
            
    def load_project(self, file_path):
        """Cargar proyecto desde archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Validar estructura del proyecto
            if not self.validate_project(project_data):
                return False, "Formato de proyecto inválido", None
            
            # Verificar si el video existe
            video_path = project_data["video"]["path"]
            if not os.path.exists(video_path):
                # Buscar en el mismo directorio del proyecto
                project_dir = os.path.dirname(file_path)
                video_filename = project_data["video"]["filename"]
                alternative_path = os.path.join(project_dir, video_filename)
                
                if os.path.exists(alternative_path):
                    project_data["video"]["path"] = alternative_path
                else:
                    # Preguntar al usuario por la ubicación del video
                    return False, "Video no encontrado", project_data
            
            self.project_file = file_path
            self.is_modified = False
            
            # Actualizar último acceso
            project_data["metadata"]["last_opened"] = datetime.now().isoformat()
            
            return True, "Proyecto cargado correctamente", project_data
            
        except Exception as e:
            return False, f"Error al cargar proyecto: {str(e)}", None
            
    def validate_project(self, project_data):
        """Validar estructura del proyecto"""
        required_keys = ["version", "video", "moments", "moment_types"]
        return all(key in project_data for key in required_keys)
        
    def export_project_bundle(self, project_data, export_path):
        """Exportar proyecto con video incluido (bundle)"""
        try:
            import zipfile
            import shutil
            
            # Crear directorio temporal
            temp_dir = os.path.join(os.path.dirname(export_path), "temp_bundle")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Copiar video
            video_path = project_data["video"]["path"]
            video_filename = os.path.basename(video_path)
            shutil.copy2(video_path, os.path.join(temp_dir, video_filename))
            
            # Actualizar path en proyecto
            bundle_data = project_data.copy()
            bundle_data["video"]["path"] = video_filename
            bundle_data["is_bundle"] = True
            
            # Guardar proyecto
            project_file = os.path.join(temp_dir, "project.json")
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(bundle_data, f, indent=2, ensure_ascii=False)
            
            # Crear archivo ZIP
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            # Limpiar directorio temporal
            shutil.rmtree(temp_dir)
            
            return True, "Bundle exportado correctamente"
            
        except Exception as e:
            return False, f"Error al exportar bundle: {str(e)}"
class ProjectManager2:
    """
    Gestiona los proyectos de análisis táctico.
    Un proyecto incluye el video, eventos, configuración, etc.
    """
    
    def __init__(self):
        """Inicializa el gestor de proyectos."""
        self.project_path = None
        self.project_data = {
            'name': 'Untitled Project',
            'created_at': datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat(),
            'video_path': None,
            'video_info': {},
            'events_file': None,
            'metadata': {}
        }
        self.is_modified = False
        self.temp_dir = None
    
    def new_project(self, name: str = "New Project") -> Dict:
        """
        Crea un nuevo proyecto.
        
        Args:
            name: Nombre del proyecto
            
        Returns:
            Datos del proyecto creado
        """
        self.project_data = {
            'name': name,
            'created_at': datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat(),
            'video_path': None,
            'video_info': {},
            'events_file': None,
            'metadata': {
                'sport': 'football',
                'competition': '',
                'date': '',
                'teams': [],
                'venue': ''
            }
        }
        
        self.project_path = None
        self.is_modified = True
        
        return self.project_data
    
    def open_project(self, filepath: str) -> Dict:
        """
        Abre un proyecto existente.
        
        Args:
            filepath: Ruta al archivo de proyecto (.vta)
            
        Returns:
            Datos del proyecto
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Project file not found: {filepath}")
        
        # Los proyectos se guardan como archivos ZIP con extensión .vta
        with zipfile.ZipFile(filepath, 'r') as zf:
            # Extraer a directorio temporal
            self.temp_dir = tempfile.mkdtemp()
            zf.extractall(self.temp_dir)
            
            # Cargar metadata del proyecto
            metadata_path = os.path.join(self.temp_dir, 'project.json')
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.project_data = json.load(f)
            
            # Actualizar rutas a archivos temporales
            if self.project_data['video_path']:
                video_filename = os.path.basename(self.project_data['video_path'])
                temp_video_path = os.path.join(self.temp_dir, video_filename)
                if os.path.exists(temp_video_path):
                    self.project_data['video_path'] = temp_video_path
            
            if self.project_data['events_file']:
                events_filename = os.path.basename(self.project_data['events_file'])
                temp_events_path = os.path.join(self.temp_dir, events_filename)
                if os.path.exists(temp_events_path):
                    self.project_data['events_file'] = temp_events_path
        
        self.project_path = filepath
        self.is_modified = False
        
        return self.project_data
    
    def save_project(self, filepath: str = None, include_video: bool = False) -> str:
        """
        Guarda el proyecto actual.
        
        Args:
            filepath: Ruta donde guardar (None para usar la actual)
            include_video: Si incluir el video en el proyecto
            
        Returns:
            Ruta donde se guardó el proyecto
        """
        if filepath is None:
            filepath = self.project_path
        
        if filepath is None:
            raise ValueError("No project path specified")
        
        # Actualizar timestamp de modificación
        self.project_data['modified_at'] = datetime.now().isoformat()
        
        # Crear archivo ZIP temporal
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.vta')
        
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Guardar metadata del proyecto
            metadata_json = json.dumps(self.project_data, indent=2, ensure_ascii=False)
            zf.writestr('project.json', metadata_json)
            
            # Incluir archivo de eventos si existe
            if self.project_data['events_file'] and os.path.exists(self.project_data['events_file']):
                events_filename = os.path.basename(self.project_data['events_file'])
                zf.write(self.project_data['events_file'], events_filename)
            
            # Incluir video si se solicita
            if include_video and self.project_data['video_path'] and os.path.exists(self.project_data['video_path']):
                video_filename = os.path.basename(self.project_data['video_path'])
                zf.write(self.project_data['video_path'], video_filename)
        
        # Mover archivo temporal al destino final
        shutil.move(temp_zip.name, filepath)
        
        self.project_path = filepath
        self.is_modified = False
        
        return filepath
    
    def set_video(self, video_path: str, video_info: Dict = None):
        """
        Establece el video del proyecto.
        
        Args:
            video_path: Ruta al archivo de video
            video_info: Información adicional del video
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.project_data['video_path'] = video_path
        self.project_data['video_info'] = video_info or {}
        self.is_modified = True
    
    def set_events_file(self, events_file: str):
        """Establece el archivo de eventos del proyecto."""
        self.project_data['events_file'] = events_file
        self.is_modified = True
    
    def update_metadata(self, **kwargs):
        """Actualiza los metadatos del proyecto."""
        self.project_data['metadata'].update(kwargs)
        self.is_modified = True
    
    def export_project(self, output_dir: str, format: str = 'json') -> str:
        """
        Exporta el proyecto en el formato especificado.
        
        Args:
            output_dir: Directorio de salida
            format: Formato de exportación ('json', 'html', 'pdf')
            
        Returns:
            Ruta al archivo exportado
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.project_data['name']}_{timestamp}"
        
        if format == 'json':
            output_path = os.path.join(output_dir, f"{filename}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.project_data, f, indent=2, ensure_ascii=False)
        
        elif format == 'html':
            # Generar reporte HTML
            output_path = os.path.join(output_dir, f"{filename}.html")
            self._generate_html_report(output_path)
        
        elif format == 'pdf':
            # Generar reporte PDF
            output_path = os.path.join(output_dir, f"{filename}.pdf")
            self._generate_pdf_report(output_path)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return output_path
    
    def _generate_html_report(self, output_path: str):
        """Genera un reporte HTML del proyecto."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.project_data['name']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .metadata {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>{self.project_data['name']}</h1>
            <div class="metadata">
                <p><strong>Created:</strong> {self.project_data['created_at']}</p>
                <p><strong>Modified:</strong> {self.project_data['modified_at']}</p>
            </div>
            <div class="section">
                <h2>Project Details</h2>
                <pre>{json.dumps(self.project_data['metadata'], indent=2)}</pre>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_pdf_report(self, output_path: str):
        """Genera un reporte PDF del proyecto."""
        # Implementación básica, se puede mejorar con reportlab
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(output_path, pagesize=letter)
        c.drawString(100, 750, f"Project: {self.project_data['name']}")
        c.drawString(100, 730, f"Created: {self.project_data['created_at']}")
        c.drawString(100, 710, f"Modified: {self.project_data['modified_at']}")
        c.save()
    
    def cleanup(self):
        """Limpia recursos temporales."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None