"""
Puzzle de patrón de secuencia mejorado
"""

import time
import random
from typing import List, Dict, Any, Optional, Tuple
from utils.config import Config
from .puzzle_base import Puzzle

class PatronSecuenciaPuzzle(Puzzle):
    """Puzzle de patrón de secuencia - adivinar el siguiente número en una secuencia"""

    def __init__(self, difficulty: float = 1.0, config: Config = None):
        super().__init__(difficulty, config)
        self.pattern_type = random.choice(["fibonacci", "arithmetic", "geometric"])
        self.sequence: List[int] = []
        self.player_input_str: str = ""
        self.attempts = 0
        self.feedback_message: Optional[str] = None
        self.feedback_color: Optional[Tuple[int, int, int]] = None
        self.feedback_timer = 0.0
        self.feedback_duration = 3.0
        self.time_limit = 30.0 + (difficulty * 5)

    def setup_puzzle(self):
        """Configurar el puzzle de patrón de secuencia"""
        super().setup_puzzle()
        self.sequence = self._generate_sequence()
        self.player_input_str = ""
        self.attempts = 0
        self.feedback_message = None
        self.feedback_color = None
        self.feedback_timer = 0.0

    def _generate_sequence(self) -> List[int]:
        """Generar secuencia basada en el tipo de patrón"""
        if self.pattern_type == "fibonacci":
            return self._generate_fibonacci()
        elif self.pattern_type == "arithmetic":
            return self._generate_arithmetic()
        elif self.pattern_type == "geometric":
            return self._generate_geometric()
        else:
            return self._generate_fibonacci()

    def _generate_fibonacci(self) -> List[int]:
        """Generar secuencia de Fibonacci"""
        length = int(4 + self.difficulty)
        sequence = [1, 1]
        for i in range(2, length):
            sequence.append(sequence[i-1] + sequence[i-2])
        return sequence

    def _generate_arithmetic(self) -> List[int]:
        """Generar secuencia aritmética"""
        start = random.randint(1, 10)
        step = random.randint(2, 5)
        length = int(4 + self.difficulty)
        return [start + i * step for i in range(length)]

    def _generate_geometric(self) -> List[int]:
        """Generar secuencia geométrica"""
        start = random.randint(1, 5)
        ratio = random.randint(2, 3)
        length = int(4 + self.difficulty)
        return [start * (ratio ** i) for i in range(length)]

    def _calculate_next_number(self) -> int:
        """Calcular el siguiente número en la secuencia"""
        if self.pattern_type == "fibonacci":
            return self.sequence[-1] + self.sequence[-2]
        elif self.pattern_type == "arithmetic":
            step = self.sequence[1] - self.sequence[0]
            return self.sequence[-1] + step
        elif self.pattern_type == "geometric":
            ratio = self.sequence[1] // self.sequence[0]
            return self.sequence[-1] * ratio
        else:
            return self.sequence[-1] + self.sequence[-2]

    def update(self, delta_time: float):
        """Actualizar la lógica del puzzle"""
        super().update(delta_time)
        if self.feedback_timer > 0:
            self.feedback_timer -= delta_time
            if self.feedback_timer <= 0:
                self.feedback_message = None
                self.feedback_color = None

    def handle_input(self, input_data: str) -> bool:
        """Manejar entrada del jugador"""
        if self.completed:
            return False

        if input_data.isdigit():
            self.player_input_str += input_data
            return True
        elif input_data == "BACKSPACE":
            if self.player_input_str:
                self.player_input_str = self.player_input_str[:-1]
            return True
        elif input_data == "ENTER":
            if not self.player_input_str:
                self._show_feedback("¡Ingresa un número antes de presionar ENTER!", self.config.COLORS['error'])
                return False

            try:
                player_answer = int(self.player_input_str)
                self.attempts += 1
                correct_answer = self._calculate_next_number()

                if player_answer == correct_answer:
                    self._show_feedback(f"¡CORRECTO! La respuesta era {correct_answer}", self.config.COLORS['success'])
                    self.complete_puzzle()
                    return True
                else:
                    self._show_feedback(f"Incorrecto. La respuesta correcta era {correct_answer}", self.config.COLORS['error'])
                    self.player_input_str = ""
                    return False
            except ValueError:
                self._show_feedback("Entrada inválida. Solo números.", self.config.COLORS['error'])
                self.player_input_str = ""
                return False
        
        return False

    def _show_feedback(self, message: str, color: Tuple[int, int, int]):
        """Mostrar mensaje de feedback temporalmente"""
        self.feedback_message = message
        self.feedback_color = color
        self.feedback_timer = self.feedback_duration

    def draw_puzzle(self, screen_width: int, screen_height: int):
        """Dibujar el puzzle de patrón de secuencia"""
        import arcade

        # Título
        arcade.draw_text(
            f"PATRÓN DE SECUENCIA - {self.pattern_type.upper()}",
            screen_width // 2,
            screen_height - 50,
            self.config.COLORS['primary'],
            font_size=self.config.FONT_SIZE_LARGE,
            anchor_x="center"
        )

        # Instrucciones detalladas
        arcade.draw_text(
            "Adivina el siguiente número en la secuencia",
            screen_width // 2,
            screen_height - 80,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "Usa las teclas 0-9 para ingresar tu respuesta",
            screen_width // 2,
            screen_height - 110,
            self.config.COLORS['accent'],
            font_size=self.config.FONT_SIZE_SMALL,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "ENTER para enviar | BACKSPACE para borrar",
            screen_width // 2,
            screen_height - 130,
            self.config.COLORS['accent'],
            font_size=self.config.FONT_SIZE_SMALL,
            anchor_x="center"
        )

        # Mostrar secuencia
        sequence_display = " ".join(map(str, self.sequence)) + " ?"
        arcade.draw_text(
            f"Secuencia: {sequence_display}",
            screen_width // 2,
            screen_height // 2 + 50,
            self.config.COLORS['secondary'],
            font_size=self.config.FONT_SIZE_LARGE,
            anchor_x="center"
        )

        # Mostrar entrada del jugador
        arcade.draw_text(
            f"Tu respuesta: {self.player_input_str}",
            screen_width // 2,
            screen_height // 2,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            anchor_x="center"
        )

        # Mostrar feedback temporal
        if self.feedback_message:
            arcade.draw_text(
                self.feedback_message,
                screen_width // 2,
                screen_height // 2 - 50,
                self.feedback_color,
                font_size=self.config.FONT_SIZE_MEDIUM,
                anchor_x="center"
            )

        # Información del puzzle
        self._draw_puzzle_info(screen_width, screen_height)

    def _draw_puzzle_info(self, screen_width: int, screen_height: int):
        """Dibujar información del puzzle"""
        import arcade
        
        # Solo mostrar información básica aquí, el temporizador se maneja en game_scene
        # Tipo de patrón
        arcade.draw_text(
            f"Tipo: {self.pattern_type.title()}",
            20,
            screen_height - 30,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_SMALL
        )
    
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
            return f"Multiplica por {ratio} el último número"
        elif self.pattern_type == "fibonacci":
            return "Suma los dos últimos números"
        else:
            return "Observa el patrón en la secuencia"
