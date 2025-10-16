#!/usr/bin/env python3
"""
Script de instalación y configuración para El Códice Mnemónico
"""

import os
import sys
import subprocess
import json

def install_dependencies():
    """Instalar dependencias del proyecto"""
    print("Instalando dependencias...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error instalando dependencias: {e}")
        return False

def create_directories():
    """Crear directorios necesarios"""
    print("Creando directorios...")
    
    directories = [
        "assets/images",
        "assets/sounds", 
        "assets/fonts",
        "data/saves",
        "logs"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Directorio creado: {directory}")
        else:
            print(f"✓ Directorio ya existe: {directory}")

def create_config_file():
    """Crear archivo de configuración del usuario"""
    print("Creando archivo de configuración...")
    
    config = {
        "game_settings": {
            "screen_width": 1200,
            "screen_height": 800,
            "fullscreen": False,
            "vsync": True,
            "sound_volume": 0.7,
            "music_volume": 0.5
        },
        "player_settings": {
            "difficulty_level": 1,
            "unlocked_abilities": ["palacio_mental"],
            "completed_maps": [],
            "high_scores": {}
        },
        "debug_settings": {
            "show_fps": False,
            "show_debug_info": False,
            "log_level": "INFO"
        }
    }
    
    config_path = "data/user_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print(f"✓ Archivo de configuración creado: {config_path}")

def verify_installation():
    """Verificar que la instalación fue exitosa"""
    print("Verificando instalación...")
    
    # Verificar que los archivos principales existen
    required_files = [
        "main.py",
        "requirements.txt",
        "src/game/game_window.py",
        "src/game/game_scene.py",
        "src/puzzles/puzzle_base.py",
        "data/game_data.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("✗ Archivos faltantes:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("✓ Todos los archivos necesarios están presentes")
    return True

def test_imports():
    """Probar que los imports funcionan correctamente"""
    print("Probando imports...")
    
    try:
        import arcade
        print("✓ Arcade importado correctamente")
        
        # Probar import del juego
        sys.path.append('src')
        from game.game_window import GameWindow
        from utils.config import Config
        print("✓ Módulos del juego importados correctamente")
        
        return True
    except ImportError as e:
        print(f"✗ Error en imports: {e}")
        return False

def main():
    """Función principal de instalación"""
    print("=== INSTALADOR DE EL CÓDICE MNEMÓNICO ===")
    print()
    
    # Verificar Python version
    if sys.version_info < (3, 7):
        print("✗ Se requiere Python 3.7 o superior")
        return False
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    # Instalar dependencias
    if not install_dependencies():
        return False
    
    # Crear directorios
    create_directories()
    
    # Crear archivo de configuración
    create_config_file()
    
    # Verificar instalación
    if not verify_installation():
        return False
    
    # Probar imports
    if not test_imports():
        return False
    
    print()
    print("=== INSTALACIÓN COMPLETADA ===")
    print("El juego está listo para ejecutarse.")
    print("Ejecuta 'python main.py' para comenzar a jugar.")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
