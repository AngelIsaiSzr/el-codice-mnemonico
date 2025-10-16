"""
Sistema de Habilidades Cognitivas
"""

import time
from typing import Dict, Any
from utils.config import Config

class CognitiveAbility:
    """Clase base para habilidades cognitivas"""
    
    def __init__(self, name: str, description: str, cooldown: float = 0):
        self.name = name
        self.description = description
        self.cooldown = cooldown
        self.last_used = 0
        self.active = False
        self.duration = 0
        self.start_time = 0
    
    def can_use(self) -> bool:
        """Verificar si la habilidad puede ser usada"""
        return time.time() - self.last_used >= self.cooldown
    
    def activate(self) -> bool:
        """Activar la habilidad"""
        if not self.can_use():
            return False
        
        self.active = True
        self.start_time = time.time()
        self.last_used = time.time()
        return True
    
    def deactivate(self):
        """Desactivar la habilidad"""
        self.active = False
    
    def is_expired(self) -> bool:
        """Verificar si la habilidad ha expirado"""
        if not self.active:
            return False
        return time.time() - self.start_time >= self.duration
    
    def update(self, delta_time: float):
        """Actualizar el estado de la habilidad"""
        if self.active and self.is_expired():
            self.deactivate()

class PalacioMental(CognitiveAbility):
    """Habilidad para almacenar información temporalmente"""
    
    def __init__(self, config: Config):
        super().__init__(
            "Palacio Mental",
            "Almacena información temporalmente en la interfaz",
            cooldown=10.0
        )
        self.config = config
        self.stored_items: Dict[str, Any] = {}
        self.max_capacity = config.PALACIO_MENTAL_CAPACITY
    
    def store_item(self, key: str, value: Any) -> bool:
        """Almacenar un elemento"""
        if len(self.stored_items) >= self.max_capacity:
            return False
        
        self.stored_items[key] = value
        return True
    
    def retrieve_item(self, key: str) -> Any:
        """Recuperar un elemento"""
        return self.stored_items.pop(key, None)
    
    def has_item(self, key: str) -> bool:
        """Verificar si tiene un elemento"""
        return key in self.stored_items
    
    def clear_items(self):
        """Limpiar todos los elementos almacenados"""
        self.stored_items.clear()

class VisionPeriferica(CognitiveAbility):
    """Habilidad para ampliar el campo de visión"""
    
    def __init__(self, config: Config):
        super().__init__(
            "Visión Periférica",
            "Amplía brevemente el campo de visión en puzzles de búsqueda",
            cooldown=15.0
        )
        self.config = config
        self.duration = config.VISION_PERIFERICA_DURATION
        self.vision_multiplier = 2.0

class Enfoque(CognitiveAbility):
    """Habilidad para ralentizar el tiempo"""
    
    def __init__(self, config: Config):
        super().__init__(
            "Enfoque",
            "Ralentiza el tiempo por unos segundos",
            cooldown=20.0
        )
        self.config = config
        self.duration = config.ENFOQUE_DURATION
        self.time_slow_factor = 0.5

class CognitiveAbilityManager:
    """Gestor de habilidades cognitivas del jugador"""
    
    def __init__(self, config: Config):
        self.config = config
        self.abilities: Dict[str, CognitiveAbility] = {}
        
        # Inicializar habilidades
        self.abilities["palacio_mental"] = PalacioMental(config)
        self.abilities["vision_periferica"] = VisionPeriferica(config)
        self.abilities["enfoque"] = Enfoque(config)
        
        # Habilidades desbloqueadas
        self.unlocked_abilities = {"palacio_mental"}  # Empezar con una habilidad
    
    def unlock_ability(self, ability_name: str) -> bool:
        """Desbloquear una nueva habilidad"""
        if ability_name in self.abilities and ability_name not in self.unlocked_abilities:
            self.unlocked_abilities.add(ability_name)
            return True
        return False
    
    def use_ability(self, ability_name: str) -> bool:
        """Usar una habilidad"""
        if (ability_name in self.unlocked_abilities and 
            ability_name in self.abilities):
            return self.abilities[ability_name].activate()
        return False
    
    def get_ability(self, ability_name: str) -> CognitiveAbility:
        """Obtener una habilidad por nombre"""
        return self.abilities.get(ability_name)
    
    def update_abilities(self, delta_time: float):
        """Actualizar todas las habilidades"""
        for ability in self.abilities.values():
            ability.update(delta_time)
    
    def get_active_abilities(self) -> Dict[str, CognitiveAbility]:
        """Obtener habilidades activas"""
        return {name: ability for name, ability in self.abilities.items() 
                if ability.active}
    
    def get_available_abilities(self) -> Dict[str, CognitiveAbility]:
        """Obtener habilidades disponibles para usar"""
        return {name: ability for name, ability in self.abilities.items() 
                if name in self.unlocked_abilities and ability.can_use()}
