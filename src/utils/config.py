"""
Configuración del juego El Códice Mnemónico
"""

class Config:
    """Clase de configuración"""
    
    # Configuración de pantalla
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    SCREEN_TITLE = "El Códice Mnemónico"
    
    # Configuración de colores - Tema de Ruinas Antiguas
    COLORS = {
        'background': (20, 25, 35),  # Azul oscuro profundo como piedra antigua
        'primary': (180, 160, 120),  # Dorado desgastado de pergaminos
        'secondary': (140, 120, 100),  # Marrón de piedra erosionada
        'accent': (220, 180, 100),  # Oro brillante de tesoros antiguos
        'text': (240, 235, 220),  # Pergamino claro
        'error': (200, 80, 80),  # Rojo de sellos de cera
        'success': (120, 180, 120),  # Verde musgo
        'warning': (220, 160, 80),  # Ámbar de antorchas
        'stone': (80, 85, 90),  # Piedra gris
        'moss': (100, 140, 100),  # Verde musgo
        'torch': (255, 200, 100),  # Llama de antorcha
        'shadow': (10, 15, 20),  # Sombra profunda
        'glow': (255, 220, 150, 100)  # Resplandor dorado
    }
    
    # Configuración de fuentes
    FONT_SIZE_LARGE = 24
    FONT_SIZE_MEDIUM = 18
    FONT_SIZE_SMALL = 14
    
    # Configuración de puzzles
    PUZZLE_TIMEOUT = 30  # segundos
    PUZZLE_DIFFICULTY_INCREMENT = 0.1
    
    # Configuración de habilidades cognitivas
    PALACIO_MENTAL_CAPACITY = 3
    VISION_PERIFERICA_DURATION = 5  # segundos
    ENFOQUE_DURATION = 3  # segundos
    
    # Configuración de mapa mental
    MAP_NODES_MIN = 5
    MAP_NODES_MAX = 15
    MAP_CONNECTIONS_MIN = 2
    MAP_CONNECTIONS_MAX = 4
