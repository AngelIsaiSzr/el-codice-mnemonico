#!/usr/bin/env python3
"""
El Códice Mnemónico - Juego Principal
Un juego de aventura narrativa con puzzles cognitivos
"""

import arcade
import sys
import os

# Agregar el directorio src al path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from game.game_window import GameWindow
from utils.config import Config

def main():
    """Función principal del juego"""
    # Configurar la ventana del juego
    config = Config()
    
    # Crear y ejecutar la ventana principal
    window = GameWindow(
        config.SCREEN_WIDTH,
        config.SCREEN_HEIGHT,
        config.SCREEN_TITLE
    )
    
    # Configurar el fondo
    arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
    
    # Ejecutar el juego
    arcade.run()

if __name__ == "__main__":
    main()
