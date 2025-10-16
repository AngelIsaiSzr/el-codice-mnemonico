"""
Gestor de Puzzles del Juego
"""

import random
from typing import Dict, Optional, Any, List
from puzzles.puzzle_base import Puzzle, SimonDicePuzzle, PatronSecuenciaPuzzle, MemoriaEspacialPuzzle
from game.memory_anomalies import AnomalyManager
from game.cognitive_abilities import CognitiveAbilityManager
from utils.config import Config

class PuzzleManager:
    """Gestor principal de puzzles del juego"""
    
    def __init__(self, config: Config):
        self.config = config
        self.current_puzzle: Optional[Puzzle] = None
        self.puzzle_factory = PuzzleFactory(config)
        self.anomaly_manager = AnomalyManager(config)
        self.ability_manager = CognitiveAbilityManager(config)
        
        # Estadísticas del jugador
        self.player_stats = {
            'puzzles_completed': 0,
            'total_score': 0,
            'average_time': 0.0,
            'weak_areas': [],
            'strong_areas': []
        }
        
        # Historial de puzzles
        self.puzzle_history: List[Dict[str, Any]] = []
    
    def create_puzzle(self, puzzle_type: str, difficulty: float = 1.0) -> Optional[Puzzle]:
        """Crear un nuevo puzzle"""
        puzzle = self.puzzle_factory.create_puzzle(puzzle_type, difficulty)
        
        if puzzle:
            # Aplicar anomalías activas
            self._apply_active_anomalies(puzzle)
            
            # Configurar el puzzle
            puzzle.setup_puzzle()
            
            self.current_puzzle = puzzle
            return puzzle
        
        return None
    
    def _apply_active_anomalies(self, puzzle: Puzzle):
        """Aplicar anomalías activas al puzzle"""
        active_anomalies = self.anomaly_manager.get_active_anomalies()
        
        for anomaly_type, anomaly in active_anomalies.items():
            puzzle.add_anomaly(anomaly_type)
            
            # Aplicar efectos específicos
            if anomaly_type == "la_repeticion":
                difficulty_modifier = anomaly.get_difficulty_modifier()
                puzzle.difficulty += difficulty_modifier
    
    def handle_puzzle_input(self, input_data: Any) -> bool:
        """Manejar entrada del puzzle actual"""
        if not self.current_puzzle:
            return False
        
        # Aplicar efectos de habilidades cognitivas
        self._apply_cognitive_abilities()
        
        # Procesar entrada
        result = self.current_puzzle.handle_input(input_data)
        
        if result:
            self._on_puzzle_completed()
        
        return result
    
    def _apply_cognitive_abilities(self):
        """Aplicar efectos de habilidades cognitivas activas"""
        active_abilities = self.ability_manager.get_active_abilities()
        
        for ability_name, ability in active_abilities.items():
            if ability_name == "enfoque":
                # Ralentizar el tiempo del puzzle
                if hasattr(self.current_puzzle, 'time_limit'):
                    self.current_puzzle.time_limit *= 1.5
            elif ability_name == "vision_periferica":
                # Mejorar la visibilidad en puzzles de búsqueda
                pass  # Implementar según el tipo de puzzle
    
    def _on_puzzle_completed(self):
        """Manejar completación del puzzle"""
        if not self.current_puzzle:
            return
        
        # Actualizar estadísticas
        self.player_stats['puzzles_completed'] += 1
        self.player_stats['total_score'] += self.current_puzzle.score
        
        # Calcular tiempo promedio
        puzzle_time = self.config.PUZZLE_TIMEOUT - self.current_puzzle.get_remaining_time()
        total_puzzles = self.player_stats['puzzles_completed']
        current_avg = self.player_stats['average_time']
        self.player_stats['average_time'] = (current_avg * (total_puzzles - 1) + puzzle_time) / total_puzzles
        
        # Guardar en historial
        puzzle_record = {
            'type': type(self.current_puzzle).__name__,
            'difficulty': self.current_puzzle.difficulty,
            'score': self.current_puzzle.score,
            'time': puzzle_time,
            'attempts': self.current_puzzle.attempts,
            'hints_used': self.current_puzzle.hints_used,
            'anomalies': self.current_puzzle.active_anomalies.copy()
        }
        self.puzzle_history.append(puzzle_record)
        
        # Analizar rendimiento para personalización adaptativa
        self._analyze_performance(puzzle_record)
        
        # Intentar activar anomalías
        self.anomaly_manager.try_activate_anomaly(self.current_puzzle.difficulty)
        
        # Desbloquear habilidades si es necesario
        self._check_ability_unlocks()
    
    def _analyze_performance(self, puzzle_record: Dict[str, Any]):
        """Analizar rendimiento para personalización adaptativa"""
        puzzle_type = puzzle_record['type']
        
        # Analizar áreas débiles
        if puzzle_record['attempts'] > 2 or puzzle_record['hints_used'] > 1:
            if puzzle_type not in self.player_stats['weak_areas']:
                self.player_stats['weak_areas'].append(puzzle_type)
        
        # Analizar áreas fuertes
        if puzzle_record['score'] > 80 and puzzle_record['attempts'] <= 1:
            if puzzle_type not in self.player_stats['strong_areas']:
                self.player_stats['strong_areas'].append(puzzle_type)
    
    def _check_ability_unlocks(self):
        """Verificar si se deben desbloquear nuevas habilidades"""
        completed_puzzles = self.player_stats['puzzles_completed']
        
        if completed_puzzles >= 5 and "vision_periferica" not in self.ability_manager.unlocked_abilities:
            self.ability_manager.unlock_ability("vision_periferica")
        elif completed_puzzles >= 10 and "enfoque" not in self.ability_manager.unlocked_abilities:
            self.ability_manager.unlock_ability("enfoque")
    
    def get_adaptive_difficulty(self, puzzle_type: str) -> float:
        """Obtener dificultad adaptativa para un tipo de puzzle"""
        base_difficulty = 1.0
        
        # Aumentar dificultad si es un área fuerte
        if puzzle_type in self.player_stats['strong_areas']:
            base_difficulty += 0.3
        
        # Disminuir dificultad si es un área débil
        if puzzle_type in self.player_stats['weak_areas']:
            base_difficulty -= 0.2
        
        # Ajustar basado en progreso general
        completed_puzzles = self.player_stats['puzzles_completed']
        base_difficulty += completed_puzzles * 0.05
        
        return max(0.5, min(3.0, base_difficulty))
    
    def get_next_puzzle_type(self) -> str:
        """Obtener el siguiente tipo de puzzle basado en análisis adaptativo"""
        # Priorizar áreas débiles
        if self.player_stats['weak_areas']:
            return random.choice(self.player_stats['weak_areas'])
        
        # Seleccionar aleatoriamente de tipos disponibles
        available_types = ["simon_dice", "patron_secuencia", "memoria_espacial", "logica_simbolos", "busqueda_patrones"]
        return random.choice(available_types)
    
    def update(self, delta_time: float):
        """Actualizar el gestor de puzzles"""
        # Actualizar anomalías
        self.anomaly_manager.update_anomalies(delta_time)
        
        # Actualizar habilidades cognitivas
        self.ability_manager.update_abilities(delta_time)
        
        # Actualizar puzzle actual
        if self.current_puzzle and not self.current_puzzle.completed:
            if self.current_puzzle.is_time_up():
                self._on_puzzle_failed()
    
    def _on_puzzle_failed(self):
        """Manejar fallo del puzzle"""
        if self.current_puzzle:
            # Registrar fallo
            puzzle_record = {
                'type': type(self.current_puzzle).__name__,
                'difficulty': self.current_puzzle.difficulty,
                'score': 0,
                'time': self.config.PUZZLE_TIMEOUT,
                'attempts': self.current_puzzle.attempts,
                'hints_used': self.current_puzzle.hints_used,
                'anomalies': self.current_puzzle.active_anomalies.copy(),
                'failed': True
            }
            self.puzzle_history.append(puzzle_record)
            
            # Marcar como área débil
            puzzle_type = puzzle_record['type']
            if puzzle_type not in self.player_stats['weak_areas']:
                self.player_stats['weak_areas'].append(puzzle_type)
    
    def get_puzzle_info(self) -> Dict[str, Any]:
        """Obtener información del puzzle actual"""
        if not self.current_puzzle:
            return {}
        
        return {
            'type': type(self.current_puzzle).__name__,
            'difficulty': self.current_puzzle.difficulty,
            'completed': self.current_puzzle.completed,
            'remaining_time': self.current_puzzle.get_remaining_time(),
            'timer_active': self.current_puzzle.is_timer_active(),
            'progress': self.current_puzzle.current_step / self.current_puzzle.total_steps if self.current_puzzle.total_steps > 0 else 0,
            'active_anomalies': self.current_puzzle.active_anomalies.copy(),
            'active_abilities': list(self.ability_manager.get_active_abilities().keys())
        }

class PuzzleFactory:
    """Factory para crear puzzles"""
    
    def __init__(self, config: Config):
        self.config = config
        self.puzzle_classes = {
            'simon_dice': SimonDicePuzzle,
            'patron_secuencia': PatronSecuenciaPuzzle,
            'memoria_espacial': MemoriaEspacialPuzzle,
            # TODO: Agregar más tipos de puzzles
        }
    
    def create_puzzle(self, puzzle_type: str, difficulty: float = 1.0) -> Optional[Puzzle]:
        """Crear un puzzle del tipo especificado"""
        if puzzle_type in self.puzzle_classes:
            puzzle_class = self.puzzle_classes[puzzle_type]
            return puzzle_class(difficulty, self.config)
        
        return None
    
    def get_available_puzzle_types(self) -> List[str]:
        """Obtener tipos de puzzles disponibles"""
        return list(self.puzzle_classes.keys())
