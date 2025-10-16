"""
Sistema de Mapa Mental Procedural
"""

import random
import math
from typing import List, Dict, Tuple
from utils.config import Config

class MemoryNode:
    """Nodo del mapa mental que representa un recuerdo/puzzle"""
    
    def __init__(self, node_id: int, x: float, y: float):
        self.id = node_id
        self.x = x
        self.y = y
        self.connections: List[int] = []
        self.puzzle_type = None
        self.completed = False
        self.difficulty = 1.0
        self.story_fragment = ""
        
    def add_connection(self, other_node_id: int):
        """Agregar conexión con otro nodo"""
        if other_node_id not in self.connections:
            self.connections.append(other_node_id)
    
    def is_connected_to(self, other_node_id: int) -> bool:
        """Verificar si está conectado a otro nodo"""
        return other_node_id in self.connections

class MemoryMap:
    """Mapa mental procedural del juego"""
    
    def __init__(self, config: Config):
        self.config = config
        self.nodes: Dict[int, MemoryNode] = {}
        self.start_node_id = None
        self.current_node_id = None
        self.completed_nodes = set()
        
        # Tipos de puzzles disponibles (solo los implementados)
        self.puzzle_types = [
            "simon_dice",
            "patron_secuencia", 
            "memoria_espacial"
        ]
        
        # Fragmentos de historia
        self.story_fragments = [
            "En los anales del tiempo, cuando la memoria era sagrada...",
            "Los antiguos archivistas guardaban secretos en sus mentes...",
            "Cada símbolo cuenta una historia perdida...",
            "La sabiduría se desvanece como la niebla al amanecer...",
            "Solo quien domina la memoria puede restaurar el códice..."
        ]
    
    def generate_map(self, difficulty_level: int = 1):
        """Generar un nuevo mapa mental procedural"""
        self.nodes.clear()
        self.completed_nodes.clear()
        
        # Determinar número de nodos basado en dificultad
        num_nodes = min(
            self.config.MAP_NODES_MAX,
            self.config.MAP_NODES_MIN + difficulty_level * 2
        )
        
        # Generar nodos en posiciones espirales
        self._generate_node_positions(num_nodes)
        
        # Conectar nodos para crear un grafo conectado
        self._connect_nodes()
        
        # Asignar tipos de puzzles y fragmentos de historia
        self._assign_puzzle_types()
        
        # Establecer nodo inicial
        self.start_node_id = 0
        self.current_node_id = self.start_node_id
    
    def _generate_node_positions(self, num_nodes: int):
        """Generar posiciones de nodos en patrón espiral"""
        center_x = self.config.SCREEN_WIDTH // 2
        center_y = self.config.SCREEN_HEIGHT // 2
        
        for i in range(num_nodes):
            if i == 0:
                # Nodo central
                x, y = center_x, center_y
            else:
                # Patrón espiral
                angle = (i - 1) * (2 * math.pi / (num_nodes - 1))
                radius = 150 + (i - 1) * 30
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
            
            node = MemoryNode(i, x, y)
            self.nodes[i] = node
    
    def _connect_nodes(self):
        """Conectar nodos para crear un camino ordenado simple"""
        node_ids = list(self.nodes.keys())
        
        # Crear conexiones ordenadas: 0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6
        for i in range(len(node_ids) - 1):
            current_id = node_ids[i]
            next_id = node_ids[i + 1]
            
            self.nodes[current_id].add_connection(next_id)
            self.nodes[next_id].add_connection(current_id)
    
    def _assign_puzzle_types(self):
        """Asignar tipos de puzzles y fragmentos de historia a los nodos"""
        for node in self.nodes.values():
            node.puzzle_type = random.choice(self.puzzle_types)
            node.story_fragment = random.choice(self.story_fragments)
            node.difficulty = random.uniform(0.8, 1.5)
    
    def get_available_nodes(self) -> List[MemoryNode]:
        """Obtener nodos disponibles para jugar"""
        available = []
        
        # El nodo inicial siempre está disponible
        if self.start_node_id is not None and self.start_node_id in self.nodes:
            start_node = self.nodes[self.start_node_id]
            if not start_node.completed:
                available.append(start_node)
        
        # Los nodos conectados a nodos completados están disponibles
        for node in self.nodes.values():
            if node.completed:
                # Agregar nodos conectados que no estén completados
                for connected_id in node.connections:
                    if connected_id in self.nodes:
                        connected_node = self.nodes[connected_id]
                        if not connected_node.completed and connected_node not in available:
                            available.append(connected_node)
        
        return available
    
    def complete_node(self, node_id: int):
        """Marcar un nodo como completado"""
        if node_id in self.nodes:
            self.nodes[node_id].completed = True
            self.completed_nodes.add(node_id)
            
            # Actualizar nodo actual si es necesario
            if node_id == self.current_node_id:
                available = self.get_available_nodes()
                if available:
                    self.current_node_id = available[0].id
    
    def get_progress(self) -> float:
        """Obtener progreso del mapa (0.0 a 1.0)"""
        if not self.nodes:
            return 0.0
        return len(self.completed_nodes) / len(self.nodes)
    
    def is_map_complete(self) -> bool:
        """Verificar si el mapa está completo"""
        return len(self.completed_nodes) == len(self.nodes)
