"""
Utilidades y helpers del juego
"""

import random
import math
from typing import List, Tuple, Dict, Any

def generate_spiral_positions(center_x: float, center_y: float, num_points: int, 
                           radius_start: float = 50, radius_increment: float = 30) -> List[Tuple[float, float]]:
    """Generar posiciones en patrón espiral"""
    positions = []
    
    for i in range(num_points):
        if i == 0:
            positions.append((center_x, center_y))
        else:
            angle = (i - 1) * (2 * math.pi / (num_points - 1))
            radius = radius_start + (i - 1) * radius_increment
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions.append((x, y))
    
    return positions

def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calcular distancia entre dos puntos"""
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def interpolate_color(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     factor: float) -> Tuple[int, int, int]:
    """Interpolar entre dos colores"""
    r = int(color1[0] + (color2[0] - color1[0]) * factor)
    g = int(color1[1] + (color2[1] - color1[1]) * factor)
    b = int(color1[2] + (color2[2] - color1[2]) * factor)
    return (r, g, b)

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Limitar un valor entre min y max"""
    return max(min_value, min(max_value, value))

def lerp(start: float, end: float, factor: float) -> float:
    """Interpolación lineal"""
    return start + (end - start) * factor

def ease_in_out_cubic(t: float) -> float:
    """Función de easing cúbica"""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2

def generate_random_symbols(count: int, symbols: List[str] = None) -> List[str]:
    """Generar símbolos aleatorios"""
    if symbols is None:
        symbols = ["▲", "●", "■", "★", "◆", "▼", "◄", "►", "▲", "▼"]
    
    return random.choices(symbols, k=count)

def format_time(seconds: float) -> str:
    """Formatear tiempo en formato MM:SS"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def calculate_score(base_score: int, time_bonus: float, difficulty_multiplier: float, 
                   attempts_penalty: int) -> int:
    """Calcular puntuación final"""
    time_bonus_score = int(time_bonus * 10)
    difficulty_bonus = int(difficulty_multiplier * 20)
    attempts_penalty_score = attempts_penalty * 5
    
    final_score = base_score + time_bonus_score + difficulty_bonus - attempts_penalty_score
    return max(0, final_score)

class Animation:
    """Clase para animaciones simples"""
    
    def __init__(self, duration: float, start_value: float, end_value: float, 
                 easing_func=None):
        self.duration = duration
        self.start_value = start_value
        self.end_value = end_value
        self.easing_func = easing_func or ease_in_out_cubic
        self.elapsed_time = 0.0
        self.active = False
    
    def start(self):
        """Iniciar la animación"""
        self.active = True
        self.elapsed_time = 0.0
    
    def stop(self):
        """Detener la animación"""
        self.active = False
    
    def update(self, delta_time: float) -> float:
        """Actualizar la animación y devolver valor actual"""
        if not self.active:
            return self.end_value
        
        self.elapsed_time += delta_time
        
        if self.elapsed_time >= self.duration:
            self.active = False
            return self.end_value
        
        factor = self.elapsed_time / self.duration
        eased_factor = self.easing_func(factor)
        
        return lerp(self.start_value, self.end_value, eased_factor)
    
    def is_finished(self) -> bool:
        """Verificar si la animación terminó"""
        return not self.active

class Timer:
    """Timer simple para el juego"""
    
    def __init__(self, duration: float):
        self.duration = duration
        self.elapsed_time = 0.0
        self.active = False
        self.finished = False
    
    def start(self):
        """Iniciar el timer"""
        self.active = True
        self.elapsed_time = 0.0
        self.finished = False
    
    def stop(self):
        """Detener el timer"""
        self.active = False
    
    def reset(self):
        """Reiniciar el timer"""
        self.elapsed_time = 0.0
        self.finished = False
    
    def update(self, delta_time: float):
        """Actualizar el timer"""
        if not self.active:
            return
        
        self.elapsed_time += delta_time
        
        if self.elapsed_time >= self.duration:
            self.finished = True
            self.active = False
    
    def get_remaining_time(self) -> float:
        """Obtener tiempo restante"""
        return max(0, self.duration - self.elapsed_time)
    
    def get_progress(self) -> float:
        """Obtener progreso del timer (0.0 a 1.0)"""
        return min(1.0, self.elapsed_time / self.duration)
