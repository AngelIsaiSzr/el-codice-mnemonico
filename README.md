# 🧠 El Códice Mnemónico

## 🎮 Descripción del Juego

**El Códice Mnemónico** es un juego de aventura narrativa innovador que combina puzzles cognitivos con una mecánica de mapa mental procedural. El jugador asume el rol de un "archivista de memorias" que debe restaurar un antiguo códice resolviendo desafíos mentales que representan recuerdos perdidos.

## ✨ Características Implementadas

### 🗺️ **Mapa Mental Procedural**
- Generación automática de nodos en patrón espiral
- Conexiones dinámicas entre nodos
- Progresión no lineal del juego
- Cada nodo representa un puzzle diferente

### 🧩 **Sistema de Puzzles**
- **Simón Dice**: Reproducir secuencias de símbolos
- **Patrones de Secuencia**: Encontrar el siguiente número en secuencias lógicas
- Dificultad adaptativa basada en rendimiento del jugador
- Sistema de puntuación y tiempo límite

### 🧠 **Habilidades Cognitivas**
- **Palacio Mental**: Almacenar información temporalmente
- **Visión Periférica**: Ampliar campo de visión (desbloqueable)
- **Enfoque**: Ralentizar el tiempo (desbloqueable)
- Sistema de cooldowns y duraciones

### 👻 **Anomalías de la Memoria**
- **El Olvido**: Oscurece partes del tablero
- **El Ruido**: Introduce información falsa
- **La Repetición**: Obliga a resolver puzzles más difíciles
- Activación aleatoria basada en dificultad

### 📊 **Personalización Adaptativa**
- Análisis de rendimiento del jugador
- Identificación de áreas débiles y fuertes
- Ajuste automático de dificultad
- Desbloqueo progresivo de habilidades

## 🏗️ Arquitectura Técnica

### **Tecnologías Utilizadas**
- **Python 3.7+**: Lenguaje principal
- **Arcade 2.6+**: Framework de juegos 2D
- **NumPy**: Cálculos matemáticos
- **Pymunk**: Motor de físicas (para futuras extensiones)

### **Estructura del Proyecto**
```
ElCodiceMnemonico/
├── main.py                 # Punto de entrada
├── install.py              # Script de instalación
├── requirements.txt        # Dependencias
├── README.md              # Documentación principal
├── src/                   # Código fuente
│   ├── game/              # Lógica principal
│   ├── puzzles/            # Implementación de puzzles
│   └── utils/              # Utilidades
├── assets/                # Recursos del juego
└── data/                  # Datos y configuración
```

### **Componentes Principales**
1. **GameWindow**: Ventana principal y manejo de estados
2. **GameScene**: Escena del juego que integra todos los sistemas
3. **MemoryMap**: Generación y manejo del mapa mental
4. **PuzzleManager**: Gestión central de puzzles
5. **CognitiveAbilityManager**: Sistema de habilidades
6. **AnomalyManager**: Sistema de anomalías

## 🎯 Mecánicas de Juego

### **Flujo Principal**
1. **Inicio**: Generación del mapa mental procedural
2. **Navegación**: Movimiento entre nodos disponibles
3. **Selección**: Elegir nodo para resolver puzzle
4. **Resolución**: Completar puzzle con entrada del jugador
5. **Progresión**: Desbloquear nuevos nodos y habilidades
6. **Narrativa**: Mostrar fragmentos de historia

### **Controles**
- **ESPACIO**: Seleccionar nodo actual
- **←→**: Navegar entre nodos
- **ESC**: Menú de habilidades
- **1-6**: Símbolos para puzzles Simón Dice
- **0-9**: Números para puzzles de patrones
- **H**: Usar pista

## 🚀 Instalación y Ejecución

### **Requisitos**
- Python 3.7 o superior
- Windows/Linux/macOS

### **Instalación Automática**
```bash
python install.py
```

### **Instalación Manual**
```bash
pip install -r requirements.txt
python main.py
```

### **Verificación**
```bash
python test_game.py
```

## 🔮 Extensiones Futuras

### **Nuevos Tipos de Puzzles**
- Memoria Espacial: Recordar posiciones
- Lógica de Símbolos: Acertijos lógicos
- Búsqueda de Patrones: Encontrar patrones ocultos

### **Nuevas Habilidades**
- Intuición: Pistas automáticas
- Persistencia: Intentos adicionales
- Claridad: Reducir anomalías

### **Nuevas Anomalías**
- La Distracción: Elementos distractores
- El Caos: Desordenar información
- La Presión: Reducir tiempo límite

## 📈 Características Técnicas Destacadas

### **Rendimiento**
- Optimizado para 60 FPS
- Gestión eficiente de memoria
- Actualizaciones solo de sistemas activos

### **Escalabilidad**
- Arquitectura modular
- Fácil adición de nuevos puzzles
- Sistema de configuración flexible

### **Mantenibilidad**
- Código bien documentado
- Separación clara de responsabilidades
- Sistema de pruebas integrado

## 🎨 Diseño Visual

### **Paleta de Colores**
- Fondo: Azul oscuro profundo
- Primario: Azul claro
- Secundario: Púrpura
- Acento: Naranja dorado
- Texto: Blanco

### **Tipografía**
- Tamaños escalables
- Legibilidad optimizada
- Soporte para caracteres especiales

## 🏆 Logros del Proyecto

✅ **Sistema completo de juego funcional**
✅ **Arquitectura modular y escalable**
✅ **Puzzles cognitivos innovadores**
✅ **Sistema de dificultad adaptativa**
✅ **Interfaz intuitiva y atractiva**
✅ **Documentación técnica completa**
✅ **Sistema de pruebas automatizado**
✅ **Instalación y configuración simplificada**

## 🎯 Impacto y Potencial

Este proyecto demuestra la capacidad de crear experiencias de juego innovadoras que combinan:
- **Educación cognitiva** a través de puzzles desafiantes
- **Narrativa inmersiva** con fragmentos de historia
- **Tecnología moderna** con Python y Arcade
- **Diseño centrado en el usuario** con dificultad adaptativa

El juego tiene potencial para:
- **Portafolio profesional** destacado
- **Investigación en cognición** y entrenamiento mental
- **Educación** en programación de juegos
- **Base para proyectos más grandes** en el futuro

---

**¡El Códice Mnemónico está listo para ser explorado! 🧠✨**
