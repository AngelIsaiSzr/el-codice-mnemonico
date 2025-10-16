"""
Sistema de Anomalías de la Memoria
"""

import random
import time
from typing import List, Dict, Any
from utils.config import Config

class MemoryAnomaly:
    """Clase base para anomalías de la memoria"""
    
    def __init__(self, name: str, description: str, duration: float = 0):
        self.name = name
        self.description = description
        self.duration = duration
        self.active = False
        self.start_time = 0
        self.intensity = 1.0
    
    def activate(self, intensity: float = 1.0):
        """Activar la anomalía"""
        self.active = True
        self.start_time = time.time()
        self.intensity = intensity
    
    def deactivate(self):
        """Desactivar la anomalía"""
        self.active = False
    
    def is_expired(self) -> bool:
        """Verificar si la anomalía ha expirado"""
        if not self.active or self.duration == 0:
            return False
        return time.time() - self.start_time >= self.duration
    
    def update(self, delta_time: float):
        """Actualizar el estado de la anomalía"""
        if self.active and self.is_expired():
            self.deactivate()

class ElOlvido(MemoryAnomaly):
    """Anomalía que oscurece partes del tablero"""
    
    def __init__(self):
        super().__init__(
            "El Olvido",
            "Oscurece partes del tablero temporalmente",
            duration=8.0
        )
        self.obscured_areas: List[Dict[str, Any]] = []
    
    def activate(self, intensity: float = 1.0):
        super().activate(intensity)
        # Generar áreas oscurecidas basadas en la intensidad
        num_areas = int(2 + intensity * 3)
        self.obscured_areas = []
        
        for _ in range(num_areas):
            area = {
                'x': random.randint(100, 1100),
                'y': random.randint(100, 700),
                'radius': random.randint(50, 150),
                'opacity': 0.7 + intensity * 0.3
            }
            self.obscured_areas.append(area)
    
    def get_obscured_areas(self) -> List[Dict[str, Any]]:
        """Obtener áreas oscurecidas"""
        return self.obscured_areas if self.active else []

class ElRuido(MemoryAnomaly):
    """Anomalía que introduce información falsa"""
    
    def __init__(self):
        super().__init__(
            "El Ruido",
            "Introduce información falsa o distractora",
            duration=6.0
        )
        self.false_information: List[str] = []
        self.distraction_level = 0.0
    
    def activate(self, intensity: float = 1.0):
        super().activate(intensity)
        self.distraction_level = intensity
        
        # Generar información falsa
        false_items = [
            "Símbolo incorrecto: ▲",
            "Número falso: 42",
            "Patrón erróneo: ●■▲",
            "Secuencia falsa: 1,2,3,5",
            "Color incorrecto: Rojo",
            "Dirección falsa: Izquierda"
        ]
        
        num_false = int(1 + intensity * 2)
        self.false_information = random.sample(false_items, min(num_false, len(false_items)))
    
    def get_false_information(self) -> List[str]:
        """Obtener información falsa"""
        return self.false_information if self.active else []
    
    def should_show_distraction(self) -> bool:
        """Verificar si debe mostrar distracción"""
        if not self.active:
            return False
        return random.random() < self.distraction_level * 0.3

class LaRepeticion(MemoryAnomaly):
    """Anomalía que obliga a repetir puzzles más difíciles"""
    
    def __init__(self):
        super().__init__(
            "La Repetición",
            "Obliga a resolver una versión más difícil de un puzzle completado",
            duration=0  # Duración indefinida hasta completar
        )
        self.original_puzzle_type = ""
        self.increased_difficulty = 0.0
        self.attempts_made = 0
    
    def activate(self, intensity: float = 1.0, puzzle_type: str = ""):
        super().activate(intensity)
        self.original_puzzle_type = puzzle_type
        self.increased_difficulty = intensity * 0.5
        self.attempts_made = 0
    
    def get_difficulty_modifier(self) -> float:
        """Obtener modificador de dificultad"""
        return self.increased_difficulty if self.active else 0.0
    
    def increment_attempts(self):
        """Incrementar intentos realizados"""
        self.attempts_made += 1
    
    def should_deactivate(self) -> bool:
        """Verificar si debe desactivarse"""
        return self.attempts_made >= 3  # Máximo 3 intentos

class AnomalyManager:
    """Gestor de anomalías de la memoria"""
    
    def __init__(self, config: Config):
        self.config = config
        self.active_anomalies: Dict[str, MemoryAnomaly] = {}
        self.anomaly_types = {
            "el_olvido": ElOlvido,
            "el_ruido": ElRuido,
            "la_repeticion": LaRepeticion
        }
        
        # Probabilidades de activación
        self.activation_probabilities = {
            "el_olvido": 0.3,
            "el_ruido": 0.4,
            "la_repeticion": 0.2
        }
        
        # Tiempo entre activaciones
        self.last_activation_time = 0
        self.min_activation_interval = 30.0  # segundos
    
    def can_activate_anomaly(self) -> bool:
        """Verificar si puede activar una anomalía"""
        return time.time() - self.last_activation_time >= self.min_activation_interval
    
    def try_activate_anomaly(self, difficulty_level: float = 1.0) -> bool:
        """Intentar activar una anomalía aleatoria"""
        if not self.can_activate_anomaly():
            return False
        
        # Seleccionar anomalía basada en probabilidades
        anomaly_type = self._select_anomaly_type()
        if not anomaly_type:
            return False
        
        # Crear y activar la anomalía
        anomaly_class = self.anomaly_types[anomaly_type]
        anomaly = anomaly_class()
        
        # Calcular intensidad basada en dificultad
        intensity = min(2.0, difficulty_level * 0.5 + random.uniform(0.5, 1.0))
        
        anomaly.activate(intensity)
        self.active_anomalies[anomaly_type] = anomaly
        self.last_activation_time = time.time()
        
        return True
    
    def _select_anomaly_type(self) -> str:
        """Seleccionar tipo de anomalía basado en probabilidades"""
        rand = random.random()
        cumulative = 0.0
        
        for anomaly_type, probability in self.activation_probabilities.items():
            cumulative += probability
            if rand <= cumulative:
                return anomaly_type
        
        return ""
    
    def activate_specific_anomaly(self, anomaly_type: str, intensity: float = 1.0) -> bool:
        """Activar una anomalía específica"""
        if anomaly_type not in self.anomaly_types:
            return False
        
        if anomaly_type in self.active_anomalies:
            return False  # Ya está activa
        
        anomaly_class = self.anomaly_types[anomaly_type]
        anomaly = anomaly_class()
        anomaly.activate(intensity)
        
        self.active_anomalies[anomaly_type] = anomaly
        return True
    
    def deactivate_anomaly(self, anomaly_type: str):
        """Desactivar una anomalía específica"""
        if anomaly_type in self.active_anomalies:
            self.active_anomalies[anomaly_type].deactivate()
            del self.active_anomalies[anomaly_type]
    
    def update_anomalies(self, delta_time: float):
        """Actualizar todas las anomalías activas"""
        anomalies_to_remove = []
        
        for anomaly_type, anomaly in self.active_anomalies.items():
            anomaly.update(delta_time)
            
            # Verificar si debe ser removida
            if not anomaly.active or anomaly.is_expired():
                anomalies_to_remove.append(anomaly_type)
        
        # Remover anomalías expiradas
        for anomaly_type in anomalies_to_remove:
            del self.active_anomalies[anomaly_type]
    
    def get_active_anomalies(self) -> Dict[str, MemoryAnomaly]:
        """Obtener anomalías activas"""
        return {name: anomaly for name, anomaly in self.active_anomalies.items() 
                if anomaly.active}
    
    def has_anomaly(self, anomaly_type: str) -> bool:
        """Verificar si tiene una anomalía específica activa"""
        return (anomaly_type in self.active_anomalies and 
                self.active_anomalies[anomaly_type].active)
    
    def get_anomaly_effects(self) -> Dict[str, Any]:
        """Obtener efectos de todas las anomalías activas"""
        effects = {}
        
        for anomaly_type, anomaly in self.active_anomalies.items():
            if anomaly.active:
                if anomaly_type == "el_olvido":
                    effects["obscured_areas"] = anomaly.get_obscured_areas()
                elif anomaly_type == "el_ruido":
                    effects["false_information"] = anomaly.get_false_information()
                    effects["show_distraction"] = anomaly.should_show_distraction()
                elif anomaly_type == "la_repeticion":
                    effects["difficulty_modifier"] = anomaly.get_difficulty_modifier()
        
        return effects
