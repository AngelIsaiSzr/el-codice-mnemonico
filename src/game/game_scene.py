"""
Escena Principal del Juego
"""

import arcade
from typing import Optional, List
from game.memory_map import MemoryMap
from game.puzzle_manager import PuzzleManager
from game.cognitive_abilities import CognitiveAbilityManager
from game.memory_anomalies import AnomalyManager
from utils.config import Config

class GameScene:
    """Escena principal del juego El Códice Mnemónico"""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Sistemas principales
        self.memory_map = MemoryMap(config)
        self.puzzle_manager = PuzzleManager(config)
        self.ability_manager = self.puzzle_manager.ability_manager
        self.anomaly_manager = self.puzzle_manager.anomaly_manager
        
        # Estado del juego
        self.game_state = "map_view"  # map_view, puzzle_view, story_view, level_complete
        self.current_node = None
        self.story_text = ""
        self.show_story = False
        self.level_complete = False
        self.selected_pause_button = 0  # 0: Reanudar, 1: Salir al mapa
        
        # UI
        self.ui_elements = {}
        self.selected_ability = None
        
        # Inicializar el juego
        self.initialize_game()
    
    def on_key_press(self, key, modifiers):
        """Manejar entrada de teclado principal"""
        if self.game_state == "map_view":
            self.handle_map_input(key, modifiers)
        elif self.game_state == "puzzle_view":
            self.handle_puzzle_input(key, modifiers)
        elif self.game_state == "story_view":
            self.handle_story_input(key, modifiers)
        elif self.game_state == "pause":
            # La navegación de pausa ahora se maneja en GameWindow
            pass
        elif self.game_state == "level_complete":
            self.handle_level_complete_input(key, modifiers)
        elif self.game_state == "construction":
            self.handle_construction_input(key, modifiers)
    
    def on_update(self, delta_time):
        """Actualizar la lógica del juego"""
        if self.game_state == "puzzle_view" and self.puzzle_manager.current_puzzle:
            self.puzzle_manager.current_puzzle.update(delta_time)
    
    def check_level_completion(self):
        """Verificar si todos los nodos están completados"""
        completed_nodes = sum(1 for node in self.memory_map.nodes.values() if node.completed)
        total_nodes = len(self.memory_map.nodes)
        return completed_nodes == total_nodes and total_nodes > 0
    
    def initialize_game(self):
        """Inicializar el juego"""
        # Generar mapa inicial
        self.memory_map.generate_map(difficulty_level=1)
        
        # Configurar nodo inicial
        if self.memory_map.start_node_id is not None:
            self.current_node = self.memory_map.nodes[self.memory_map.start_node_id]
        else:
            # Si no hay nodo inicial, usar el primer nodo disponible
            available_nodes = self.memory_map.get_available_nodes()
            if available_nodes:
                self.current_node = available_nodes[0]
        
        # Configurar UI
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar elementos de la interfaz"""
        # Botones de habilidades
        self.ui_elements['ability_buttons'] = []
        
        # Información del mapa
        self.ui_elements['map_info'] = {
            'progress': 0.0,
            'completed_nodes': 0,
            'total_nodes': len(self.memory_map.nodes)
        }
    
    def on_key_press(self, key, modifiers):
        """Manejar teclas presionadas"""
        if self.game_state == "map_view":
            self.handle_map_input(key, modifiers)
        elif self.game_state == "puzzle_view":
            self.handle_puzzle_input(key, modifiers)
        elif self.game_state == "story_view":
            self.handle_story_input(key, modifiers)
    
    def handle_map_input(self, key, modifiers):
        """Manejar entrada en vista del mapa"""
        if key == arcade.key.SPACE:
            # Seleccionar nodo actual
            if self.current_node:
                self.start_puzzle(self.current_node)
        elif key == arcade.key.ESCAPE:
            # Volver al menú principal
            self.return_to_main_menu()
        elif key == arcade.key.LEFT:
            self.move_to_previous_node()
        elif key == arcade.key.RIGHT:
            self.move_to_next_node()
    
    def handle_puzzle_input(self, key, modifiers):
        """Manejar entrada en vista de puzzle"""
        if key == arcade.key.ESCAPE:
            # Mostrar pantalla de pausa - pausar timer
            if self.puzzle_manager.current_puzzle:
                self.puzzle_manager.current_puzzle.pause_timer()
            self.game_state = "pause"
        elif key == arcade.key.H:
            # Usar pista
            if self.puzzle_manager.current_puzzle:
                hint = self.puzzle_manager.current_puzzle.get_hint()
                self.show_hint(hint)
        else:
            # Manejar entrada específica por tipo de puzzle
            if self.puzzle_manager.current_puzzle:
                puzzle_type = self.puzzle_manager.current_puzzle.__class__.__name__
                
                if puzzle_type == "SimonDicePuzzle":
                    # Mapear teclas numéricas a símbolos para Simón Dice
                    symbol_map = {
                        arcade.key.KEY_1: '▲', arcade.key.KEY_2: '●', arcade.key.KEY_3: '■',
                        arcade.key.KEY_4: '★', arcade.key.KEY_5: '◆', arcade.key.KEY_6: '▼'
                    }
                    if key in symbol_map:
                        self.puzzle_manager.handle_puzzle_input(symbol_map[key])
                
                elif puzzle_type == "PatronSecuenciaPuzzle":
                    # Manejar entrada numérica y BACKSPACE/ENTER para Patrón de Secuencia
                    if key >= arcade.key.KEY_0 and key <= arcade.key.KEY_9:
                        digit = str(key - arcade.key.KEY_0)
                        self.puzzle_manager.handle_puzzle_input(digit)
                    elif key == arcade.key.BACKSPACE:
                        self.puzzle_manager.handle_puzzle_input("BACKSPACE")
                    elif key == arcade.key.ENTER:
                        self.puzzle_manager.handle_puzzle_input("ENTER")
                
                elif puzzle_type == "MemoriaEspacialPuzzle":
                    # Manejar entrada numérica para Memoria Espacial (solo 1-4)
                    if key >= arcade.key.KEY_1 and key <= arcade.key.KEY_4:
                        digit = str(key - arcade.key.KEY_0)
                        self.puzzle_manager.handle_puzzle_input(digit)
                    elif key == arcade.key.BACKSPACE:
                        self.puzzle_manager.handle_puzzle_input("BACKSPACE")
    
    def handle_story_input(self, key, modifiers):
        """Manejar entrada en vista de historia"""
        if key == arcade.key.SPACE or key == arcade.key.ENTER:
            # Reanudar música de fondo antes de volver al mapa
            self.resume_background_music()
            self.game_state = "map_view"
    
    def handle_level_complete_input(self, key, modifiers):
        """Manejar entrada en pantalla de nivel completado"""
        if key == arcade.key.S:
            # Continuar al siguiente nivel
            self.show_construction_message()
        elif key == arcade.key.N:
            # Volver al menú principal
            self.game_state = "menu"
    
    def show_construction_message(self):
        """Mostrar mensaje de construcción para el siguiente nivel"""
        self.game_state = "construction"
    
    def handle_construction_input(self, key, modifiers):
        """Manejar entrada en pantalla de construcción"""
        if key == arcade.key.SPACE or key == arcade.key.ENTER:
            self.game_state = "menu"
    
    def start_puzzle(self, node):
        """Iniciar un puzzle en el nodo especificado"""
        if not node:
            print("Error: No hay nodo seleccionado")
            return
        
        # Si el nodo ya está completado, mostrar mensaje
        if node.completed:
            self.story_text = f"El nodo {node.id} ya está completado. Selecciona otro nodo."
            self.show_story = True
            self.game_state = "story_view"
            return
        
        # Verificar si el nodo está disponible
        if not self._is_node_available(node):
            # Mostrar mensaje de nodo bloqueado
            self.story_text = f"El nodo {node.id} está bloqueado. Completa otros nodos primero para desbloquearlo."
            self.show_story = True
            self.game_state = "story_view"
            return
        
        print(f"Iniciando puzzle en nodo {node.id}: {node.puzzle_type}")
        
        # Crear puzzle basado en el tipo del nodo
        puzzle_type = node.puzzle_type
        difficulty = node.difficulty
        
        # Aplicar dificultad adaptativa
        adaptive_difficulty = self.puzzle_manager.get_adaptive_difficulty(puzzle_type)
        final_difficulty = difficulty * adaptive_difficulty
        
        # Crear el puzzle
        puzzle = self.puzzle_manager.create_puzzle(puzzle_type, final_difficulty)
        
        if puzzle:
            print(f"Puzzle creado exitosamente: {puzzle_type}")
            self.game_state = "puzzle_view"
            self.current_node = node
        else:
            print(f"Error: No se pudo crear el puzzle {puzzle_type}")
            self.story_text = f"Error al crear el puzzle {puzzle_type}. Inténtalo de nuevo."
            self.show_story = True
            self.game_state = "story_view"
    
    def move_to_previous_node(self):
        """Mover al nodo anterior disponible"""
        available_nodes = self.memory_map.get_available_nodes()
        if not available_nodes:
            return
        
        # Si no hay nodo actual, usar el primero
        if not self.current_node:
            self.current_node = available_nodes[0]
            return
        
        # Buscar el índice del nodo actual
        try:
            current_index = available_nodes.index(self.current_node)
            previous_index = (current_index - 1) % len(available_nodes)
            self.current_node = available_nodes[previous_index]
        except ValueError:
            # Si el nodo actual no está en disponibles, usar el primero
            self.current_node = available_nodes[0]
    
    def move_to_next_node(self):
        """Mover al siguiente nodo disponible"""
        available_nodes = self.memory_map.get_available_nodes()
        if not available_nodes:
            return
        
        # Si no hay nodo actual, usar el primero
        if not self.current_node:
            self.current_node = available_nodes[0]
            return
        
        # Buscar el índice del nodo actual
        try:
            current_index = available_nodes.index(self.current_node)
            next_index = (current_index + 1) % len(available_nodes)
            self.current_node = available_nodes[next_index]
        except ValueError:
            # Si el nodo actual no está en disponibles, usar el primero
            self.current_node = available_nodes[0]
    
    def show_ability_menu(self):
        """Mostrar menú de habilidades"""
        # TODO: Implementar menú de habilidades
        pass
    
    def show_hint(self, hint_text: str):
        """Mostrar una pista"""
        # TODO: Implementar sistema de pistas
        pass
    
    def on_update(self, delta_time: float):
        """Actualizar la lógica del juego"""
        # Actualizar sistemas
        self.puzzle_manager.update(delta_time)
        
        # Verificar si se completó un puzzle
        if (self.game_state == "puzzle_view" and 
            self.puzzle_manager.current_puzzle and 
            self.puzzle_manager.current_puzzle.completed):
            self.on_puzzle_completed()
        
        # Verificar si se falló un puzzle (tiempo agotado)
        if (self.game_state == "puzzle_view" and 
            self.puzzle_manager.current_puzzle and 
            self.puzzle_manager.current_puzzle.is_time_up() and 
            not self.puzzle_manager.current_puzzle.completed):
            self.on_puzzle_failed()
        
        # Actualizar información del mapa
        self.ui_elements['map_info']['progress'] = self.memory_map.get_progress()
        self.ui_elements['map_info']['completed_nodes'] = len(self.memory_map.completed_nodes)
    
    def on_puzzle_completed(self):
        """Manejar completación de puzzle"""
        if not self.current_node:
            return
        
        # Completar el nodo
        self.memory_map.complete_node(self.current_node.id)
        
        # Mostrar fragmento de historia
        self.story_text = self.current_node.story_fragment
        self.show_story = True
        self.game_state = "story_view"
        
        # Reproducir música de victoria
        self.play_victory_music()
        
        # Verificar si se completó el mapa
        if self.memory_map.is_map_complete():
            self.on_map_completed()
    
    def on_puzzle_failed(self):
        """Manejar fallo de puzzle"""
        if not self.current_node:
            return
        
        # Mostrar mensaje de fallo
        self.story_text = f"¡Tiempo agotado! El puzzle '{self.current_node.puzzle_type}' ha fallado. Inténtalo de nuevo."
        self.show_story = True
        self.game_state = "story_view"
        
        # Reproducir música de derrota
        self.play_defeat_music()
        
        # Limpiar el puzzle actual
        self.puzzle_manager.current_puzzle = None
    
    def on_map_completed(self):
        """Manejar completación del mapa"""
        self.level_complete = True
        self.game_state = "level_complete"
    
    def draw(self):
        """Dibujar la escena actual"""
        if self.game_state == "map_view":
            self.draw_map_view()
        elif self.game_state == "puzzle_view":
            self.draw_puzzle_view()
        elif self.game_state == "story_view":
            self.draw_story_view()
        elif self.game_state == "pause":
            self.draw_pause_view()
        elif self.game_state == "level_complete":
            self.draw_level_complete_view()
        elif self.game_state == "construction":
            self.draw_construction_view()
    
    def draw_map_view(self):
        """Dibujar vista del mapa mental con estilo de ruinas antiguas"""
        # Fondo atmosférico con gradiente
        self._draw_atmospheric_background(all_corners=False)
        
        # Dibujar efectos de iluminación
        self._draw_lighting_effects(all_corners=False)
        
        # Dibujar nodos del mapa
        for node in self.memory_map.nodes.values():
            self.draw_memory_node(node)
        
        # Dibujar conexiones
        self.draw_connections()
        
        # Dibujar UI del mapa
        self.draw_map_ui()
    
    def _draw_atmospheric_background(self, all_corners=False):
        """Dibujar fondo atmosférico de ruinas antiguas"""
        import arcade
        
        # Fondo base con gradiente
        arcade.draw_lrbt_rectangle_filled(
            0, self.config.SCREEN_WIDTH, 0, self.config.SCREEN_HEIGHT,
            self.config.COLORS['background']
        )
        
        # Efectos de piedra antigua
        for i in range(0, self.config.SCREEN_WIDTH, 100):
            for j in range(0, self.config.SCREEN_HEIGHT, 100):
                # Textura de piedra sutil
                stone_color = (
                    self.config.COLORS['stone'][0] + (i % 20) - 10,
                    self.config.COLORS['stone'][1] + (j % 20) - 10,
                    self.config.COLORS['stone'][2] + ((i+j) % 20) - 10
                )
                arcade.draw_lrbt_rectangle_filled(
                    i, i + 100, j, j + 100,
                    stone_color
                )
        
        # Efectos de musgo
        if all_corners:
            # Todas las esquinas (para pausa y puzzles)
            moss_positions = [
                (self.config.SCREEN_WIDTH - 200, 0, self.config.SCREEN_WIDTH, 150),  # Inferior derecha
                (self.config.SCREEN_WIDTH - 200, self.config.SCREEN_HEIGHT - 150, self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT),  # Superior derecha
                (0, 0, 200, 150),  # Inferior izquierda
                (0, self.config.SCREEN_HEIGHT - 150, 200, self.config.SCREEN_HEIGHT)  # Superior izquierda
            ]
        else:
            # Solo esquinas derechas (para mapa)
            moss_positions = [
                (self.config.SCREEN_WIDTH - 200, 0, self.config.SCREEN_WIDTH, 150),
                (self.config.SCREEN_WIDTH - 200, self.config.SCREEN_HEIGHT - 150, self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)
            ]
        
        for x1, y1, x2, y2 in moss_positions:
            arcade.draw_lrbt_rectangle_filled(
                x1, x2, y1, y2,
                (*self.config.COLORS['moss'], 60)  # Musgo con transparencia
            )
    
    def _draw_lighting_effects(self, all_corners=False):
        """Dibujar efectos de iluminación atmosférica"""
        import arcade
        
        # Luz central mística
        center_x = self.config.SCREEN_WIDTH // 2
        center_y = self.config.SCREEN_HEIGHT // 2
        
        # Resplandor central
        for radius in [300, 200, 100]:
            alpha = max(0, 50 - radius // 6)
            arcade.draw_circle_filled(
                center_x, center_y, radius,
                (*self.config.COLORS['torch'], alpha)
            )
        
        # Efectos de antorchas
        if all_corners:
            # Todas las esquinas (para pausa y puzzles)
            torch_positions = [
                (self.config.SCREEN_WIDTH - 100, self.config.SCREEN_HEIGHT - 100),  # Superior derecha
                (self.config.SCREEN_WIDTH - 100, 100),  # Inferior derecha
                (100, self.config.SCREEN_HEIGHT - 100),  # Superior izquierda
                (100, 100)  # Inferior izquierda
            ]
        else:
            # Solo esquinas derechas (para mapa)
            torch_positions = [
                (self.config.SCREEN_WIDTH - 100, self.config.SCREEN_HEIGHT - 100),  # Superior derecha
                (self.config.SCREEN_WIDTH - 100, 100)  # Inferior derecha
            ]
        
        for tx, ty in torch_positions:
            # Llama de antorcha
            arcade.draw_circle_filled(tx, ty, 15, self.config.COLORS['torch'])
            # Resplandor de antorcha
            for radius in [40, 25, 10]:
                alpha = max(0, 30 - radius)
                arcade.draw_circle_filled(
                    tx, ty, radius,
                    (*self.config.COLORS['torch'], alpha)
                )
    
    def draw_memory_node(self, node):
        """Dibujar un nodo del mapa mental con estilo de ruinas antiguas"""
        import arcade
        
        # Determinar colores y efectos basados en estado
        if node.completed:
            base_color = self.config.COLORS['success']
            glow_color = (*self.config.COLORS['success'], 120)
            border_color = self.config.COLORS['accent']
            border_width = 4
            node_size = 35
        elif node == self.current_node:
            base_color = self.config.COLORS['accent']
            glow_color = self.config.COLORS['glow']
            border_color = self.config.COLORS['torch']
            border_width = 5
            node_size = 40
        elif node.id in self.memory_map.completed_nodes:
            base_color = self.config.COLORS['success']
            glow_color = (*self.config.COLORS['success'], 80)
            border_color = self.config.COLORS['primary']
            border_width = 3
            node_size = 32
        else:
            base_color = self.config.COLORS['primary']
            glow_color = (*self.config.COLORS['primary'], 60)
            border_color = self.config.COLORS['secondary']
            border_width = 3
            node_size = 30
        
        # Dibujar efecto de resplandor
        arcade.draw_circle_filled(
            node.x, node.y, node_size + 15, glow_color
        )
        
        # Dibujar sombra del nodo
        arcade.draw_circle_filled(
            node.x + 3, node.y - 3, node_size,
            self.config.COLORS['shadow']
        )
        
        # Dibujar nodo principal
        arcade.draw_circle_filled(
            node.x, node.y, node_size, base_color
        )
        
        # Dibujar borde con efecto de relieve
        arcade.draw_circle_outline(
            node.x, node.y, node_size, border_color, border_width
        )
        
        # Dibujar borde interno para efecto de profundidad
        arcade.draw_circle_outline(
            node.x, node.y, node_size - 2, 
            (*border_color[:3], 100), 2
        )
        
        # Dibujar ID del nodo con sombra
        arcade.draw_text(
            str(node.id),
            node.x + 2, node.y - 2,
            self.config.COLORS['shadow'],
            font_size=18,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        arcade.draw_text(
            str(node.id),
            node.x, node.y,
            self.config.COLORS['text'],
            font_size=18,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        
        # Dibujar tipo de puzzle con fondo de pergamino mejorado
        if node.puzzle_type:
            # Fondo de pergamino con bordes redondeados simulados
            arcade.draw_lrbt_rectangle_filled(
                node.x - 65, node.x + 65, node.y - 55, node.y - 25,
                (*self.config.COLORS['primary'], 200)
            )
            # Borde exterior
            arcade.draw_lrbt_rectangle_outline(
                node.x - 65, node.x + 65, node.y - 55, node.y - 25,
                self.config.COLORS['secondary'], 2
            )
            # Borde interior para efecto de profundidad
            arcade.draw_lrbt_rectangle_outline(
                node.x - 63, node.x + 63, node.y - 53, node.y - 27,
                (*self.config.COLORS['accent'], 100), 1
            )
            
            arcade.draw_text(
                node.puzzle_type.replace('_', ' ').title(),
                node.x, node.y - 46,
                self.config.COLORS['text'],
                font_size=12,
                anchor_x="center",
                bold=True
            )
        
        # Dibujar indicador de bloqueo con estilo de sello roto mejorado
        if not self._is_node_available(node):
            # Fondo de sello roto con múltiples capas
            arcade.draw_lrbt_rectangle_filled(
                node.x - 65, node.x + 65, node.y + 40, node.y + 70,
                (*self.config.COLORS['error'], 180)
            )
            # Borde exterior del sello
            arcade.draw_lrbt_rectangle_outline(
                node.x - 65, node.x + 65, node.y + 40, node.y + 70,
                self.config.COLORS['error'], 3
            )
            # Borde interior para efecto de relieve
            arcade.draw_lrbt_rectangle_outline(
                node.x - 63, node.x + 63, node.y + 42, node.y + 68,
                (*self.config.COLORS['text'], 100), 1
            )
            
            arcade.draw_text(
                "SELLADO",
                node.x, node.y + 50,
                self.config.COLORS['text'],
                font_size=10,
                anchor_x="center",
                bold=True
            )
    
    def _is_node_available(self, node):
        """Verificar si un nodo está disponible para jugar"""
        available_nodes = self.memory_map.get_available_nodes()
        return node in available_nodes
    
    def draw_connections(self):
        """Dibujar conexiones entre nodos con estilo de energía mística"""
        import arcade
        
        for node in self.memory_map.nodes.values():
            for connected_id in node.connections:
                if connected_id in self.memory_map.nodes:
                    connected_node = self.memory_map.nodes[connected_id]
                    
                    # Determinar color de conexión basado en estado
                    if node.completed and connected_node.completed:
                        connection_color = self.config.COLORS['success']
                        glow_color = (*self.config.COLORS['success'], 100)
                        width = 4
                    elif node == self.current_node or connected_node == self.current_node:
                        connection_color = self.config.COLORS['torch']
                        glow_color = (*self.config.COLORS['torch'], 120)
                        width = 5
                    else:
                        connection_color = self.config.COLORS['secondary']
                        glow_color = (*self.config.COLORS['secondary'], 80)
                        width = 3
                    
                    # Dibujar efecto de resplandor
                    arcade.draw_line(
                        node.x, node.y,
                        connected_node.x, connected_node.y,
                        glow_color, width + 2
                    )
                    
                    # Dibujar línea principal
                    arcade.draw_line(
                        node.x, node.y,
                        connected_node.x, connected_node.y,
                        connection_color, width
                    )
                    
                    # Dibujar línea brillante central
                    arcade.draw_line(
                        node.x, node.y,
                        connected_node.x, connected_node.y,
                        self.config.COLORS['accent'], 1
                    )
    
    def draw_map_ui(self):
        """Dibujar UI del mapa con estilo de pergamino antiguo"""
        import arcade
        
        # Fondo de pergamino para el título con bordes mejorados
        arcade.draw_lrbt_rectangle_filled(
            self.config.SCREEN_WIDTH // 2 - 280, self.config.SCREEN_WIDTH // 2 + 280,
            self.config.SCREEN_HEIGHT - 55, self.config.SCREEN_HEIGHT - 5,
            (*self.config.COLORS['primary'], 220)
        )
        # Borde exterior
        arcade.draw_lrbt_rectangle_outline(
            self.config.SCREEN_WIDTH // 2 - 280, self.config.SCREEN_WIDTH // 2 + 280,
            self.config.SCREEN_HEIGHT - 55, self.config.SCREEN_HEIGHT - 5,
            self.config.COLORS['secondary'], 4
        )
        # Borde interior para efecto de profundidad
        arcade.draw_lrbt_rectangle_outline(
            self.config.SCREEN_WIDTH // 2 - 276, self.config.SCREEN_WIDTH // 2 + 276,
            self.config.SCREEN_HEIGHT - 51, self.config.SCREEN_HEIGHT - 9,
            (*self.config.COLORS['accent'], 120), 2
        )
        
        # Título con efecto de texto antiguo
        arcade.draw_text(
            "MAPA MENTAL - EL CÓDICE MNEMÓNICO",
            self.config.SCREEN_WIDTH // 2 + 2, self.config.SCREEN_HEIGHT - 42,
            self.config.COLORS['shadow'],
            font_size=self.config.FONT_SIZE_LARGE,
            anchor_x="center",
            bold=True
        )
        arcade.draw_text(
            "MAPA MENTAL - EL CÓDICE MNEMÓNICO",
            self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 40,
            self.config.COLORS['accent'],
            font_size=self.config.FONT_SIZE_LARGE,
            anchor_x="center",
            bold=True
        )
        
        # Panel de información con altura ajustada
        arcade.draw_lrbt_rectangle_filled(
            5, 260, self.config.SCREEN_HEIGHT - 120, self.config.SCREEN_HEIGHT - 5,
            (*self.config.COLORS['primary'], 200)
        )
        # Borde exterior
        arcade.draw_lrbt_rectangle_outline(
            5, 260, self.config.SCREEN_HEIGHT - 120, self.config.SCREEN_HEIGHT - 5,
            self.config.COLORS['secondary'], 3
        )
        # Borde interior
        arcade.draw_lrbt_rectangle_outline(
            8, 257, self.config.SCREEN_HEIGHT - 117, self.config.SCREEN_HEIGHT - 8,
            (*self.config.COLORS['accent'], 100), 1
        )
        
        # Información del progreso
        progress = self.ui_elements['map_info']['progress']
        arcade.draw_text(
            f"Progreso: {progress:.1%}",
            20, self.config.SCREEN_HEIGHT - 60,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            bold=True
        )
        
        # Nodos completados
        completed = self.ui_elements['map_info']['completed_nodes']
        total = self.ui_elements['map_info']['total_nodes']
        arcade.draw_text(
            f"Fragmentos: {completed}/{total}",
            20, self.config.SCREEN_HEIGHT - 80,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            bold=True
        )
        
        # Panel de instrucciones con bordes mejorados
        arcade.draw_lrbt_rectangle_filled(
            5, 610, 5, 85,
            (*self.config.COLORS['primary'], 200)
        )
        # Borde exterior
        arcade.draw_lrbt_rectangle_outline(
            5, 610, 5, 85,
            self.config.COLORS['secondary'], 3
        )
        # Borde interior
        arcade.draw_lrbt_rectangle_outline(
            8, 607, 8, 82,
            (*self.config.COLORS['accent'], 100), 1
        )
        
        # Instrucciones
        arcade.draw_text(
            "ESPACIO: Seleccionar nodo | ←→: Navegar | ESC: Inicio / Pausa",
            20, 30,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_SMALL,
            bold=True
        )
        
        # Mostrar nodo actual seleccionado
        if self.current_node:
            arcade.draw_text(
                f"Nodo seleccionado: {self.current_node.id} ({self.current_node.puzzle_type})",
                20, 50,
                self.config.COLORS['accent'],
                font_size=self.config.FONT_SIZE_SMALL,
                bold=True
            )
        
        # Dibujar anomalías activas
        self.draw_active_anomalies()
    
    def draw_puzzle_view(self):
        """Dibujar vista del puzzle"""
        if self.puzzle_manager.current_puzzle:
            self.puzzle_manager.current_puzzle.draw_puzzle(
                self.config.SCREEN_WIDTH,
                self.config.SCREEN_HEIGHT
            )
        
        # Dibujar información del puzzle
        puzzle_info = self.puzzle_manager.get_puzzle_info()
        if puzzle_info:
            # Información del puzzle en la esquina superior izquierda
            arcade.draw_text(
                f"Tipo: {puzzle_info['type']}",
                20,
                self.config.SCREEN_HEIGHT - 30,
                self.config.COLORS['text'],
                font_size=self.config.FONT_SIZE_SMALL
            )
            
            arcade.draw_text(
                f"Dificultad: {puzzle_info['difficulty']:.1f}",
                20,
                self.config.SCREEN_HEIGHT - 50,
                self.config.COLORS['text'],
                font_size=self.config.FONT_SIZE_SMALL
            )
            
            # Temporizador en la esquina superior derecha
            # Timer del puzzle (solo si está activo)
            remaining_time = puzzle_info.get('remaining_time', 0)
            timer_active = puzzle_info.get('timer_active', False)
            
            if timer_active and remaining_time > 0:
                arcade.draw_text(
                    f"Tiempo: {remaining_time:.1f}s",
                    self.config.SCREEN_WIDTH - 50,
                    self.config.SCREEN_HEIGHT - 30,
                    self.config.COLORS['text'],
                    font_size=self.config.FONT_SIZE_SMALL,
                    anchor_x="right"
                )
            
            # Progreso del puzzle
            progress = puzzle_info.get('progress', 0)
            arcade.draw_text(
                f"Progreso: {progress:.1%}",
                self.config.SCREEN_WIDTH - 50,
                self.config.SCREEN_HEIGHT - 50,
                self.config.COLORS['text'],
                font_size=self.config.FONT_SIZE_SMALL,
                anchor_x="right"
            )
        
        # Dibujar habilidades activas
        active_abilities = self.ability_manager.get_active_abilities()
        if active_abilities:
            y_offset = 50
            for ability_name, ability in active_abilities.items():
                arcade.draw_text(
                    f"Habilidad activa: {ability.name}",
                    20,
                    self.config.SCREEN_HEIGHT - y_offset,
                    self.config.COLORS['accent'],
                    font_size=self.config.FONT_SIZE_SMALL
                )
                y_offset += 20
    
    def draw_story_view(self):
        """Dibujar vista de historia con diseño de ruinas"""
        import arcade
        
        # Fondo atmosférico de ruinas
        self._draw_atmospheric_background(all_corners=True)
        
        # Efectos de iluminación
        self._draw_lighting_effects(all_corners=True)
        
        # Panel principal de pergamino
        panel_width = self.config.SCREEN_WIDTH - 100
        panel_height = self.config.SCREEN_HEIGHT - 100
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        # Fondo de pergamino con múltiples capas
        arcade.draw_lrbt_rectangle_filled(
            panel_x, panel_x + panel_width,
            panel_y, panel_y + panel_height,
            (*self.config.COLORS['primary'], 240)
        )
        
        # Bordes exteriores
        arcade.draw_lrbt_rectangle_outline(
            panel_x, panel_x + panel_width,
            panel_y, panel_y + panel_height,
            self.config.COLORS['secondary'], 6
        )
        
        # Bordes interiores
        arcade.draw_lrbt_rectangle_outline(
            panel_x + 10, panel_x + panel_width - 10,
            panel_y + 10, panel_y + panel_height - 10,
            (*self.config.COLORS['accent'], 150), 4
        )
        
        arcade.draw_lrbt_rectangle_outline(
            panel_x + 20, panel_x + panel_width - 20,
            panel_y + 20, panel_y + panel_height - 20,
            (*self.config.COLORS['torch'], 100), 2
        )
        
        # Determinar si es victoria o derrota
        is_victory = "completado" in self.story_text.lower() or "éxito" in self.story_text.lower()
        is_defeat = "agotado" in self.story_text.lower() or "fallado" in self.story_text.lower()
        
        # Título según el tipo de mensaje
        if is_victory:
            title = "🎉 ¡VICTORIA! 🎉"
            title_color = self.config.COLORS['success']
        elif is_defeat:
            title = "💀 TIEMPO AGOTADO 💀"
            title_color = self.config.COLORS['error']
        else:
            title = "📜 HISTORIA 📜"
            title_color = self.config.COLORS['accent']
        
        # Título con efecto épico
        arcade.draw_text(
            title,
            self.config.SCREEN_WIDTH // 2 + 3, panel_y + panel_height - 80,
            self.config.COLORS['shadow'],
            font_size=self.config.FONT_SIZE_LARGE,
            anchor_x="center",
            bold=True
        )
        arcade.draw_text(
            title,
            self.config.SCREEN_WIDTH // 2, panel_y + panel_height - 77,
            title_color,
            font_size=self.config.FONT_SIZE_LARGE,
            anchor_x="center",
            bold=True
        )
        
        # Texto de la historia con sombra
        arcade.draw_text(
            self.story_text,
            self.config.SCREEN_WIDTH // 2 + 2, self.config.SCREEN_HEIGHT // 2 - 2,
            self.config.COLORS['shadow'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            anchor_x="center",
            anchor_y="center",
            width=self.config.SCREEN_WIDTH - 200,
            bold=True
        )
        arcade.draw_text(
            self.story_text,
            self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2,
            self.config.COLORS['text'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            anchor_x="center",
            anchor_y="center",
            width=self.config.SCREEN_WIDTH - 200,
            bold=True
        )
        
        # Panel de instrucciones en la parte inferior
        instruction_panel_y = panel_y + 50
        arcade.draw_lrbt_rectangle_filled(
            self.config.SCREEN_WIDTH // 2 - 200, self.config.SCREEN_WIDTH // 2 + 200,
            instruction_panel_y - 25, instruction_panel_y + 15,
            (*self.config.COLORS['primary'], 200)
        )
        arcade.draw_lrbt_rectangle_outline(
            self.config.SCREEN_WIDTH // 2 - 200, self.config.SCREEN_WIDTH // 2 + 200,
            instruction_panel_y - 25, instruction_panel_y + 15,
            self.config.COLORS['secondary'], 3
        )
        arcade.draw_lrbt_rectangle_outline(
            self.config.SCREEN_WIDTH // 2 - 195, self.config.SCREEN_WIDTH // 2 + 195,
            instruction_panel_y - 20, instruction_panel_y + 10,
            (*self.config.COLORS['accent'], 150), 2
        )
        
        # Instrucción con sombra
        arcade.draw_text(
            "Presiona ESPACIO para continuar",
            self.config.SCREEN_WIDTH // 2 + 2, instruction_panel_y - 14,
            self.config.COLORS['shadow'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            anchor_x="center",
            bold=True
        )
        arcade.draw_text(
            "Presiona ESPACIO para continuar",
            self.config.SCREEN_WIDTH // 2, instruction_panel_y - 12,
            self.config.COLORS['accent'],
            font_size=self.config.FONT_SIZE_MEDIUM,
            anchor_x="center",
            bold=True
        )
    
    def draw_level_complete_view(self):
        """Dibujar pantalla de nivel completado"""
        import arcade
        
        screen_width = arcade.get_window().width
        screen_height = arcade.get_window().height
        
        # Fondo
        arcade.draw_lrbt_rectangle_filled(
            0, screen_width, 0, screen_height,
            self.config.COLORS['background']
        )
        
        # Título épico
        arcade.draw_text(
            "🎉 ¡NIVEL COMPLETADO! 🎉",
            screen_width // 2,
            screen_height - 100,
            self.config.COLORS['success'],
            font_size=48,
            anchor_x="center",
            bold=True
        )
        
        # Mensaje épico
        arcade.draw_text(
            "¡Has restaurado todos los fragmentos del Códice Mnemónico!",
            screen_width // 2,
            screen_height - 150,
            self.config.COLORS['primary'],
            font_size=24,
            anchor_x="center"
        )
        
        # Estadísticas
        completed_nodes = sum(1 for node in self.memory_map.nodes.values() if node.completed)
        total_nodes = len(self.memory_map.nodes)
        
        arcade.draw_text(
            f"Fragmentos restaurados: {completed_nodes}/{total_nodes}",
            screen_width // 2,
            screen_height - 200,
            self.config.COLORS['secondary'],
            font_size=20,
            anchor_x="center"
        )
        
        # Mensaje de continuación
        arcade.draw_text(
            "¿Estás listo para el siguiente desafío?",
            screen_width // 2,
            screen_height // 2 + 50,
            self.config.COLORS['text'],
            font_size=22,
            anchor_x="center"
        )
        
        # Opciones
        arcade.draw_text(
            "SÍ - Continuar al siguiente nivel",
            screen_width // 2,
            screen_height // 2,
            self.config.COLORS['accent'],
            font_size=18,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "NO - Volver al menú principal",
            screen_width // 2,
            screen_height // 2 - 30,
            self.config.COLORS['text'],
            font_size=18,
            anchor_x="center"
        )
        
        # Instrucciones
        arcade.draw_text(
            "Presiona S para continuar o N para volver al menú",
            screen_width // 2,
            50,
            self.config.COLORS['accent'],
            font_size=16,
            anchor_x="center"
        )
    
    def draw_construction_view(self):
        """Dibujar pantalla de construcción"""
        import arcade
        
        screen_width = arcade.get_window().width
        screen_height = arcade.get_window().height
        
        # Fondo
        arcade.draw_lrbt_rectangle_filled(
            0, screen_width, 0, screen_height,
            self.config.COLORS['background']
        )
        
        # Título
        arcade.draw_text(
            "🚧 NIVEL 2 EN CONSTRUCCIÓN 🚧",
            screen_width // 2,
            screen_height - 100,
            self.config.COLORS['warning'],
            font_size=36,
            anchor_x="center",
            bold=True
        )
        
        # Mensaje
        arcade.draw_text(
            "¡Gracias por completar el primer nivel!",
            screen_width // 2,
            screen_height - 150,
            self.config.COLORS['primary'],
            font_size=24,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "El siguiente nivel está siendo desarrollado",
            screen_width // 2,
            screen_height - 180,
            self.config.COLORS['text'],
            font_size=20,
            anchor_x="center"
        )
        
        # Información de desarrollo
        arcade.draw_text(
            "Próximamente:",
            screen_width // 2,
            screen_height // 2 + 50,
            self.config.COLORS['secondary'],
            font_size=22,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "• Puzzles más complejos",
            screen_width // 2,
            screen_height // 2 + 20,
            self.config.COLORS['text'],
            font_size=18,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "• Nuevas anomalías de memoria",
            screen_width // 2,
            screen_height // 2 - 10,
            self.config.COLORS['text'],
            font_size=18,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "• Habilidades cognitivas avanzadas",
            screen_width // 2,
            screen_height // 2 - 40,
            self.config.COLORS['text'],
            font_size=18,
            anchor_x="center"
        )
        
        # Instrucciones
        arcade.draw_text(
            "Presiona ESPACIO para volver al menú principal",
            screen_width // 2,
            50,
            self.config.COLORS['accent'],
            font_size=16,
            anchor_x="center"
        )
    
    def draw_active_anomalies(self):
        """Dibujar anomalías activas con estilo de maldiciones antiguas"""
        import arcade
        
        active_anomalies = self.anomaly_manager.get_active_anomalies()
        
        if active_anomalies:
            # Panel de anomalías con estilo de pergamino maldito mejorado
            arcade.draw_lrbt_rectangle_filled(
                5, 310, self.config.SCREEN_HEIGHT - 245, self.config.SCREEN_HEIGHT - 145,
                (*self.config.COLORS['error'], 180)
            )
            # Borde exterior
            arcade.draw_lrbt_rectangle_outline(
                5, 310, self.config.SCREEN_HEIGHT - 245, self.config.SCREEN_HEIGHT - 145,
                self.config.COLORS['error'], 3
            )
            # Borde interior
            arcade.draw_lrbt_rectangle_outline(
                8, 307, self.config.SCREEN_HEIGHT - 242, self.config.SCREEN_HEIGHT - 148,
                (*self.config.COLORS['text'], 100), 1
            )
            
            arcade.draw_text(
                "MALDICIONES ACTIVAS:",
                20, self.config.SCREEN_HEIGHT - 170,
                self.config.COLORS['text'],
                font_size=self.config.FONT_SIZE_SMALL,
                bold=True
            )
            
            y_offset = 190
            for anomaly_name, anomaly in active_anomalies.items():
                arcade.draw_text(
                    f"• {anomaly.name}",
                    30, self.config.SCREEN_HEIGHT - y_offset,
                    self.config.COLORS['text'],
                    font_size=self.config.FONT_SIZE_SMALL
                )
                y_offset += 20
    
    def play_victory_music(self):
        """Reproducir música de victoria"""
        try:
            # Obtener referencia al game_window para acceder a los métodos de música
            window = arcade.get_window()
            if hasattr(window, 'play_temporary_music'):
                window.play_temporary_music("victory.mp3")
                print("Música de victoria reproducida")
        except Exception as e:
            print(f"Error al reproducir música de victoria: {e}")
    
    def play_defeat_music(self):
        """Reproducir música de derrota"""
        try:
            # Obtener referencia al game_window para acceder a los métodos de música
            window = arcade.get_window()
            if hasattr(window, 'play_temporary_music'):
                window.play_temporary_music("game_over.mp3")
                print("Música de derrota reproducida")
        except Exception as e:
            print(f"Error al reproducir música de derrota: {e}")
    
    def resume_background_music(self):
        """Reanudar música de fondo"""
        try:
            # Obtener referencia al game_window para acceder a los métodos de música
            window = arcade.get_window()
            if hasattr(window, 'resume_background_music'):
                window.resume_background_music()
                print("Música de fondo reanudada")
        except Exception as e:
            print(f"Error al reanudar música de fondo: {e}")
    
    def return_to_main_menu(self):
        """Volver al menú principal"""
        try:
            # Obtener referencia al game_window para usar el nuevo sistema de guardado
            window = arcade.get_window()
            if hasattr(window, 'return_to_menu'):
                window.return_to_menu()
                print("Volviendo al menú principal con progreso guardado")
            else:
                # Fallback al método anterior
                window.current_state = "menu"
                print("Volviendo al menú principal")
        except Exception as e:
            print(f"Error al volver al menú: {e}")
    
    def draw_pause_view(self):
        """Dibujar pantalla de pausa con diseño de ruinas"""
        import arcade
        
        # Fondo atmosférico de ruinas
        self._draw_atmospheric_background(all_corners=True)
        
        # Efectos de iluminación
        self._draw_lighting_effects(all_corners=True)
        
        # Panel principal de pergamino
        panel_width = 400
        panel_height = 300
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        # Fondo de pergamino con múltiples capas
        arcade.draw_lrbt_rectangle_filled(
            panel_x, panel_x + panel_width,
            panel_y, panel_y + panel_height,
            (*self.config.COLORS['primary'], 240)
        )
        
        # Bordes exteriores
        arcade.draw_lrbt_rectangle_outline(
            panel_x, panel_x + panel_width,
            panel_y, panel_y + panel_height,
            self.config.COLORS['secondary'], 6
        )
        
        # Bordes interiores
        arcade.draw_lrbt_rectangle_outline(
            panel_x + 10, panel_x + panel_width - 10,
            panel_y + 10, panel_y + panel_height - 10,
            (*self.config.COLORS['accent'], 150), 4
        )
        
        arcade.draw_lrbt_rectangle_outline(
            panel_x + 20, panel_x + panel_width - 20,
            panel_y + 20, panel_y + panel_height - 20,
            (*self.config.COLORS['torch'], 100), 2
        )
        
        # Título PAUSA con efecto épico
        arcade.draw_text(
            "PAUSA",
            self.config.SCREEN_WIDTH // 2 + 3, panel_y + panel_height - 80,
            self.config.COLORS['shadow'],
            font_size=36,
            anchor_x="center",
            bold=True
        )
        arcade.draw_text(
            "PAUSA",
            self.config.SCREEN_WIDTH // 2, panel_y + panel_height - 77,
            self.config.COLORS['accent'],
            font_size=36,
            anchor_x="center",
            bold=True
        )
        
        # Botón Reanudar
        resume_y = panel_y + panel_height - 150
        self._draw_pause_button(
            "REANUDAR",
            self.config.SCREEN_WIDTH // 2, resume_y,
            self.config.COLORS['success'],
            is_selected=(self.selected_pause_button == 0)
        )
        
        # Botón Salir al Mapa
        exit_y = panel_y + panel_height - 220
        self._draw_pause_button(
            "SALIR AL MAPA",
            self.config.SCREEN_WIDTH // 2, exit_y,
            self.config.COLORS['error'],
            is_selected=(self.selected_pause_button == 1)
        )
    
    def _draw_pause_button(self, text, x, y, bg_color, is_selected=False):
        """Dibujar botón de pausa con estilo de pergamino"""
        # Efecto de resplandor si está seleccionado
        if is_selected:
            arcade.draw_lrbt_rectangle_filled(
                x - 130, x + 130, y - 30, y + 30,
                (*self.config.COLORS['torch'], 80)
            )
        
        # Fondo del botón
        arcade.draw_lrbt_rectangle_filled(
            x - 120, x + 120, y - 20, y + 20,
            (*bg_color, 220)
        )
        
        # Borde exterior
        border_color = self.config.COLORS['torch'] if is_selected else self.config.COLORS['secondary']
        border_width = 4 if is_selected else 3
        arcade.draw_lrbt_rectangle_outline(
            x - 120, x + 120, y - 20, y + 20,
            border_color, border_width
        )
        
        # Borde interior
        arcade.draw_lrbt_rectangle_outline(
            x - 115, x + 115, y - 15, y + 15,
            (*self.config.COLORS['accent'], 120), 2
        )
        
        # Texto del botón con sombra
        text_color = self.config.COLORS['torch'] if is_selected else self.config.COLORS['text']
        arcade.draw_text(
            text,
            x + 2, y - 2,
            self.config.COLORS['shadow'],
            font_size=18,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        arcade.draw_text(
            text,
            x, y,
            text_color,
            font_size=18,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
    
    def handle_pause_input(self, key, modifiers):
        """Manejar entrada en pantalla de pausa (ahora manejado por GameWindow)"""
        # Esta función ya no se usa directamente, GameWindow maneja la navegación
        pass
