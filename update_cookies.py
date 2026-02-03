"""
Script para actualizar automáticamente las cookies del .env desde el navegador
Soporta: Chrome, Edge, Brave
"""
import sqlite3
import os
from pathlib import Path
import shutil
import win32crypt
import json

def get_chrome_cookies():
    """Extrae cookies de Chrome/Edge"""
    # Rutas de cookies para diferentes navegadores
    browsers = {
        "Chrome": os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies"),
        "Edge": os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\Network\Cookies"),
        "Brave": os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\Network\Cookies")
    }
    
    cookies = {}
    
    for browser_name, cookie_path in browsers.items():
        if not os.path.exists(cookie_path):
            continue
            
        print(f"🔍 Buscando cookies en {browser_name}...")
        
        try:
            # Copiar el archivo de cookies (SQLite está bloqueado si el navegador está abierto)
            temp_cookie = "temp_cookies.db"
            shutil.copy2(cookie_path, temp_cookie)
            
            # Conectar a la base de datos SQLite
            conn = sqlite3.connect(temp_cookie)
            cursor = conn.cursor()
            
            # Buscar cookies de america.fboxdata.com
            cursor.execute("""
                SELECT name, encrypted_value 
                FROM cookies 
                WHERE host_key LIKE '%fboxdata.com%'
            """)
            
            for name, encrypted_value in cursor.fetchall():
                if name in ['ssid', 'Admin-Token']:
                    try:
                        # Desencriptar el valor
                        decrypted_value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8')
                        cookies[name] = decrypted_value
                        print(f"  ✅ {name}: {decrypted_value[:10]}...")
                    except:
                        pass
            
            conn.close()
            os.remove(temp_cookie)
            
            if cookies:
                print(f"✅ Cookies encontradas en {browser_name}\n")
                break
                
        except Exception as e:
            print(f"  ⚠️ Error leyendo {browser_name}: {e}")
            if os.path.exists("temp_cookies.db"):
                os.remove("temp_cookies.db")
            continue
    
    return cookies

def update_env_file(cookies):
    """Actualiza el archivo .env con las nuevas cookies"""
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("❌ Archivo .env no encontrado")
        return False
    
    # Leer el archivo actual
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Actualizar las líneas con los nuevos valores
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('FBOX_SSID=') and 'ssid' in cookies:
            lines[i] = f'FBOX_SSID={cookies["ssid"]}\n'
            updated = True
            print(f"✏️ Actualizado FBOX_SSID")
        elif line.startswith('FBOX_ADMIN_TOKEN=') and 'Admin-Token' in cookies:
            lines[i] = f'FBOX_ADMIN_TOKEN={cookies["Admin-Token"]}\n'
            updated = True
            print(f"✏️ Actualizado FBOX_ADMIN_TOKEN")
    
    if updated:
        # Escribir el archivo actualizado
        with open(env_file, 'w') as f:
            f.writelines(lines)
        print("✅ Archivo .env actualizado correctamente")
        return True
    else:
        print("⚠️ No se encontraron cookies para actualizar")
        return False

if __name__ == "__main__":
    print("🔐 Actualizador de Cookies FBOX\n")
    
    cookies = get_chrome_cookies()
    
    if cookies:
        update_env_file(cookies)
    else:
        print("❌ No se encontraron cookies en ningún navegador")
        print("💡 Asegúrate de:")
        print("   1. Estar logueado en http://america.fboxdata.com")
        print("   2. Usar Chrome, Edge o Brave")
        print("   3. Cerrar el navegador antes de ejecutar este script")
