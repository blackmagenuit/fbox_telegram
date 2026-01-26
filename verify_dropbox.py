"""
Script para verificar la configuración de Dropbox
"""
import os
from pathlib import Path

# Cargar .env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

DROPBOX_PATH = os.environ.get("DROPBOX_PATH", "")

print("=" * 60)
print("VERIFICACIÓN DE CONFIGURACIÓN DE DROPBOX")
print("=" * 60)

if DROPBOX_PATH:
    print(f"\n✅ Ruta configurada: {DROPBOX_PATH}")
    
    dropbox_path = Path(DROPBOX_PATH)
    
    if dropbox_path.exists():
        print("✅ La carpeta existe")
    else:
        print("⚠️  La carpeta no existe, se creará automáticamente")
        try:
            dropbox_path.mkdir(parents=True, exist_ok=True)
            print("✅ Carpeta creada correctamente")
        except Exception as e:
            print(f"❌ Error creando carpeta: {e}")
    
    # Probar escritura
    test_file = dropbox_path / "test_fbox.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test OK")
        print("✅ Permisos de escritura: OK")
        test_file.unlink()  # Eliminar archivo de prueba
    except Exception as e:
        print(f"❌ Error de escritura: {e}")
    
    print("\n📁 Los archivos se guardarán en:")
    print(f"   {DROPBOX_PATH}")
else:
    print("\n⚠️  No hay ruta de Dropbox configurada")
    print("Los archivos se guardarán en la carpeta actual del proyecto")

print("\n" + "=" * 60)
