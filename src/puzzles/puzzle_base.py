"""
Sistema base de puzzles
"""

import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from utils.config import Config

class Puzzle(ABC):
    """Clase base abstracta para todos los puzzles"""
    
    def __init__(self, difficulty: float = 1.0, config: Config = None):
        self.config = config or Config()
        self.difficulty = difficulty
        self.completed = False
        self.start_time = time.time()
        self.time_limit = self.config.PUZZLE_TIMEOUT
        self.score = 0
        self.attempts = 0
        self.max_attempts = 3
        
        # Estado del puzzle
        self.current_step = 0
        self.total_steps = 0
        self.hints_used = 0
        self.max_hints = 2
        
        # Anomalías activas
        self.active_anomalies: List[str] = []
        
        # Control de pausa del timer
        self.is_paused = False
        self.paused_time = 0.0  # Tiempo acumulado mientras estaba pausado
    
    def _draw_ruins_background(self, screen_width: int, screen_height: int):
        """Dibujar fondo atmosférico de ruinas"""
        import arcade
        
        # Fondo base con gradiente
        arcade.draw_lrbt_rectangle_filled(
            0, screen_width, 0, screen_height,
            self.config.COLORS['background']
        )
        
        # Efectos de piedra antigua
        for i in range(0, screen_width, 120):
            for j in range(0, screen_height, 120):
                # Textura de piedra sutil
                stone_color = (
                    self.config.COLORS['stone'][0] + (i % 25) - 12,
                    self.config.COLORS['stone'][1] + (j % 25) - 12,
                    self.config.COLORS['stone'][2] + ((i+j) % 25) - 12
                )
                arcade.draw_lrbt_rectangle_filled(
                    i, i + 120, j, j + 120,
                    stone_color
                )
        
        # Efectos de musgo en las esquinas
        moss_positions = [
            (screen_width - 250, 0, screen_width, 180),
            (screen_width - 250, screen_height - 180, screen_width, screen_height),
            (0, 0, 250, 180),
            (0, screen_height - 180, 250, screen_height)
        ]
        
        for x1, y1, x2, y2 in moss_positions:
            arcade.draw_lrbt_rectangle_filled(
                x1, x2, y1, y2,
                (*self.config.COLORS['moss'], 70)
            )

    def _draw_ruins_lighting(self, screen_width: int, screen_height: int):
        """Dibujar efectos de iluminación de ruinas"""
        import arcade
        
        # Luz central mística
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Resplandor central más intenso
        for radius in [400, 300, 200, 100]:
            alpha = max(0, 60 - radius // 8)
            arcade.draw_circle_filled(
                center_x, center_y, radius,
                (*self.config.COLORS['torch'], alpha)
            )
        
        # Antorchas en las esquinas
        torch_positions = [
            (120, screen_height - 120),
            (screen_width - 120, screen_height - 120),
            (120, 120),
            (screen_width - 120, 120)
        ]
        
        for tx, ty in torch_positions:
            # Llama de antorcha
            arcade.draw_circle_filled(tx, ty, 20, self.config.COLORS['torch'])
            # Resplandor de antorcha
            for radius in [50, 35, 20]:
                alpha = max(0, 40 - radius)
                arcade.draw_circle_filled(
                    tx, ty, radius,
                    (*self.config.COLORS['torch'], alpha)
                )

    def _draw_puzzle_title(self, title: str, screen_width: int, screen_height: int):
        """Dibujar título del puzzle con estilo de pergamino"""
        import arcade
        
        # Fondo de pergamino para el título
        arcade.draw_lrbt_rectangle_filled(
            screen_width // 2 - 200, screen_width // 2 + 200,
            screen_height - 80, screen_height - 20,
            (*self.config.COLORS['primary'], 240)
        )
        # Borde exterior
        arcade.draw_lrbt_rectangle_outline(
            screen_width // 2 - 200, screen_width // 2 + 200,
            screen_height - 80, screen_height - 20,
            self.config.COLORS['secondary'], 5
        )
        # Borde interior
        arcade.draw_lrbt_rectangle_outline(
            screen_width // 2 - 195, screen_width // 2 + 195,
            screen_height - 75, screen_height - 25,
            (*self.config.COLORS['accent'], 150), 3
        )
        
        # Título con efecto de texto épico
        arcade.draw_text(
            title,
            screen_width // 2 + 3, screen_height - 64,
            self.config.COLORS['shadow'],
            font_size=self.config.FONT_SIZE_LARGE,
            anchor_x="center",
            bold=True
        )
        arcade.draw_text(
            title,
            screen_width // 2, screen_height - 61,
            self.config.COLORS['accent'],
            font_size=self.config.FONT_SIZE_LARGE,
            anchor_x="center",
            bold=True
        )
    
    def _draw_instructions_panel(self, screen_width: int, screen_height: int, instruction_text: str):
        """Dibujar panel de instrucciones con estilo de pergamino"""
        import arcade
        
        # Panel de instrucciones
        panel_y = screen_height - 140
        arcade.draw_lrbt_rectangle_filled(
            screen_width // 2 - 300, screen_width // 2 + 300,
            panel_y - 30, panel_y + 10,
            (*self.config.COLORS['primary'], 200)
        )
        arcade.draw_lrbt_rectangle_outline(
            screen_width // 2 - 300, screen_width // 2 + 300,
            panel_y - 30, panel_y + 10,
            self.config.COLORS['secondary'], 3
        )
        arcade.draw_lrbt_rectangle_outline(
            screen_width // 2 - 295, screen_width // 2 + 295,
            panel_y - 25, panel_y + 5,
            (*self.config.COLORS['accent'], 100), 2
        )
        
        # Texto de instrucciones con sombra
        arcade.draw_text(
            instruction_text,
            screen_width // 2 + 2, panel_y - 19,
            self.config.COLORS['shadow'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            anchor_x="center",
            bold=True
        )
        arcade.draw_text(
            instruction_text,
            screen_width // 2, panel_y - 17,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            anchor_x="center",
            bold=True
        )
    
    @abstractmethod
    def setup_puzzle(self):
        """Configurar el puzzle inicial"""
        pass
    
    @abstractmethod
    def handle_input(self, input_data: Any) -> bool:
        """Manejar entrada del usuario"""
        pass
    
    @abstractmethod
    def draw_puzzle(self, screen_width: int, screen_height: int):
        """Dibujar el puzzle en pantalla"""
        pass
    
    @abstractmethod
    def get_hint(self) -> str:
        """Obtener una pista para el puzzle"""
        pass
    
    def is_time_up(self) -> bool:
        """Verificar si se agotó el tiempo"""
        if self.is_paused:
            # Si está pausado, verificar usando el tiempo pausado
            return self.paused_time >= self.time_limit
        else:
            # Si no está pausado, verificar normalmente
            return time.time() - self.start_time >= self.time_limit
    
    def get_remaining_time(self) -> float:
        """Obtener tiempo restante"""
        if self.is_paused:
            # Si está pausado, devolver el tiempo que quedaba cuando se pausó
            return max(0, self.time_limit - self.paused_time)
        else:
            # Si no está pausado, calcular normalmente
            return max(0, self.time_limit - (time.time() - self.start_time))
    
    def is_timer_active(self) -> bool:
        """Verificar si el timer está activo"""
        return not self.is_paused  # El timer está activo solo si no está pausado
    
    def pause_timer(self):
        """Pausar el timer del puzzle"""
        if not self.is_paused:
            self.is_paused = True
            # Guardar el tiempo transcurrido hasta ahora
            self.paused_time = time.time() - self.start_time
    
    def resume_timer(self):
        """Reanudar el timer del puzzle"""
        if self.is_paused:
            self.is_paused = False
            # Ajustar el start_time para que el timer continúe desde donde se pausó
            self.start_time = time.time() - self.paused_time
    
    def add_anomaly(self, anomaly_type: str):
        """Agregar una anomalía al puzzle"""
        if anomaly_type not in self.active_anomalies:
            self.active_anomalies.append(anomaly_type)
    
    def remove_anomaly(self, anomaly_type: str):
        """Remover una anomalía del puzzle"""
        if anomaly_type in self.active_anomalies:
            self.active_anomalies.remove(anomaly_type)
    
    def has_anomaly(self, anomaly_type: str) -> bool:
        """Verificar si tiene una anomalía activa"""
        return anomaly_type in self.active_anomalies
    
    def calculate_score(self) -> int:
        """Calcular puntuación basada en rendimiento"""
        base_score = 100
        
        # Penalización por tiempo
        time_penalty = int((self.time_limit - self.get_remaining_time()) * 2)
        
        # Penalización por intentos
        attempt_penalty = self.attempts * 10
        
        # Penalización por pistas
        hint_penalty = self.hints_used * 15
        
        # Bonus por dificultad
        difficulty_bonus = int(self.difficulty * 20)
        
        final_score = max(0, base_score - time_penalty - attempt_penalty - hint_penalty + difficulty_bonus)
        return final_score
    
    def complete_puzzle(self):
        """Completar el puzzle"""
        self.completed = True
        self.score = self.calculate_score()

class SimonDicePuzzle(Puzzle):
    """Puzzle tipo Simón Dice con símbolos"""
    
    def __init__(self, difficulty: float = 1.0, config: Config = None):
        super().__init__(difficulty, config)
        self.sequence: List[str] = []
        self.player_sequence: List[str] = []
        self.symbols = ["▲", "●", "■", "★", "◆", "▼"]
        self.current_symbol_index = 0
        self.showing_sequence = True
        self.sequence_delay = 1.0
        self.last_symbol_time = 0
        self.timer_started = False  # Para controlar cuándo inicia el timer
        
    def setup_puzzle(self):
        """Configurar el puzzle de Simón Dice"""
        # Generar secuencia basada en dificultad
        sequence_length = int(3 + self.difficulty * 2)
        self.sequence = random.choices(self.symbols, k=sequence_length)
        self.total_steps = sequence_length
        self.current_symbol_index = 0
        self.player_sequence = []
        self.showing_sequence = True
        self.last_symbol_time = time.time()
        self.timer_started = False  # Timer no iniciado hasta terminar demostración
    
    def is_timer_active(self) -> bool:
        """Verificar si el timer está activo"""
        return self.timer_started and not self.showing_sequence
    
    def update(self, delta_time: float):
        """Actualizar el puzzle"""
        # Si la demostración terminó y el timer no ha iniciado, iniciarlo
        if not self.showing_sequence and not self.timer_started:
            self.start_time = time.time()
            self.timer_started = True
    
    def handle_input(self, input_data: str) -> bool:
        """Manejar entrada del jugador"""
        if self.showing_sequence:
            return False  # No aceptar entrada mientras se muestra la secuencia
        
        if isinstance(input_data, str) and input_data in self.symbols:
            self.player_sequence.append(input_data)
            self.attempts += 1
            
            # Verificar si la secuencia es correcta hasta ahora
            if len(self.player_sequence) <= len(self.sequence):
                if self.player_sequence[-1] != self.sequence[len(self.player_sequence) - 1]:
                    # Secuencia incorrecta, reiniciar
                    self.player_sequence = []
                    return False  # Secuencia incorrecta
            
            # Verificar si se completó la secuencia
            if len(self.player_sequence) == len(self.sequence):
                if self.player_sequence == self.sequence:
                    self.complete_puzzle()
                    return True
                else:
                    # Secuencia incorrecta, reiniciar
                    self.player_sequence = []
                    return False
        
        return False
    
    def draw_puzzle(self, screen_width: int, screen_height: int):
        """Dibujar el puzzle de Simón Dice con diseño de ruinas"""
        import arcade
        
        # Fondo atmosférico de ruinas
        self._draw_ruins_background(screen_width, screen_height)
        
        # Efectos de iluminación
        self._draw_ruins_lighting(screen_width, screen_height)
        
        # Título con estilo de pergamino
        self._draw_puzzle_title("SIMÓN DICE - SÍMBOLOS", screen_width, screen_height)
        
        # Instrucciones con panel de pergamino
        instruction_text = ("Observa la secuencia de símbolos que aparece" if self.showing_sequence 
                           else "Reproduce la secuencia usando las teclas 1-6")
        self._draw_instructions_panel(screen_width, screen_height, instruction_text)
        
        # Mostrar qué tecla corresponde a qué símbolo (con símbolos más grandes)
        arcade.draw_text(
            "1=▲ 2=● 3=■ 4=★ 5=◆ 6=▼",
            screen_width // 2,
            screen_height - 110,
            self.config.COLORS['accent'],
            font_size=self.config.FONT_SIZE_SMALL,
            anchor_x="center"
        )
        
        # Mostrar secuencia o símbolos para seleccionar
        if self.showing_sequence:
            self._draw_sequence(screen_width, screen_height)
        else:
            self._draw_symbol_selection(screen_width, screen_height)
        
        # Información del puzzle
        self._draw_puzzle_info(screen_width, screen_height)
    
    def _draw_sequence(self, screen_width: int, screen_height: int):
        """Dibujar la secuencia que se está mostrando"""
        import arcade
        
        # Mostrar símbolo actual de la secuencia
        if self.current_symbol_index < len(self.sequence):
            symbol = self.sequence[self.current_symbol_index]
            arcade.draw_text(
                symbol,
                screen_width // 2,
                screen_height // 2,
                self.config.COLORS['accent'],
                font_size=72,
                anchor_x="center",
                anchor_y="center"
            )
            
            # Avanzar al siguiente símbolo
            if time.time() - self.last_symbol_time >= self.sequence_delay:
                self.current_symbol_index += 1
                self.last_symbol_time = time.time()
                
                if self.current_symbol_index >= len(self.sequence):
                    self.showing_sequence = False
                    # Iniciar timer cuando termine la demostración
                    if not self.timer_started:
                        self.start_time = time.time()
                        self.timer_started = True
        else:
            self.showing_sequence = False
    
    def _draw_symbol_selection(self, screen_width: int, screen_height: int):
        """Dibujar los símbolos para seleccionar"""
        import arcade
        
        # Mostrar símbolos disponibles
        symbol_size = 60
        card_width = symbol_size + 30  # Ancho total de cada tarjeta
        spacing = card_width + 20  # Espacio entre tarjetas (sin superposición)
        total_width = (len(self.symbols) - 2) * spacing + card_width  # Ancho total real
        start_x = screen_width // 2 - total_width // 2  # Centrar horizontalmente
        
        for i, symbol in enumerate(self.symbols):
            x = start_x + i * spacing
            y = screen_height // 2
            
            # Fondo de pergamino para cada símbolo
            arcade.draw_lrbt_rectangle_filled(
                x - card_width // 2, x + card_width // 2,
                y - symbol_size - 15, y + symbol_size + 15,
                (*self.config.COLORS['primary'], 220)
            )
            arcade.draw_lrbt_rectangle_outline(
                x - card_width // 2, x + card_width // 2,
                y - symbol_size - 15, y + symbol_size + 15,
                self.config.COLORS['secondary'], 3
            )
            arcade.draw_lrbt_rectangle_outline(
                x - card_width // 2 + 5, x + card_width // 2 - 5,
                y - symbol_size - 10, y + symbol_size + 10,
                (*self.config.COLORS['accent'], 150), 2
            )
            
            # Símbolo con sombra
            arcade.draw_text(
                symbol,
                x + 2, y - 2,
                self.config.COLORS['shadow'],
                font_size=symbol_size,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )
            arcade.draw_text(
                symbol,
                x, y,
                self.config.COLORS['accent'],
                font_size=symbol_size,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )
            
            # Dibujar borde si está disponible
            arcade.draw_lrbt_rectangle_outline(
                x - (symbol_size + 10) // 2,
                x + (symbol_size + 10) // 2,
                y - (symbol_size + 10) // 2,
                y + (symbol_size + 10) // 2,
                self.config.COLORS['primary'],
                2
            )
        
        # Mostrar secuencia del jugador
        if self.player_sequence:
            arcade.draw_text(
                "Tu secuencia: " + " ".join(self.player_sequence),
                screen_width // 2,
                screen_height // 2 - 100,
                self.config.COLORS['shadow'],
                font_size=self.config.FONT_SIZE_MEDIUM,
                anchor_x="center"
            )
            
            # Mostrar progreso
            progress = len(self.player_sequence) / len(self.sequence)
            arcade.draw_text(
                f"Progreso: {progress:.1%}",
                screen_width // 2,
                screen_height // 2 - 130,
                self.config.COLORS['text'],
                font_size=self.config.FONT_SIZE_SMALL,
                anchor_x="center"
            )
        else:
            arcade.draw_text(
                "Presiona las teclas 1-6 para reproducir la secuencia",
                screen_width // 2,
                screen_height // 2 - 100,
                self.config.COLORS['text'],
                font_size=self.config.FONT_SIZE_MEDIUM,
                anchor_x="center"
            )
    
    def _draw_puzzle_info(self, screen_width: int, screen_height: int):
        """Dibujar información del puzzle"""
        import arcade
        
        # Solo mostrar información básica aquí, el temporizador se maneja en game_scene
        # Progreso
        progress = len(self.player_sequence) / len(self.sequence) if self.sequence else 0
        arcade.draw_text(
            f"Progreso: {progress:.1%}",
            20,
            screen_height - 70,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_SMALL
        )
    
    def get_hint(self) -> str:
        """Obtener una pista"""
        if self.hints_used >= self.max_hints:
            return "No hay más pistas disponibles"
        
        self.hints_used += 1
        
        if self.showing_sequence:
            return "Observa cuidadosamente la secuencia de símbolos"
        else:
            if self.player_sequence:
                next_symbol = self.sequence[len(self.player_sequence)]
                return f"El siguiente símbolo es: {next_symbol}"
            else:
                return "Reproduce la secuencia que viste"

class MemoriaEspacialPuzzle(Puzzle):
    """Puzzle de memoria espacial - recordar posiciones"""
    
    def __init__(self, difficulty: float = 1.0, config: Config = None):
        super().__init__(difficulty, config)
        self.positions: List[Tuple[int, int]] = []
        self.player_positions: List[Tuple[int, int]] = []
        self.grid_size = 4
        self.current_position_index = 0
        self.showing_positions = True
        self.position_delay = 1.0
        self.last_position_time = 0
        
    def setup_puzzle(self):
        """Configurar el puzzle de memoria espacial"""
        # Generar posiciones basadas en dificultad
        num_positions = int(2 + self.difficulty)
        self.positions = []
        
        for _ in range(num_positions):
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            self.positions.append((x, y))
        
        self.total_steps = num_positions
        self.current_position_index = 0
        self.player_positions = []
        self.showing_positions = True
        self.last_position_time = time.time()
    
    def is_timer_active(self) -> bool:
        """Verificar si el timer está activo"""
        return not self.showing_positions
    
    def handle_input(self, input_data: str) -> bool:
        """Manejar entrada del jugador"""
        if self.showing_positions:
            return False  # No aceptar entrada mientras se muestran las posiciones
        
        # Manejar entrada de coordenadas como "x,y" o teclas individuales
        if isinstance(input_data, str):
            if ',' in input_data:
                # Formato "x,y"
                try:
                    x, y = map(int, input_data.split(','))
                    if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                        self.player_positions.append((x, y))
                        self.attempts += 1
                        
                        # Verificar si la posición es correcta
                        if len(self.player_positions) <= len(self.positions):
                            expected_pos = self.positions[len(self.player_positions) - 1]
                            if (x, y) != expected_pos:
                                # Incorrecto, reiniciar
                                self.player_positions = []
                                print(f"Incorrecto. La posición correcta era {expected_pos}")
                                return False
                        
                        # Si todas las posiciones han sido ingresadas correctamente
                        if len(self.player_positions) == len(self.positions):
                            print("¡CORRECTO! Has completado la secuencia")
                            self.complete_puzzle()
                            return True
                        return True
                except ValueError:
                    print("Formato inválido. Usa 'x,y' (ejemplo: '0,1')")
                    return False
            elif input_data.isdigit() and input_data in ['1', '2', '3', '4']:
                # Entrada numérica para coordenadas (solo 1-4)
                if not hasattr(self, 'current_input'):
                    self.current_input = ""
                
                self.current_input += input_data
                print(f"Entrada actual: {self.current_input}")
                
                # Si tenemos 2 dígitos, procesar como coordenada
                if len(self.current_input) == 2:
                    try:
                        x = int(self.current_input[0]) - 1  # Convertir 1-4 a 0-3
                        y = int(self.current_input[1]) - 1  # Convertir 1-4 a 0-3
                        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                            self.player_positions.append((x, y))
                            self.attempts += 1
                            self.current_input = ""
                            
                            # Verificar si la posición es correcta
                            if len(self.player_positions) <= len(self.positions):
                                expected_pos = self.positions[len(self.player_positions) - 1]
                                if (x, y) != expected_pos:
                                    # Incorrecto, reiniciar
                                    self.player_positions = []
                                    print(f"Incorrecto. La posición correcta era ({expected_pos[0]+1}, {expected_pos[1]+1})")
                                    return False
                            
                            # Si todas las posiciones han sido ingresadas correctamente
                            if len(self.player_positions) == len(self.positions):
                                print("¡CORRECTO! Has completado la secuencia")
                                self.complete_puzzle()
                                return True
                            return True
                        else:
                            print("Coordenadas fuera de rango. Usa 1-4")
                            self.current_input = ""
                            return False
                    except ValueError:
                        self.current_input = ""
                        return False
                return True
            elif input_data == "BACKSPACE":
                # Borrar último dígito
                if hasattr(self, 'current_input') and self.current_input:
                    self.current_input = self.current_input[:-1]
                    print(f"Entrada actual: {self.current_input}")
                return True
        
        return False
    
    def draw_puzzle(self, screen_width: int, screen_height: int):
        """Dibujar el puzzle de memoria espacial con diseño de ruinas"""
        import arcade
        
        # Fondo atmosférico de ruinas
        self._draw_ruins_background(screen_width, screen_height)
        
        # Efectos de iluminación
        self._draw_ruins_lighting(screen_width, screen_height)
        
        # Título con estilo de pergamino
        self._draw_puzzle_title("MEMORIA ESPACIAL", screen_width, screen_height)
        
        # Instrucciones con panel de pergamino
        instruction_text = ("Observa las posiciones que se iluminan en la cuadrícula" if self.showing_positions
                           else "Reproduce las posiciones usando coordenadas")
        self._draw_instructions_panel(screen_width, screen_height, instruction_text)
        
        arcade.draw_text(
            "Usa las teclas 1-4 para coordenadas (ejemplo: 12 = columna 1, fila 2)",
            screen_width // 2,
                screen_height - 110,
            self.config.COLORS['accent'],
            font_size=self.config.FONT_SIZE_SMALL,
            anchor_x="center"
        )
        
        # Mostrar entrada actual
        current_input = getattr(self, 'current_input', "")
        if current_input:
            arcade.draw_text(
                f"Entrada actual: {current_input}",
                screen_width // 2,
                screen_height - 190,
                self.config.COLORS['shadow'],
                font_size=self.config.FONT_SIZE_SMALL,
                anchor_x="center"
            )
        
        # Dibujar grid
        self._draw_grid(screen_width, screen_height)
        
        # Información del puzzle
        self._draw_puzzle_info(screen_width, screen_height)
    
    def _draw_grid(self, screen_width: int, screen_height: int):
        """Dibujar el grid de posiciones con diseño de pergamino"""
        import arcade
        
        grid_size = 200
        start_x = screen_width // 2 - grid_size // 2
        start_y = screen_height // 2 - grid_size // 2
        cell_size = grid_size // self.grid_size
        
        # Fondo de pergamino para la cuadrícula
        arcade.draw_lrbt_rectangle_filled(
            start_x - 20, start_x + grid_size + 20,
            start_y - 20, start_y + grid_size + 20,
            (*self.config.COLORS['primary'], 200)
        )
        arcade.draw_lrbt_rectangle_outline(
            start_x - 20, start_x + grid_size + 20,
            start_y - 20, start_y + grid_size + 20,
            self.config.COLORS['secondary'], 4
        )
        arcade.draw_lrbt_rectangle_outline(
            start_x - 15, start_x + grid_size + 15,
            start_y - 15, start_y + grid_size + 15,
            (*self.config.COLORS['accent'], 150), 2
        )
        
        # Dibujar grid
        for i in range(self.grid_size + 1):
            # Líneas verticales
            arcade.draw_line(
                start_x + i * cell_size, start_y,
                start_x + i * cell_size, start_y + grid_size,
                self.config.COLORS['secondary'], 2
            )
            # Líneas horizontales
            arcade.draw_line(
                start_x, start_y + i * cell_size,
                start_x + grid_size, start_y + i * cell_size,
                self.config.COLORS['secondary'], 2
            )
        
        # Dibujar números de coordenadas en cada celda
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cell_x = start_x + j * cell_size + cell_size // 2
                cell_y = start_y + i * cell_size + cell_size // 2
                
                # Coordenadas del 1 al 4
                coord_x = j + 1
                coord_y = i + 1
                
                # Fondo de celda
                arcade.draw_lrbt_rectangle_filled(
                    start_x + j * cell_size + 2, start_x + (j + 1) * cell_size - 2,
                    start_y + i * cell_size + 2, start_y + (i + 1) * cell_size - 2,
                    (*self.config.COLORS['primary'], 150)
                )
                
                # Coordenadas con sombra
                arcade.draw_text(
                    f"{coord_x},{coord_y}",
                    cell_x + 1, cell_y - 1,
                    self.config.COLORS['shadow'],
                    font_size=10,
                    anchor_x="center",
                    anchor_y="center"
                )
                arcade.draw_text(
                    f"{coord_x},{coord_y}",
                    cell_x, cell_y,
                    self.config.COLORS['accent'],
                    font_size=10,
                    anchor_x="center",
                    anchor_y="center"
                )
        
        # Dibujar posiciones
        if self.showing_positions:
            # Mostrar posición actual
            if self.current_position_index < len(self.positions):
                x, y = self.positions[self.current_position_index]
                cell_x = start_x + x * cell_size + cell_size // 2
                cell_y = start_y + y * cell_size + cell_size // 2
                
                arcade.draw_circle_filled(
                    cell_x, cell_y, cell_size // 3,
                    self.config.COLORS['accent']
                )
                
                # Avanzar al siguiente símbolo
                if time.time() - self.last_position_time >= self.position_delay:
                    self.current_position_index += 1
                    self.last_position_time = time.time()
                    
                    if self.current_position_index >= len(self.positions):
                        self.showing_positions = False
        else:
            # Mostrar posiciones del jugador
            for i, (x, y) in enumerate(self.player_positions):
                cell_x = start_x + x * cell_size + cell_size // 2
                cell_y = start_y + y * cell_size + cell_size // 2
                
                color = self.config.COLORS['success'] if i < len(self.positions) and (x, y) == self.positions[i] else self.config.COLORS['error']
                arcade.draw_circle_filled(
                    cell_x, cell_y, cell_size // 4,
                    color
                )
    
    def _draw_puzzle_info(self, screen_width: int, screen_height: int):
        """Dibujar información del puzzle"""
        import arcade
        
        # Solo mostrar información básica aquí, el temporizador se maneja en game_scene
        # Progreso
        progress = len(self.player_positions) / len(self.positions) if self.positions else 0
        arcade.draw_text(
            f"Progreso: {progress:.1%}",
            20,
            screen_height - 70,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_SMALL
        )
    
    def get_hint(self) -> str:
        """Obtener una pista"""
        if self.hints_used >= self.max_hints:
            return "No hay más pistas disponibles"
        
        self.hints_used += 1
        
        if self.showing_positions:
            return "Observa cuidadosamente el orden de las posiciones"
        else:
            if self.player_positions:
                next_pos = self.positions[len(self.player_positions)]
                return f"La siguiente posición es: {next_pos[0]},{next_pos[1]}"
            else:
                return "Reproduce las posiciones en el mismo orden"

class PatronSecuenciaPuzzle(Puzzle):
    """Puzzle de patrones y secuencias lógicas"""
    
    def __init__(self, difficulty: float = 1.0, config: Config = None):
        super().__init__(difficulty, config)
        self.sequence: List[int] = []
        self.player_answer: Optional[int] = None
        self.pattern_type = ""
        
    def setup_puzzle(self):
        """Configurar el puzzle de patrones"""
        # Generar diferentes tipos de patrones
        pattern_types = ["arithmetic", "geometric", "fibonacci", "prime"]
        self.pattern_type = random.choice(pattern_types)
        
        if self.pattern_type == "arithmetic":
            self._generate_arithmetic_sequence()
        elif self.pattern_type == "geometric":
            self._generate_geometric_sequence()
        elif self.pattern_type == "fibonacci":
            self._generate_fibonacci_sequence()
        elif self.pattern_type == "prime":
            self._generate_prime_sequence()
        
        self.total_steps = 1
        self.player_answer = None
    
    def _generate_arithmetic_sequence(self):
        """Generar secuencia aritmética"""
        start = random.randint(1, 10)
        step = random.randint(2, 5)
        length = int(4 + self.difficulty)
        
        self.sequence = [start + i * step for i in range(length)]
    
    def _generate_geometric_sequence(self):
        """Generar secuencia geométrica"""
        start = random.randint(2, 5)
        ratio = random.randint(2, 3)
        length = int(4 + self.difficulty)
        
        self.sequence = [start * (ratio ** i) for i in range(length)]
    
    def _generate_fibonacci_sequence(self):
        """Generar secuencia de Fibonacci"""
        length = int(5 + self.difficulty)
        self.sequence = [1, 1]
        
        for i in range(2, length):
            self.sequence.append(self.sequence[i-1] + self.sequence[i-2])
    
    def _generate_prime_sequence(self):
        """Generar secuencia de números primos"""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        length = int(4 + self.difficulty)
        self.sequence = primes[:length]
    
    def handle_input(self, input_data: str) -> bool:
        """Manejar entrada del jugador"""
        if self.completed:
            return False

        if input_data.isdigit():
            if not hasattr(self, 'player_input_str'):
                self.player_input_str = ""
            self.player_input_str += input_data
            return True
        elif input_data == "BACKSPACE":
            if hasattr(self, 'player_input_str') and self.player_input_str:
                self.player_input_str = self.player_input_str[:-1]
            return True
        elif input_data == "ENTER":
            if not hasattr(self, 'player_input_str') or not self.player_input_str:
                print("¡Ingresa un número antes de presionar ENTER!")
                return False

            try:
                player_answer = int(self.player_input_str)
                self.attempts += 1
                correct_answer = self._calculate_next_number()

                if player_answer == correct_answer:
                    print(f"¡CORRECTO! La respuesta era {correct_answer}")
                    self.complete_puzzle()
                    return True
                else:
                    print(f"Incorrecto. La respuesta correcta era {correct_answer}")
                    self.player_input_str = ""
                    return False
            except ValueError:
                print("Entrada inválida. Solo números.")
                self.player_input_str = ""
                return False
        
        return False
    
    def _show_error_message(self, message: str):
        """Mostrar mensaje de error temporalmente"""
        # Por ahora solo imprimir, podríamos implementar un sistema de mensajes en pantalla
        print(f"Error: {message}")
    
    def _calculate_next_number(self) -> int:
        """Calcular el siguiente número en la secuencia"""
        if self.pattern_type == "arithmetic":
            step = self.sequence[1] - self.sequence[0]
            return self.sequence[-1] + step
        elif self.pattern_type == "geometric":
            ratio = self.sequence[1] // self.sequence[0]
            return self.sequence[-1] * ratio
        elif self.pattern_type == "fibonacci":
            return self.sequence[-1] + self.sequence[-2]
        elif self.pattern_type == "prime":
            # Encontrar el siguiente primo
            last_prime = self.sequence[-1]
            candidate = last_prime + 1
            while not self._is_prime(candidate):
                candidate += 1
            return candidate
        
        return 0
    
    def _is_prime(self, n: int) -> bool:
        """Verificar si un número es primo"""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    def draw_puzzle(self, screen_width: int, screen_height: int):
        """Dibujar el puzzle de patrones con diseño de ruinas"""
        import arcade
        
        # Fondo atmosférico de ruinas
        self._draw_ruins_background(screen_width, screen_height)
        
        # Efectos de iluminación
        self._draw_ruins_lighting(screen_width, screen_height)
        
        # Título con estilo de pergamino
        self._draw_puzzle_title("PATRÓN DE SECUENCIA", screen_width, screen_height)
        
        # Instrucciones con panel de pergamino
        instruction_text = "ENTER para enviar | BACKSPACE para borrar"
        self._draw_instructions_panel(screen_width, screen_height, instruction_text)
        
        # Mostrar secuencia con fondo de pergamino
        sequence_text = " ".join(map(str, self.sequence))
        sequence_panel_y = screen_height // 2 + 50
        
        # Fondo de pergamino para la secuencia
        arcade.draw_lrbt_rectangle_filled(
            screen_width // 2 - 200, screen_width // 2 + 200,
            sequence_panel_y - 30, sequence_panel_y + 10,
            (*self.config.COLORS['primary'], 220)
        )
        arcade.draw_lrbt_rectangle_outline(
            screen_width // 2 - 200, screen_width // 2 + 200,
            sequence_panel_y - 30, sequence_panel_y + 10,
            self.config.COLORS['secondary'], 3
        )
        arcade.draw_lrbt_rectangle_outline(
            screen_width // 2 - 195, screen_width // 2 + 195,
            sequence_panel_y - 25, sequence_panel_y + 5,
            (*self.config.COLORS['accent'], 150), 2
        )
        
        # Secuencia con sombra
        arcade.draw_text(
            sequence_text,
            screen_width // 2 + 2, sequence_panel_y - 19,
            self.config.COLORS['shadow'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            anchor_x="center",
            bold=True
        )
        arcade.draw_text(
            sequence_text,
            screen_width // 2, sequence_panel_y - 17,
            self.config.COLORS['accent'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            anchor_x="center",
            bold=True
        )
        
        # Mostrar qué teclas utilizar
        arcade.draw_text(
            "Usa las teclas 0-9 para ingresar tu respuesta",
            screen_width // 2,
            screen_height - 110,
            self.config.COLORS['accent'],
            font_size=self.config.FONT_SIZE_SMALL,
            anchor_x="center"
        )

        # Mostrar entrada del jugador
        player_input = getattr(self, 'player_input_str', "")
        arcade.draw_text(
            f"Tu respuesta: {player_input}",
            screen_width // 2,
            screen_height // 2 - 5,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "¿Cuál es el siguiente número?",
            screen_width // 2,
            screen_height // 2 - 30,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_SMALL,
            anchor_x="center"
        )
        
        # Información del puzzle
        self._draw_puzzle_info(screen_width, screen_height)
    
    def _draw_puzzle_info(self, screen_width: int, screen_height: int):
        """Dibujar información del puzzle"""
        import arcade
        
        # No dibujar información aquí para evitar superposición con game_scene
        pass
    
    def get_hint(self) -> str:
        """Obtener una pista"""
        if self.hints_used >= self.max_hints:
            return "No hay más pistas disponibles"
        
        self.hints_used += 1
        
        if self.pattern_type == "arithmetic":
            step = self.sequence[1] - self.sequence[0]
            return f"Suma {step} al último número"
        elif self.pattern_type == "geometric":
            ratio = self.sequence[1] // self.sequence[0]
            return f"Multiplica el último número por {ratio}"
        elif self.pattern_type == "fibonacci":
            return "Suma los dos últimos números"
        elif self.pattern_type == "prime":
            return "Busca el siguiente número primo"
        
        return "Observa la relación entre los números"
