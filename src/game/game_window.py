"""
Ventana principal del juego
"""

import arcade
from utils.config import Config
from game.game_scene import GameScene

class GameWindow(arcade.Window):
    """Ventana principal del juego El Códice Mnemónico"""
    
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        
        self.game_config = Config()
        
        # Estados del juego
        self.current_state = "menu"  # menu, gameplay, pause, game_over
        self.game_scene = None
        
        # Música de fondo
        self.background_music = None
        self.music_player = None
        self.temp_music_player = None  # Para música temporal
        self.current_music_index = 0
        self.music_list = [
            "cancion_random.mp3",
            "la_buena_y_la_mala.mp3",
            "mi_segunda_vida.mp3",
            "el_amor_de_su_vida.mp3",
            "a_lo_mejor.mp3"
        ]
        
        # Menú
        self.selected_button = 0  # 0: Iniciar, 1: Instrucciones, 2: Salir
        self.show_instructions = False
        
        # Configurar la escena inicial
        self.setup_menu()
        self.setup_music()

    def setup_music(self):
        """Cargar y reproducir la música de fondo"""
        self.load_current_music()
    
    def stop_current_music(self):
        """Detener la música actual de forma segura"""
        # Detener música temporal también
        self.stop_temporary_music()
        
        if self.music_player:
            try:
                # Intentar diferentes métodos para detener la música
                if hasattr(self.music_player, 'stop'):
                    self.music_player.stop()
                elif hasattr(self.music_player, 'pause'):
                    self.music_player.pause()
                # Limpiar la referencia
                self.music_player = None
            except Exception as e:
                print(f"Error al detener música: {e}")
                self.music_player = None
    
    def pause_background_music(self):
        """Pausar la música de fondo temporalmente"""
        if self.music_player:
            try:
                if hasattr(self.music_player, 'pause'):
                    self.music_player.pause()
                print("Música de fondo pausada")
            except Exception as e:
                print(f"Error al pausar música: {e}")
    
    def stop_temporary_music(self):
        """Detener música temporal"""
        if self.temp_music_player:
            try:
                if hasattr(self.temp_music_player, 'stop'):
                    self.temp_music_player.stop()
                elif hasattr(self.temp_music_player, 'pause'):
                    self.temp_music_player.pause()
                self.temp_music_player = None
                print("Música temporal detenida")
            except Exception as e:
                print(f"Error al detener música temporal: {e}")
                self.temp_music_player = None
    
    def resume_background_music(self):
        """Reanudar la música de fondo"""
        # Detener cualquier música temporal que esté reproduciéndose
        self.stop_temporary_music()
        
        if self.music_player:
            try:
                if hasattr(self.music_player, 'resume'):
                    self.music_player.resume()
                else:
                    # Si no hay resume, recargar la música
                    self.load_current_music()
                print("Música de fondo reanudada")
            except Exception as e:
                print(f"Error al reanudar música: {e}")
                # Intentar recargar como fallback
                self.load_current_music()
    
    def play_temporary_music(self, music_file: str):
        """Reproducir música temporal (victoria/derrota)"""
        try:
            # Detener música temporal anterior si existe
            self.stop_temporary_music()
            
            # Pausar música de fondo
            self.pause_background_music()
            
            # Cargar y reproducir música temporal
            temp_music = arcade.load_sound(f"assets/sounds/{music_file}")
            self.temp_music_player = arcade.play_sound(temp_music, volume=0.4, loop=False)
            print(f"Música temporal reproducida: {music_file}")
            return self.temp_music_player
        except Exception as e:
            print(f"Error al reproducir música temporal {music_file}: {e}")
            return None

    def load_current_music(self):
        """Cargar la música actual"""
        try:
            # Detener música anterior primero
            self.stop_current_music()
            
            # Todas las canciones están en la subcarpeta music
            filename = self.music_list[self.current_music_index]
            music_file = f"assets/sounds/music/{filename}"
            
            self.background_music = arcade.load_sound(music_file)
            self.music_player = arcade.play_sound(self.background_music, volume=0.3, loop=True)
            print(f"Música cargada: {self.format_song_name(filename)}")
        except Exception as e:
            print(f"Error al cargar la música {filename}: {e}")
            # Intentar con la primera canción como fallback
            if self.current_music_index != 0:
                self.current_music_index = 0
                try:
                    self.stop_current_music()
                    fallback_filename = self.music_list[0]
                    music_file = f"assets/sounds/music/{fallback_filename}"
                    
                    self.background_music = arcade.load_sound(music_file)
                    self.music_player = arcade.play_sound(self.background_music, volume=0.3, loop=True)
                    print(f"Música de respaldo cargada: {self.format_song_name(fallback_filename)}")
                except Exception as e2:
                    print(f"Error al cargar música de respaldo: {e2}")
    
    def change_music(self, direction):
        """Cambiar música (direction: 1 para siguiente, -1 para anterior)"""
        # Cambiar índice con navegación circular
        self.current_music_index = (self.current_music_index + direction) % len(self.music_list)
        print(f"Cambiando a canción {self.current_music_index + 1}/{len(self.music_list)}: {self.format_song_name(self.music_list[self.current_music_index])}")
        self.load_current_music()
    
    def format_song_name(self, filename):
        """Formatear nombre de canción para mostrar"""
        # Remover extensión .mp3
        name = filename.replace('.mp3', '')
        # Reemplazar guiones bajos con espacios
        name = name.replace('_', ' ')
        # Capitalizar primera letra de cada palabra
        name = ' '.join(word.capitalize() for word in name.split())
        return name
    
    def setup_menu(self):
        """Configurar el menú principal"""
        self.current_state = "menu"
        # TODO: Implementar menú principal
    
    def setup_game(self):
        """Configurar la escena de juego"""
        self.current_state = "gameplay"
        self.game_scene = GameScene(self.game_config)
    
    def on_draw(self):
        """Renderizar el frame actual"""
        self.clear()
        
        if self.current_state == "menu":
            self.draw_menu()
        elif self.current_state == "gameplay":
            self.draw_game()
        elif self.current_state == "pause":
            self.draw_pause()
        elif self.current_state == "game_over":
            self.draw_game_over()
    
    def draw_menu(self):
        """Dibujar el menú principal con estilo de ruinas antiguas"""
        # Fondo atmosférico
        self._draw_menu_background()
        
        # Efectos de iluminación
        self._draw_menu_lighting()
        
        if self.show_instructions:
            # Mostrar pantalla de instrucciones
            self._draw_instructions_screen()
            # Agregar antorcha en instrucciones
            self._draw_instructions_torch()
        else:
            # Título principal con estilo épico
            self._draw_menu_title()
            
            # Subtítulo descriptivo
            self._draw_menu_subtitle()
            
            # Botones del menú
            self._draw_menu_buttons()
            
            # Información adicional
            self._draw_menu_info()
        
        # Selector de música (solo en menú principal, no en instrucciones)
        if not self.show_instructions:
            self._draw_music_selector()
    
    def _draw_menu_background(self):
        """Dibujar fondo atmosférico del menú"""
        # Fondo base con gradiente
        arcade.draw_lrbt_rectangle_filled(
            0, self.game_config.SCREEN_WIDTH, 0, self.game_config.SCREEN_HEIGHT,
            self.game_config.COLORS['background']
        )
        
        # Efectos de piedra antigua
        for i in range(0, self.game_config.SCREEN_WIDTH, 120):
            for j in range(0, self.game_config.SCREEN_HEIGHT, 120):
                # Textura de piedra sutil
                stone_color = (
                    self.game_config.COLORS['stone'][0] + (i % 25) - 12,
                    self.game_config.COLORS['stone'][1] + (j % 25) - 12,
                    self.game_config.COLORS['stone'][2] + ((i+j) % 25) - 12
                )
                arcade.draw_lrbt_rectangle_filled(
                    i, i + 120, j, j + 120,
                    stone_color
                )
        
        # Efectos de musgo en las esquinas derechas
        moss_positions = [
            (self.game_config.SCREEN_WIDTH - 250, 0, self.game_config.SCREEN_WIDTH, 180),
            (self.game_config.SCREEN_WIDTH - 250, self.game_config.SCREEN_HEIGHT - 180, self.game_config.SCREEN_WIDTH, self.game_config.SCREEN_HEIGHT)
        ]
        
        for x1, y1, x2, y2 in moss_positions:
            arcade.draw_lrbt_rectangle_filled(
                x1, x2, y1, y2,
                (*self.game_config.COLORS['moss'], 70)
            )
    
    def _draw_menu_lighting(self):
        """Dibujar efectos de iluminación del menú"""
        # Luz central mística
        center_x = self.game_config.SCREEN_WIDTH // 2
        center_y = self.game_config.SCREEN_HEIGHT // 2
        
        # Resplandor central más intenso
        for radius in [400, 300, 200, 100]:
            alpha = max(0, 60 - radius // 8)
            arcade.draw_circle_filled(
                center_x, center_y, radius,
                (*self.game_config.COLORS['torch'], alpha)
            )
        
        # Antorchas en las esquinas derechas
        torch_positions = [
            (self.game_config.SCREEN_WIDTH - 120, self.game_config.SCREEN_HEIGHT - 120),
            (self.game_config.SCREEN_WIDTH - 120, 120)
        ]
        
        for tx, ty in torch_positions:
            # Llama de antorcha
            arcade.draw_circle_filled(tx, ty, 20, self.game_config.COLORS['torch'])
            # Resplandor de antorcha
            for radius in [50, 35, 20]:
                alpha = max(0, 40 - radius)
                arcade.draw_circle_filled(
                    tx, ty, radius,
                    (*self.game_config.COLORS['torch'], alpha)
                )
    
    def _draw_menu_title(self):
        """Dibujar título principal del menú"""
        # Fondo de pergamino para el título
        arcade.draw_lrbt_rectangle_filled(
            self.game_config.SCREEN_WIDTH // 2 - 320, self.game_config.SCREEN_WIDTH // 2 + 320,
            self.game_config.SCREEN_HEIGHT - 80, self.game_config.SCREEN_HEIGHT - 20,
            (*self.game_config.COLORS['primary'], 240)
        )
        # Borde exterior
        arcade.draw_lrbt_rectangle_outline(
            self.game_config.SCREEN_WIDTH // 2 - 320, self.game_config.SCREEN_WIDTH // 2 + 320,
            self.game_config.SCREEN_HEIGHT - 80, self.game_config.SCREEN_HEIGHT - 20,
            self.game_config.COLORS['secondary'], 5
        )
        # Borde interior
        arcade.draw_lrbt_rectangle_outline(
            self.game_config.SCREEN_WIDTH // 2 - 315, self.game_config.SCREEN_WIDTH // 2 + 315,
            self.game_config.SCREEN_HEIGHT - 75, self.game_config.SCREEN_HEIGHT - 25,
            (*self.game_config.COLORS['accent'], 150), 3
        )
        
        # Título con efecto de texto épico
        arcade.draw_text(
            "EL CÓDICE MNEMÓNICO",
            self.game_config.SCREEN_WIDTH // 2 + 3, self.game_config.SCREEN_HEIGHT - 67,
            self.game_config.COLORS['shadow'],
            font_size=36,
            anchor_x="center",
            bold=True
        )
        arcade.draw_text(
            "EL CÓDICE MNEMÓNICO",
            self.game_config.SCREEN_WIDTH // 2, self.game_config.SCREEN_HEIGHT - 64,
            self.game_config.COLORS['accent'],
            font_size=36,
            anchor_x="center",
            bold=True
        )
    
    def _draw_menu_subtitle(self):
        """Dibujar subtítulo del menú"""
        # Fondo de pergamino para el subtítulo
        arcade.draw_lrbt_rectangle_filled(
            self.game_config.SCREEN_WIDTH // 2 - 330, self.game_config.SCREEN_WIDTH // 2 + 330,
            self.game_config.SCREEN_HEIGHT - 130, self.game_config.SCREEN_HEIGHT - 90,
            (*self.game_config.COLORS['primary'], 200)
        )
        # Borde exterior
        arcade.draw_lrbt_rectangle_outline(
            self.game_config.SCREEN_WIDTH // 2 - 330, self.game_config.SCREEN_WIDTH // 2 + 330,
            self.game_config.SCREEN_HEIGHT - 130, self.game_config.SCREEN_HEIGHT - 90,
            self.game_config.COLORS['secondary'], 3
        )
        # Borde interior
        arcade.draw_lrbt_rectangle_outline(
            self.game_config.SCREEN_WIDTH // 2 - 325, self.game_config.SCREEN_WIDTH // 2 + 325,
            self.game_config.SCREEN_HEIGHT - 125, self.game_config.SCREEN_HEIGHT - 95,
            (*self.game_config.COLORS['accent'], 100), 2
        )
        
        arcade.draw_text(
            "Una aventura de memorias perdidas y conocimientos olvidados",
            self.game_config.SCREEN_WIDTH // 2, self.game_config.SCREEN_HEIGHT - 118,
            self.game_config.COLORS['text'],
            font_size=18,
            anchor_x="center",
            bold=True
        )
    
    def _draw_menu_buttons(self):
        """Dibujar botones del menú"""
        button_y = self.game_config.SCREEN_HEIGHT // 2 + 50
        
        # Botón principal - Iniciar Aventura
        is_selected = self.selected_button == 0
        self._draw_menu_button(
            "INICIAR AVENTURA",
            self.game_config.SCREEN_WIDTH // 2, button_y,
            self.game_config.COLORS['accent'] if is_selected else self.game_config.COLORS['primary'],
            self.game_config.COLORS['torch'] if is_selected else self.game_config.COLORS['text'],
            is_selected
        )
        
        # Botón secundario - Instrucciones
        is_selected = self.selected_button == 1
        self._draw_menu_button(
            "INSTRUCCIONES",
            self.game_config.SCREEN_WIDTH // 2, button_y - 80,
            self.game_config.COLORS['accent'] if is_selected else self.game_config.COLORS['primary'],
            self.game_config.COLORS['torch'] if is_selected else self.game_config.COLORS['text'],
            is_selected
        )
        
        # Botón terciario - Salir
        is_selected = self.selected_button == 2
        self._draw_menu_button(
            "SALIR",
            self.game_config.SCREEN_WIDTH // 2, button_y - 160,
            self.game_config.COLORS['accent'] if is_selected else self.game_config.COLORS['primary'],
            self.game_config.COLORS['torch'] if is_selected else self.game_config.COLORS['text'],
            is_selected
        )
    
    def _draw_menu_button(self, text, x, y, bg_color, text_color, is_selected=False):
        """Dibujar un botón del menú con estilo de pergamino"""
        # Efecto de resplandor si está seleccionado
        if is_selected:
            arcade.draw_lrbt_rectangle_filled(
                x - 160, x + 160, y - 35, y + 35,
                (*self.game_config.COLORS['torch'], 80)
            )
        
        # Fondo del botón
        arcade.draw_lrbt_rectangle_filled(
            x - 150, x + 150, y - 25, y + 25,
            (*bg_color, 220)
        )
        # Borde exterior
        border_color = self.game_config.COLORS['torch'] if is_selected else self.game_config.COLORS['secondary']
        border_width = 4 if is_selected else 3
        arcade.draw_lrbt_rectangle_outline(
            x - 150, x + 150, y - 25, y + 25,
            border_color, border_width
        )
        # Borde interior
        arcade.draw_lrbt_rectangle_outline(
            x - 145, x + 145, y - 20, y + 20,
            (*self.game_config.COLORS['accent'], 120), 2
        )
        
        # Texto del botón
        arcade.draw_text(
            text,
            x, y,
            text_color,
            font_size=20,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
    
    def _draw_menu_info(self):
        """Dibujar información adicional del menú"""
        # Panel de información en la esquina inferior izquierda
        arcade.draw_lrbt_rectangle_filled(
            10, 300, 10, 80,
            (*self.game_config.COLORS['primary'], 180)
        )
        arcade.draw_lrbt_rectangle_outline(
            10, 300, 10, 80,
            self.game_config.COLORS['secondary'], 2
        )
        
        arcade.draw_text(
             "Presiona ESPACIO para iniciar",
             20, 50,
             self.game_config.COLORS['text'],
             font_size=14,
             bold=True
         )
        
        arcade.draw_text(
            "ESC para salir",
            20, 30,
            self.game_config.COLORS['text'],
            font_size=14
        )
    
    def _draw_music_selector(self):
        """Dibujar selector de música en la esquina superior izquierda"""
        # Panel de música compacto para evitar superposición
        panel_x = 10
        panel_y = self.game_config.SCREEN_HEIGHT - 10
        panel_width = 220
        panel_height = 175
        
        arcade.draw_lrbt_rectangle_filled(
            panel_x, panel_x + panel_width, panel_y - panel_height, panel_y,
            (*self.game_config.COLORS['primary'], 200)
        )
        arcade.draw_lrbt_rectangle_outline(
            panel_x, panel_x + panel_width, panel_y - panel_height, panel_y,
            self.game_config.COLORS['secondary'], 3
        )
        arcade.draw_lrbt_rectangle_outline(
            panel_x + 5, panel_x + panel_width - 5, panel_y - panel_height + 5, panel_y - 5,
            (*self.game_config.COLORS['accent'], 100), 2
        )
        
        # Título del selector
        arcade.draw_text(
            "MÚSICA",
            panel_x + panel_width // 2, panel_y - 20,
            self.game_config.COLORS['accent'],
            font_size=14,
            anchor_x="center",
            bold=True
        )
        
        # Botones de navegación
        # Botón anterior
        arcade.draw_lrbt_rectangle_filled(
            panel_x + 10, panel_x + 40, panel_y - 45, panel_y - 25,
            (*self.game_config.COLORS['secondary'], 200)
        )
        arcade.draw_lrbt_rectangle_outline(
            panel_x + 10, panel_x + 40, panel_y - 45, panel_y - 25,
            self.game_config.COLORS['accent'], 2
        )
        arcade.draw_text(
            "◀",
            panel_x + 23, panel_y - 35,
            self.game_config.COLORS['text'],
            font_size=14,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Nombre de la canción actual
        current_song = self.format_song_name(self.music_list[self.current_music_index])
        arcade.draw_text(
            current_song,
            panel_x + panel_width // 2, panel_y - 35,
            self.game_config.COLORS['text'],
            font_size=12,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        
        # Botón siguiente
        arcade.draw_lrbt_rectangle_filled(
            panel_x + panel_width - 40, panel_x + panel_width - 10, panel_y - 45, panel_y - 25,
            (*self.game_config.COLORS['secondary'], 200)
        )
        arcade.draw_lrbt_rectangle_outline(
            panel_x + panel_width - 40, panel_x + panel_width - 10, panel_y - 45, panel_y - 25,
            self.game_config.COLORS['accent'], 2
        )
        arcade.draw_text(
            "▶",
            panel_x + panel_width - 23, panel_y - 35,
            self.game_config.COLORS['text'],
            font_size=14,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Mostrar todas las canciones con indicador de la actual
        y_offset = 75
        for i, song_file in enumerate(self.music_list):
            song_name = self.format_song_name(song_file)
            if i == self.current_music_index:
                # Canción actual - destacada
                color = self.game_config.COLORS['torch']
                prefix = "▶ "
            else:
                # Otras canciones
                color = self.game_config.COLORS['text']
                prefix = "  "
            
            arcade.draw_text(
                f"{prefix}{song_name}",
                panel_x + 15, panel_y - y_offset,
                color,
                font_size=10,
                bold=(i == self.current_music_index)
            )
            y_offset += 15
        
        # Instrucciones
        arcade.draw_text(
            "A/D para cambiar",
            panel_x + panel_width // 2, panel_y - panel_height + 15,
            self.game_config.COLORS['shadow'],
            font_size=9,
            anchor_x="center"
        )
    
    def _draw_instructions_screen(self):
        """Dibujar pantalla de instrucciones"""
        # Fondo de pergamino para instrucciones
        arcade.draw_lrbt_rectangle_filled(
            self.game_config.SCREEN_WIDTH // 2 - 400, self.game_config.SCREEN_WIDTH // 2 + 400,
            self.game_config.SCREEN_HEIGHT // 2 - 300, self.game_config.SCREEN_HEIGHT // 2 + 300,
            (*self.game_config.COLORS['primary'], 220)
        )
        arcade.draw_lrbt_rectangle_outline(
            self.game_config.SCREEN_WIDTH // 2 - 400, self.game_config.SCREEN_WIDTH // 2 + 400,
            self.game_config.SCREEN_HEIGHT // 2 - 300, self.game_config.SCREEN_HEIGHT // 2 + 300,
            self.game_config.COLORS['secondary'], 4
        )
        
        # Título
        arcade.draw_text(
            "INSTRUCCIONES",
            self.game_config.SCREEN_WIDTH // 2 + 3, self.game_config.SCREEN_HEIGHT // 2 + 250,
            self.game_config.COLORS['shadow'],
            font_size=28,
            anchor_x="center",
            bold=True
        )
        arcade.draw_text(
            "INSTRUCCIONES",
            self.game_config.SCREEN_WIDTH // 2, self.game_config.SCREEN_HEIGHT // 2 + 253,
            self.game_config.COLORS['accent'],
            font_size=28,
            anchor_x="center",
            bold=True
        )
        
        # Contenido de instrucciones
        instructions = [
            "OBJETIVO:",
            "Restaura el Códice Mnemónico resolviendo puzzles",
            "que representan fragmentos de memoria perdidos.",
            "",
            "CONTROLES:",
            "• Flechas ←→: Navegar entre nodos",
            "• ESPACIO: Seleccionar nodo/puzzle",
            "• ESC: Pausa/Salir",
            "",
            "TIPOS DE PUZZLES:",
            "• Simon Dice: Repite secuencias de símbolos",
            "• Patrón de Secuencia: Completa secuencias numéricas",
            "• Memoria Espacial: Recuerda posiciones en cuadrícula",
            "",
            "Presiona ESC para volver al menú"
        ]
        
        y_offset = 200
        for instruction in instructions:
            if instruction.startswith(("OBJETIVO:", "CONTROLES:", "TIPOS DE PUZZLES:")):
                color = self.game_config.COLORS['accent']
                font_size = 16
                bold = True
            elif instruction.startswith("•"):
                color = self.game_config.COLORS['text']
                font_size = 14
                bold = False
            elif instruction == "":
                y_offset -= 10
                continue
            else:
                color = self.game_config.COLORS['text']
                font_size = 14
                bold = False
            
            # Dibujar texto con sombra para mejor legibilidad
            arcade.draw_text(
                 instruction,
                 self.game_config.SCREEN_WIDTH // 2 + 2, self.game_config.SCREEN_HEIGHT // 2 + y_offset - 2,
                 self.game_config.COLORS['shadow'],
                 font_size=font_size,
                 anchor_x="center",
                 bold=bold
            )
            arcade.draw_text(
                 instruction,
                 self.game_config.SCREEN_WIDTH // 2, self.game_config.SCREEN_HEIGHT // 2 + y_offset,
                 color,
                 font_size=font_size,
                 anchor_x="center",
                 bold=bold
            )
            y_offset -= 25
         
         # Instrucciones de control en la esquina inferior izquierda
        arcade.draw_lrbt_rectangle_filled(
            10, 300, 10, 80,
            (*self.game_config.COLORS['primary'], 180)
        )
        arcade.draw_lrbt_rectangle_outline(
            10, 300, 10, 80,
            self.game_config.COLORS['secondary'], 2
        )
         
        arcade.draw_text(
            "Presiona ESPACIO para iniciar",
            20, 50,
            self.game_config.COLORS['text'],
            font_size=14,
            bold=True
        )
         
        arcade.draw_text(
            "ESC para volver al menú",
            20, 30,
            self.game_config.COLORS['text'],
            font_size=14
        )
    
    def _draw_instructions_torch(self):
        """Dibujar antorcha en la pantalla de instrucciones"""
        # Antorcha en la esquina superior derecha
        torch_x = self.game_config.SCREEN_WIDTH - 120
        torch_y = self.game_config.SCREEN_HEIGHT - 120
        
        # Llama de antorcha
        arcade.draw_circle_filled(torch_x, torch_y, 20, self.game_config.COLORS['torch'])
        
        # Resplandor de antorcha
        for radius in [50, 35, 20]:
            alpha = max(0, 40 - radius)
            arcade.draw_circle_filled(
                torch_x, torch_y, radius,
                (*self.game_config.COLORS['torch'], alpha)
            )
        
        # Fondo de musgo detrás de la antorcha
        arcade.draw_lrbt_rectangle_filled(
            self.game_config.SCREEN_WIDTH - 200, self.game_config.SCREEN_WIDTH, 
            self.game_config.SCREEN_HEIGHT - 200, self.game_config.SCREEN_HEIGHT,
            (*self.game_config.COLORS['moss'], 70)
        )
    
    def draw_game(self):
        """Dibujar la escena de juego"""
        if self.game_scene:
            self.game_scene.draw()
        else:
            arcade.draw_text(
                "Cargando juego...",
                self.game_config.SCREEN_WIDTH // 2,
                self.game_config.SCREEN_HEIGHT // 2,
                self.game_config.COLORS['text'],
                font_size=self.game_config.FONT_SIZE_LARGE,
                anchor_x="center"
            )
    
    def draw_pause(self):
        """Dibujar la pantalla de pausa"""
        arcade.draw_text(
            "PAUSA",
            self.game_config.SCREEN_WIDTH // 2,
            self.game_config.SCREEN_HEIGHT // 2,
            self.game_config.COLORS['primary'],
            font_size=self.game_config.FONT_SIZE_LARGE,
            anchor_x="center"
        )
    
    def draw_game_over(self):
        """Dibujar la pantalla de fin de juego"""
        arcade.draw_text(
            "FIN DEL JUEGO",
            self.game_config.SCREEN_WIDTH // 2,
            self.game_config.SCREEN_HEIGHT // 2,
            self.game_config.COLORS['error'],
            font_size=self.game_config.FONT_SIZE_LARGE,
            anchor_x="center"
        )
    
    def on_mouse_press(self, x, y, button, modifiers):
        """Manejar clics del mouse"""
        if self.current_state == "menu":
            # Verificar si se hizo clic en el botón de inicio
            button_x = self.game_config.SCREEN_WIDTH // 2
            button_y = self.game_config.SCREEN_HEIGHT // 2
            button_width = 200
            button_height = 50
            
            if (button_x - button_width // 2 <= x <= button_x + button_width // 2 and
                button_y - button_height // 2 <= y <= button_y + button_height // 2):
                self.setup_game()
    
    def on_key_press(self, key, modifiers):
        """Manejar teclas presionadas"""
        if self.current_state == "menu":
            self.handle_menu_input(key, modifiers)
        elif self.current_state == "gameplay":
            # Verificar si GameScene está en estado pause
            if self.game_scene and self.game_scene.game_state == "pause":
                self.handle_pause_navigation(key, modifiers)
            else:
                # Pasar todas las teclas al game_scene para manejo normal
                if self.game_scene:
                    self.game_scene.on_key_press(key, modifiers)
        elif key == arcade.key.ESCAPE:
            # Solo manejar ESC para salir si no estamos en gameplay
            arcade.exit()
    
    def handle_pause_navigation(self, key, modifiers):
        """Manejar navegación en pantalla de pausa"""
        if key == arcade.key.UP:
            # Navegar hacia arriba (Reanudar)
            self.game_scene.selected_pause_button = 0
        elif key == arcade.key.DOWN:
            # Navegar hacia abajo (Salir al mapa)
            self.game_scene.selected_pause_button = 1
        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            # Ejecutar acción del botón seleccionado
            if self.game_scene.selected_pause_button == 0:
                # Reanudar puzzle - reanudar timer
                if self.game_scene.puzzle_manager.current_puzzle:
                    self.game_scene.puzzle_manager.current_puzzle.resume_timer()
                self.game_scene.game_state = "puzzle_view"
            elif self.game_scene.selected_pause_button == 1:
                # Salir al mapa - no reanudar timer
                self.game_scene.game_state = "map_view"
        elif key == arcade.key.ESCAPE:
            # Salir al mapa con ESC (comportamiento por defecto) - no reanudar timer
            self.game_scene.game_state = "map_view"
    
    def handle_menu_input(self, key, modifiers):
        """Manejar entrada en el menú"""
        if self.show_instructions:
            if key == arcade.key.ESCAPE:
                self.show_instructions = False
        else:
            # Navegación con flechas
            if key == arcade.key.UP:
                self.selected_button = (self.selected_button - 1) % 3
            elif key == arcade.key.DOWN:
                self.selected_button = (self.selected_button + 1) % 3
            elif key == arcade.key.SPACE:
                self.execute_selected_action()
            
            # Cambio de música
            elif key == arcade.key.A:
                self.change_music(-1)
            elif key == arcade.key.D:
                self.change_music(1)
            
            # Salir con ESC
            elif key == arcade.key.ESCAPE:
                arcade.exit()
    
    def execute_selected_action(self):
        """Ejecutar la acción del botón seleccionado"""
        if self.selected_button == 0:  # Iniciar Aventura
            self.setup_game()
        elif self.selected_button == 1:  # Instrucciones
            self.show_instructions = True
        elif self.selected_button == 2:  # Salir
            arcade.exit()
    
    def on_update(self, delta_time):
        """Actualizar la lógica del juego"""
        if self.current_state == "gameplay" and self.game_scene:
            self.game_scene.on_update(delta_time)
