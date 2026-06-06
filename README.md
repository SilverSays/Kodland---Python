# Cave Crawler 

Juego de sobrevivencia en una cueva hecho con PyGame.
Mata monstruos, recoge monedas y usa la pausa para comprar mejoras.

## Requisitos y cómo correrlo

**Python 3.12 (recomendado):**
```bash
pip install pygame
python main.py
```

**Python 3.13 / 3.14 (versiones más nuevas):**
```bash
pip install pygame-ce
python main.py
```

> Corré el juego **desde la carpeta donde está main.py**, no desde otra ubicación.
> La primera vez genera los sprites automáticamente en `/sprites`.

## Controles

| Tecla | Acción |
|-------|--------|
| WASD / Flechas | Mover |
| SPACE | Atacar en la dirección que mirás |
| P / ESC | Pausar / reanudar |
| 1, 2, 3 | Comprar mejoras (solo desde la pausa) |
| Q (en pausa) | Volver al menú |

## Sistema de monedas y mejoras

Las monedas se recogen caminando sobre ellas y también se ganan matando enemigos.
Pausá el juego (P o ESC) para acceder a la tienda de mejoras:

| Tecla | Mejora | Costo |
|-------|--------|-------|
| 1 | Recuperar una vida | 30 monedas |
| 2 | +Velocidad de movimiento | 20 monedas |
| 3 | +Daño por ataque | 25 monedas |

La velocidad se puede comprar hasta 3 veces. El ataque hasta 2 veces.

## Enemigos

- **Slime** (verde): lento, siempre persigue. 2 golpes para matar.
- **Esqueleto** (blanco): más rápido, a veces se mueve random. 3 golpes para matar.

Los esqueletos aparecen desde la oleada 2. Cada oleada hay más enemigos.

## Puntuación

- Recoger moneda: +10 puntos y +10 monedas
- Matar enemigo: +15 puntos y +5 monedas

## Cómo funcionan los sprites

Los sprites se dibujan con la **Tortuga** al iniciar el juego y se guardan como PNG reales.
La Tortuga es una implementación propia del sistema `turtle.Turtle()` de Python,
pero que dibuja sobre superficies de PyGame en vez de abrir su propia ventana.

## Estructura del código

El `main.py` está dividido en dos secciones claramente separadas:

```
SECCIÓN 1 — CLASE TORTUGA Y SPRITES
  class Tortuga          ← implementación del sistema de la Tortuga
  sprite_jugador()       ← dibuja al caballero
  sprite_slime()         ← dibuja el slime
  sprite_esqueleto()     ← dibuja el esqueleto
  sprite_moneda()        ← dibuja la moneda
  sprite_corazon()       ← dibuja el corazón de vida
  sprite_suelo()         ← dibuja el tile del suelo
  generar_sprites()      ← guarda todo en /sprites como PNG

SECCIÓN 2 — JUEGO
  class Jugador
  class Slime
  class Esqueleto
  class Moneda
  funciones auxiliares
  pantalla_menu / pausa / gameover
  main()
```
