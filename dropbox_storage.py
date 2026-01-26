"""
Módulo para interactuar con Dropbox API
Permite leer/escribir archivos JSON en Dropbox desde cualquier lugar
"""
import os
import json
from pathlib import Path

# Solo importar dropbox si está disponible (para mantener compatibilidad local)
try:
    import dropbox
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False

class DropboxStorage:
    """Maneja almacenamiento en Dropbox usando la API"""
    
    def __init__(self):
        self.access_token = os.environ.get('DROPBOX_ACCESS_TOKEN')
        self.folder_path = '/Archivos de Informatica/Archivos de FBOX'
        self.dbx = None
        
        if self.access_token and DROPBOX_AVAILABLE:
            try:
                self.dbx = dropbox.Dropbox(self.access_token)
                # Verificar que la conexión funcione
                self.dbx.users_get_current_account()
                print("✅ Conectado a Dropbox API")
            except Exception as e:
                print(f"⚠️ Error conectando a Dropbox API: {e}")
                self.dbx = None
    
    def is_available(self):
        """Verifica si Dropbox API está disponible y configurada"""
        return self.dbx is not None
    
    def read_json(self, filename):
        """Lee un archivo JSON desde Dropbox"""
        if not self.is_available():
            # Fallback a storage local
            local_path = Path(__file__).parent / filename
            if local_path.exists():
                with open(local_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        
        try:
            dropbox_path = f"{self.folder_path}/{filename}"
            metadata, response = self.dbx.files_download(dropbox_path)
            content = response.content.decode('utf-8')
            return json.loads(content)
        except dropbox.exceptions.ApiError as e:
            if hasattr(e.error, 'is_path') and e.error.is_path():
                # Archivo no existe
                return None
            print(f"Error leyendo {filename} desde Dropbox: {e}")
            return None
        except Exception as e:
            print(f"Error leyendo {filename}: {e}")
            return None
    
    def write_json(self, filename, data):
        """Escribe un archivo JSON a Dropbox"""
        if not self.is_available():
            # Fallback a storage local
            local_path = Path(__file__).parent / filename
            with open(local_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        
        try:
            dropbox_path = f"{self.folder_path}/{filename}"
            content = json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8')
            
            # Usar upload con modo overwrite
            self.dbx.files_upload(
                content,
                dropbox_path,
                mode=dropbox.files.WriteMode.overwrite
            )
            return True
        except Exception as e:
            print(f"Error escribiendo {filename} a Dropbox: {e}")
            return False
    
    def upload_file(self, local_path, dropbox_filename):
        """Sube un archivo (como Excel) a Dropbox"""
        if not self.is_available():
            print(f"⚠️ Dropbox API no disponible, archivo guardado localmente: {local_path}")
            return False
        
        try:
            dropbox_path = f"{self.folder_path}/{dropbox_filename}"
            with open(local_path, 'rb') as f:
                self.dbx.files_upload(
                    f.read(),
                    dropbox_path,
                    mode=dropbox.files.WriteMode.overwrite
                )
            print(f"✅ Archivo subido a Dropbox: {dropbox_filename}")
            return True
        except Exception as e:
            print(f"Error subiendo {dropbox_filename} a Dropbox: {e}")
            return False

# Instancia global
storage = DropboxStorage()
