"""
CAVE CRAWLER
----------------
Sobrevive oleadas de monstruos, recoge monedas y cómprate mejoras

Controles:
  WASD / Flechas  =  Mover
  SPACE           =  Atacar
  P / ESC         =  Pausar  (desde la pausa se compran mejoras con 1, 2, 3)
"""

import pygame
import sys
import math
import random
import time          # ya no lo usé xd
import os

pygame.init()

SCREEN_W = 800
SCREEN_H = 600
screen   = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Cave Crawler")
clock    = pygame.time.Clock()
FPS      = 60

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0  )
RED    = (210,  50,  50 )
YELLOW = (240, 200,  50 )
GRAY   = (120, 120, 130 )
DARK   = ( 22,  17,  30 )

MENU     = 0
PLAYING  = 1
PAUSED   = 2
GAMEOVER = 3

SPRITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")

                  
#  SECCIÓN 1 - Creacion de sprites con tortuga

class Tortuga:
    

    def __init__(self, superficie):
        self.surf     = superficie
        self.x        = superficie.get_width()  / 2
        self.y        = superficie.get_height() / 2
        self.angulo   = 90       # 90 = apunta arriba, 0 = apunta derecha
        self.pen      = True
        self.pen_col  = (0, 0, 0)
        self.pen_w    = 1
        self._fill_c  = None
        self._fill_pts = []
        self._filling  = False

    # - Movimiento 

    def adelante(self, distancia):
        """Avanza en la dirección actual."""
        rad = math.radians(self.angulo)
        nx  = self.x + math.cos(rad) * distancia
        ny  = self.y - math.sin(rad) * distancia
        self._mover(nx, ny)

    def atras(self, distancia):
        self.adelante(-distancia)

    def derecha(self, grados):
        self.angulo -= grados

    def izquierda(self, grados):
        self.angulo += grados

    def ir_a(self, tx, ty):
        """Va al punto (tx, ty) en coordenadas tortuga (origen = centro)."""
        cx = self.surf.get_width()  / 2
        cy = self.surf.get_height() / 2
        self._mover(cx + tx, cy - ty)

    def inicio(self):
        """Vuelve al centro apuntando hacia arriba."""
        self.ir_a(0, 0)
        self.angulo = 90

    def direccion(self, grados):
        """Apunta en la dirección indicada."""
        self.angulo = grados

    # ---- Lápiz 

    def lapiz_arriba(self):     self.pen     = False
    def lapiz_abajo(self):      self.pen     = True
    def color(self, c):         self.pen_col = c
    def grosor(self, w):        self.pen_w   = w

    # ---- Relleno (igual que begin_fill / end_fill de turtle) 

    def iniciar_relleno(self, color):
        """Empieza a recopilar puntos para un polígono relleno."""
        self._fill_c   = color
        self._fill_pts = [(int(self.x), int(self.y))]
        self._filling  = True

    def terminar_relleno(self):
        """Dibuja el polígono con los puntos recopilados."""
        if len(self._fill_pts) >= 3:
            pygame.draw.polygon(self.surf, self._fill_c, self._fill_pts)
        self._filling  = False
        self._fill_pts = []

    # ---- Atajos para formas comunes 

    def circulo_relleno(self, color, tx, ty, radio):
        """Círculo relleno centrado en (tx, ty) en coords tortuga."""
        cx = int(self.surf.get_width()  / 2 + tx)
        cy = int(self.surf.get_height() / 2 - ty)
        pygame.draw.circle(self.surf, color, (cx, cy), radio)

    def rect_relleno(self, color, tx, ty, ancho, alto):
        """Rectángulo relleno. (tx, ty) = esquina sup-izq en coords tortuga."""
        cx = int(self.surf.get_width()  / 2 + tx)
        cy = int(self.surf.get_height() / 2 - ty)
        pygame.draw.rect(self.surf, color, (cx, cy, ancho, alto))

    # ---- Interno 

    def _mover(self, nx, ny):
        if self.pen:
            pygame.draw.line(self.surf, self.pen_col,
                             (int(self.x), int(self.y)),
                             (int(nx),     int(ny)),
                             self.pen_w)
        if self._filling:
            self._fill_pts.append((int(nx), int(ny)))
        self.x, self.y = nx, ny


# ---- Funciones de dibujo de cada sprite 

def sprite_jugador():
    """Caballero"""
    surf = pygame.Surface((44, 56), pygame.SRCALPHA)
    t    = Tortuga(surf)          # centro en (22, 28)

    # Casco
    t.rect_relleno((90, 130, 220), -10, 24, 20, 10)
    t.color((60, 90, 180)); t.grosor(1)
    t.lapiz_arriba(); t.ir_a(-11, 14); t.lapiz_abajo()
    t.ir_a(11, 14)                     # línea inferior del casco

    # Cara
    t.circulo_relleno((215, 175, 135), 0, 15, 7)
    t.circulo_relleno(( 40,  30,  50), -3, 16, 2)   # ojo izquierdo
    t.circulo_relleno(( 40,  30,  50),  3, 16, 2)   # ojo derecho

    # Cuerpo / armadura
    t.rect_relleno((70, 110, 200), -10, 5, 20, 14)
    t.color((50, 80, 155)); t.grosor(1)
    t.lapiz_arriba(); t.ir_a(-10, 5); t.lapiz_abajo()
    t.ir_a(10, 5)                      # línea del pecho

    # Piernas
    t.rect_relleno((55, 80, 155), -10, -13, 8, 10)
    t.rect_relleno((55, 80, 155),   2, -13, 8, 10)

    # Botas
    t.rect_relleno((65, 48, 28), -11, -24, 9, 4)
    t.rect_relleno((65, 48, 28),   1, -24, 9, 4)

    # Espada (línea diagonal con la tortuga)
    t.color((200, 215, 225)); t.grosor(2)
    t.lapiz_arriba(); t.ir_a(11, 20); t.lapiz_abajo()
    t.ir_a(15, 5)
    # Guarda de la espada
    t.color((200, 170, 40)); t.grosor(2)
    t.lapiz_arriba(); t.ir_a(10, 14); t.lapiz_abajo()
    t.ir_a(16, 12)

    return surf


def sprite_slime():
    """Slime verde"""
    surf = pygame.Surface((38, 34), pygame.SRCALPHA)
    t    = Tortuga(surf)          

    t.iniciar_relleno((55, 195, 75))
    for i in range(25):
        ang = math.radians(i * 15)     
        tx  = 15 * math.cos(ang)
        ty  =  9 * math.sin(ang)
        if i == 0: t.lapiz_arriba()
        else:      t.lapiz_abajo()
        t.ir_a(tx, ty - 2)
    t.terminar_relleno()

    # Protuberancia superior
    t.circulo_relleno((70, 210, 88), 0, 7, 7)

    # Contorno del cuerpo 
    t.color((35, 140, 50)); t.grosor(2)
    for i in range(25):
        ang = math.radians(i * 15)
        tx  = 15 * math.cos(ang)
        ty  =  9 * math.sin(ang)
        if i == 0: t.lapiz_arriba()
        else:      t.lapiz_abajo()
        t.ir_a(tx, ty - 2)

    # Ojos
    t.circulo_relleno((20, 15, 25), -5,  3, 3)
    t.circulo_relleno((20, 15, 25),  5,  3, 3)
    t.circulo_relleno((255, 255, 255), -4, 4, 1)   # brillo ojo izq
    t.circulo_relleno((255, 255, 255),  6, 4, 1)   # brillo ojo der

    return surf


def sprite_esqueleto():
    """Esqueleto"""
    surf = pygame.Surface((36, 54), pygame.SRCALPHA)
    t    = Tortuga(surf)          
    bone = (225, 220, 210)
    dark = ( 25,  20,  35)

    # Craneo
    t.iniciar_relleno(bone)
    for i in range(21):
        ang = math.radians(i * 18)     
        tx  = 9 * math.cos(ang)
        ty  = 9 * math.sin(ang)
        if i == 0: t.lapiz_arriba()
        else:      t.lapiz_abajo()
        t.ir_a(tx, ty + 14)             

    # Mandíbula
    t.rect_relleno(bone, -7, 4, 14, 7)

    # Ojos
    t.circulo_relleno(dark, -4, 15, 3)
    t.circulo_relleno(dark,  4, 15, 3)

    # Dientes 
    t.color((200, 195, 180)); t.grosor(1)
    for dx in (-5, -1, 3):
        t.lapiz_arriba(); t.ir_a(dx, 4); t.lapiz_abajo()
        t.ir_a(dx + 3, 4)

    # Torso
    t.rect_relleno(bone, -8, -4, 16, 12)
    # Costillas 
    t.color((185, 180, 165)); t.grosor(1)
    for dy in (-5, -9):
        t.lapiz_arriba(); t.ir_a(-8, dy); t.lapiz_abajo()
        t.ir_a(8, dy)

    # Brazos
    t.color(bone); t.grosor(2)
    t.lapiz_arriba(); t.ir_a( -8, -3); t.lapiz_abajo(); t.ir_a(-14, -13)
    t.lapiz_arriba(); t.ir_a(  8, -3); t.lapiz_abajo(); t.ir_a( 14, -13)

    # Piernas
    t.lapiz_arriba(); t.ir_a(-4, -16); t.lapiz_abajo(); t.ir_a(-6, -26)
    t.lapiz_arriba(); t.ir_a( 4, -16); t.lapiz_abajo(); t.ir_a( 6, -26)

    # Pies 
    t.grosor(1)
    t.lapiz_arriba(); t.ir_a(-9,  -26); t.lapiz_abajo(); t.ir_a(-3,  -26)
    t.lapiz_arriba(); t.ir_a( 3,  -26); t.lapiz_abajo(); t.ir_a( 9,  -26)

    return surf


def sprite_moneda():
    """Moneda de oro - círculo dorado"""
    surf = pygame.Surface((24, 24), pygame.SRCALPHA)
    t    = Tortuga(surf)          

    # Círculo exterior 
    t.iniciar_relleno((255, 190, 40))
    for i in range(21):
        ang = math.radians(i * 18)
        if i == 0: t.lapiz_arriba()
        else:      t.lapiz_abajo()
        t.ir_a(10 * math.cos(ang), 10 * math.sin(ang))
    t.terminar_relleno()

    # Círculo interior más claro
    t.circulo_relleno((255, 220, 100), 0, 0, 7)

    # Contorno dorado oscuro 
    t.color((200, 150, 20)); t.grosor(2)
    for i in range(21):
        ang = math.radians(i * 18)
        if i == 0: t.lapiz_arriba()
        else:      t.lapiz_abajo()
        t.ir_a(10 * math.cos(ang), 10 * math.sin(ang))

    # G en el centro
    g = pygame.font.Font(None, 16).render("G", True, (175, 125, 15))
    surf.blit(g, (8, 6))

    return surf


def sprite_corazon():
    """Corazón rojo - dos círculos + triángulo"""
    surf = pygame.Surface((24, 22), pygame.SRCALPHA)
    t    = Tortuga(surf)         

    col = (220, 50, 60)
    # Dos lóbulos superiores
    t.circulo_relleno(col, -5, 4, 6)
    t.circulo_relleno(col,  5, 4, 6)

    # Triángulo inferior 
    t.iniciar_relleno(col)
    t.lapiz_arriba(); t.ir_a(-10, 2); t.lapiz_abajo()
    t.ir_a(0, -9)
    t.ir_a(10, 2)
    t.ir_a(-10, 2)
    t.terminar_relleno()

    # Brillito
    t.circulo_relleno((240, 110, 120), -4, 6, 2)

    return surf


def sprite_suelo():
    """Tile de suelo de cueva"""
    surf = pygame.Surface((32, 32))
    t    = Tortuga(surf)          

    surf.fill((48, 42, 60))
    t.rect_relleno((40, 35, 52), -14, 14, 28, 28)  

    # Líneas de la baldosa 
    t.color((58, 52, 70)); t.grosor(1)
    t.lapiz_arriba(); t.ir_a(-16, 0);  t.lapiz_abajo(); t.ir_a(16,  0)   # horizontal
    t.lapiz_arriba(); t.ir_a(0,   16); t.lapiz_abajo(); t.ir_a(0,  -16)  # vertical

    t.color((44, 39, 56)); t.grosor(2)
    for rx, ry in [(-7, 5), (5, -6), (-3, -8), (8, 7)]:
        t.lapiz_arriba(); t.ir_a(rx, ry); t.lapiz_abajo()
        t.ir_a(rx + 2, ry)

    return surf


def generar_sprites():
    """Genera y guarda todos los sprites en /sprites como archivos PNG."""
    os.makedirs(SPRITE_DIR, exist_ok=True)
    pares = [
        ("jugador.png",   sprite_jugador()),
        ("slime.png",     sprite_slime()),
        ("esqueleto.png", sprite_esqueleto()),
        ("moneda.png",    sprite_moneda()),
        ("corazon.png",   sprite_corazon()),
        ("suelo.png",     sprite_suelo()),
    ]
    for nombre, superficie in pares:
        pygame.image.save(superficie, os.path.join(SPRITE_DIR, nombre))


#  SECCIÓN 2 - Juego



def cargar(nombre):
    """Carga un sprite desde la carpeta /sprites."""
    return pygame.image.load(os.path.join(SPRITE_DIR, nombre)).convert_alpha()


class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.imagen_orig = cargar("jugador.png")
        self.image       = self.imagen_orig.copy()
        self.rect        = self.image.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))

        self.velocidad   = 3
        self.vidas       = 3
        self.max_vidas   = 5
        self.dano_atk    = 1        # HP que quita por golpe
        self.monedas     = 0        # monedas gastables en mejoras
        self.score       = 0        # puntuación total (no baja nunca)

        self.niv_vel     = 0        # cuántas veces compró velocidad (máx 3)
        self.niv_atk     = 0        # cuántas veces compró ataque (máx 2)

        self.invincible  = 0        # frames de invencibilidad tras recibir daño
        self.atk_timer   = 0        # frames que dura el hitbox del ataque
        self.facing      = "right"
        self.flipped     = False

    def update(self, keys):
        old_x = self.rect.x   

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.velocidad;  self.facing = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.velocidad;  self.facing = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.velocidad;  self.facing = "left"
            if not self.flipped:
                self.image   = pygame.transform.flip(self.imagen_orig, True, False)
                self.flipped = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.velocidad;  self.facing = "right"
            if self.flipped:
                self.image   = self.imagen_orig.copy()
                self.flipped = False

        self.rect.clamp_ip(screen.get_rect())
        if self.invincible > 0: self.invincible -= 1
        if self.atk_timer   > 0: self.atk_timer   -= 1

    def atacar(self):
        if self.atk_timer == 0:
            self.atk_timer = 18

    def hitbox_ataque(self):
        
        if self.atk_timer <= 0:
            return None
        r = pygame.Rect(0, 0, 44, 28)
        if   self.facing == "right": r.midleft   = self.rect.midright
        elif self.facing == "left":  r.midright  = self.rect.midleft
        elif self.facing == "up":    r.midbottom = self.rect.midtop
        else:                        r.midtop    = self.rect.midbottom
        return r

    def recibir_golpe(self):
        if self.invincible == 0:
            self.vidas     -= 1
            self.invincible = 80


class Slime(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = cargar("slime.png")
        self.rect  = self.image.get_rect(center=(x, y))
        self.hp    = 2
        self.fx    = float(x)
        self.fy    = float(y)
        self.speed = 1.3

    def update(self, jugador):
        dx   = jugador.rect.centerx - self.fx
        dy   = jugador.rect.centery - self.fy
        dist = math.hypot(dx, dy) or 1
        self.fx += (dx / dist) * self.speed
        self.fy += (dy / dist) * self.speed
        self.rect.center = (int(self.fx), int(self.fy))


class Esqueleto(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = cargar("esqueleto.png")
        self.rect  = self.image.get_rect(center=(x, y))
        self.hp    = 3
        self.fx    = float(x)
        self.fy    = float(y)
        self.speed = 1.8
        self.tick  = random.randint(0, 149)
        self.wx    = random.choice([-1, 0, 1])
        self.wy    = random.choice([-1, 0, 1])

    def update(self, jugador):
        self.tick += 1
        if self.tick % 150 == 0:        
            self.wx = random.choice([-1, 0, 1])
            self.wy = random.choice([-1, 0, 1])

        if self.tick % 150 < 40:        
            self.fx += self.wx * self.speed
            self.fy += self.wy * self.speed
        else:                           
            dx   = jugador.rect.centerx - self.fx
            dy   = jugador.rect.centery - self.fy
            dist = math.hypot(dx, dy) or 1
            self.fx += (dx / dist) * self.speed
            self.fy += (dy / dist) * self.speed

        self.rect.center = (int(self.fx), int(self.fy))


class Moneda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image  = cargar("moneda.png")
        self.rect   = self.image.get_rect(center=(x, y))
        self.base_y = float(y)
        self.bob_t  = random.uniform(0, 6.28)

    def update(self):
        self.bob_t        += 0.07
        self.rect.centery  = int(self.base_y + math.sin(self.bob_t) * 3)


def borde_al_azar():
    """Posición aleatoria en el borde de la pantalla para spawnear enemigos"""
    lado = random.randint(0, 3)
    if   lado == 0: return random.randint(0, SCREEN_W), -35
    elif lado == 1: return SCREEN_W + 35, random.randint(0, SCREEN_H)
    elif lado == 2: return random.randint(0, SCREEN_W), SCREEN_H + 35
    else:           return -35, random.randint(0, SCREEN_H)


def crear_oleada(numero):
    """Crea el grupo de enemigos para la oleada indicada"""
    grupo        = pygame.sprite.Group()
    n_slimes     = 2 + numero * 2
    n_esqueletos = max(0, numero - 1)
    for _ in range(n_slimes):
        grupo.add(Slime(*borde_al_azar()))
    for _ in range(n_esqueletos):
        grupo.add(Esqueleto(*borde_al_azar()))
    return grupo


def crear_monedas(n):
    grupo = pygame.sprite.Group()
    for _ in range(n):
        x = random.randint(60, SCREEN_W - 60)
        y = random.randint(60, SCREEN_H - 60)
        grupo.add(Moneda(x, y))
    return grupo


def dibujar_fondo(tile):
    for tx in range(0, SCREEN_W, 32):
        for ty in range(0, SCREEN_H, 32):
            screen.blit(tile, (tx, ty))


def dibujar_hud(jugador, oleada, font, corazon_img):
    t = font.render(f"SCORE: {jugador.score}", True, YELLOW)
    screen.blit(t, (10, 10))
    t = font.render(f"MON: {jugador.monedas}", True, (255, 210, 60))
    screen.blit(t, (10, 44))
    t = font.render(f"OLA {oleada}", True, (100, 180, 255))
    screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 10))
    for i in range(jugador.vidas):
        screen.blit(corazon_img, (SCREEN_W - 32 - i * 28, 10))


def dibujar_efecto_ataque(jugador):
    hr = jugador.hitbox_ataque()
    if hr is None:
        return
    s = pygame.Surface((hr.width, hr.height), pygame.SRCALPHA)
    s.fill((255, 240, 80, int(180 * jugador.atk_timer / 18)))
    screen.blit(s, hr.topleft)
    pygame.draw.rect(screen, (255, 220, 60), hr, 2)


# ---- Pantallas 

def pantalla_menu(font_big, font_sm, tick):
    screen.fill(DARK)
    t = font_big.render("CAVE CRAWLER", True, YELLOW)
    screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 155))
    t = font_sm.render("Sobrevive las oleadas y gasta tus monedas en mejoras", True, (180, 155, 220))
    screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 245))
    if (tick // 35) % 2 == 0:
        t = font_sm.render("Presiona ENTER para jugar", True, WHITE)
        screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 325))
    t = font_sm.render("WASD: Mover  |  SPACE: Atacar  |  P/ESC: Pausar y mejorar", True, GRAY)
    screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 410))


def pantalla_pausa(font_big, font_sm, jugador):
    """Pausa con sistema de mejoras integrado."""
    # Overlay oscuro semitransparente
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 172))
    screen.blit(overlay, (0, 0))

    # Caja central
    caja = pygame.Rect(SCREEN_W // 2 - 210, SCREEN_H // 2 - 185, 420, 370)
    pygame.draw.rect(screen, (28, 20, 44), caja, border_radius=12)
    pygame.draw.rect(screen, (145, 95, 215), caja, 2, border_radius=12)

    def txt(texto, fuente, color, y):
        s = fuente.render(texto, True, color)
        screen.blit(s, (SCREEN_W // 2 - s.get_width() // 2, y))

    txt("PAUSADO", font_big, YELLOW, caja.y + 16)
    txt(f"Monedas disponibles: {jugador.monedas}", font_sm, (255, 210, 60), caja.y + 88)
    txt("── Mejoras ──", font_sm, (180, 155, 220), caja.y + 122)

    mejoras = [
        ("1", "Recuperar vida",  30, jugador.vidas < jugador.max_vidas),
        ("2", "+Velocidad",      20, jugador.niv_vel < 3),
        ("3", "+Ataque",         25, jugador.niv_atk < 2),
    ]
    py = caja.y + 158
    for tecla, nombre, costo, disponible in mejoras:
        if not disponible:
            color  = GRAY
            etiq   = f"[{tecla}]  {nombre}  — maximo alcanzado"
        elif jugador.monedas < costo:
            color  = (155, 100, 100)
            etiq   = f"[{tecla}]  {nombre}  ({costo} mon.)  — sin monedas"
        else:
            color  = WHITE
            etiq   = f"[{tecla}]  {nombre}  ({costo} mon.)"
        txt(etiq, font_sm, color, py)
        py += 42

    txt("P / ESC = Continuar   |   Q = Menu", font_sm, GRAY, caja.bottom - 38)


def pantalla_gameover(font_big, font_sm, score, oleada):
    screen.fill((14, 8, 18))
    t = font_big.render("GAME OVER", True, RED)
    screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 185))
    t = font_sm.render(f"Puntuacion: {score}", True, YELLOW)
    screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 285))
    t = font_sm.render(f"Llegaste a la ola {oleada}", True, (100, 180, 255))
    screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 328))
    t = font_sm.render("ENTER: Volver al menu   ESC: Salir", True, GRAY)
    screen.blit(t, (SCREEN_W // 2 - t.get_width() // 2, 418))


# ---- Main
def main():
    font_big = pygame.font.Font(None, 72)
    font_sm  = pygame.font.Font(None, 32)

    generar_sprites()

    tile_img    = pygame.image.load(os.path.join(SPRITE_DIR, "suelo.png")).convert()
    corazon_img = cargar("corazon.png")

    state      = MENU
    jugador    = None
    enemigos   = pygame.sprite.Group()
    monedas    = pygame.sprite.Group()
    oleada     = 1
    tick       = 0
    wave_timer = 0     

    def centrar_jugador(j): j.rect.center = (SCREEN_W//2, SCREEN_H//2) 

    running = True
    while running:
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                # ESC
                if event.key == pygame.K_ESCAPE:
                    if   state == PLAYING: state = PAUSED
                    elif state == PAUSED:  state = PLAYING
                    else:                  running = False

                # P  (pausa / reanudar)
                elif event.key == pygame.K_p:
                    if   state == PLAYING: state = PAUSED
                    elif state == PAUSED:  state = PLAYING

                # ENTER
                elif event.key == pygame.K_RETURN:
                    if state == MENU:
                        jugador  = Jugador()
                        oleada   = 1
                        enemigos = crear_oleada(oleada)
                        monedas  = crear_monedas(5)
                        state    = PLAYING
                    elif state == GAMEOVER:
                        state = MENU

                # SPACE — atacar
                elif event.key == pygame.K_SPACE and state == PLAYING:
                    jugador.atacar()

                # Acciones desde la pausa
                elif state == PAUSED:
                    if event.key == pygame.K_q:
                        state = MENU

                    elif event.key == pygame.K_1:
                        if jugador.monedas >= 30 and jugador.vidas < jugador.max_vidas:
                            jugador.monedas -= 30
                            jugador.vidas   += 1

                    elif event.key == pygame.K_2:
                        if jugador.monedas >= 20 and jugador.niv_vel < 3:
                            jugador.monedas   -= 20
                            jugador.velocidad += 1
                            jugador.niv_vel   += 1

                    elif event.key == pygame.K_3:
                        if jugador.monedas >= 25 and jugador.niv_atk < 2:
                            jugador.monedas  -= 25
                            jugador.dano_atk += 1
                            jugador.niv_atk  += 1

        # ---- UPDATE 
        if state == PLAYING:
            keys = pygame.key.get_pressed()
            jugador.update(keys)

            for e in enemigos:
                e.update(jugador)
            monedas.update()

            # Recoger monedas
            recogidas = pygame.sprite.spritecollide(jugador, monedas, True)
            for _ in recogidas:
                jugador.monedas = jugador.monedas + 10   
                jugador.score  += 10

            # Enemigos tocan al jugador
            for e in pygame.sprite.spritecollide(jugador, enemigos, False):
                jugador.recibir_golpe()

            # Jugador ataca a enemigos
            hr = jugador.hitbox_ataque()
            if hr:
                for e in list(enemigos):
                    if hr.colliderect(e.rect):
                        e.hp -= jugador.dano_atk
                        if e.hp <= 0:
                            e.kill()
                            jugador.score   += 15
                            jugador.monedas += 5   # bonus por matar

            # Oleada terminada
            if len(enemigos) == 0:
                oleada     += 1
                wave_timer  = 100
                enemigos    = crear_oleada(oleada)
                monedas.add(*crear_monedas(3 + oleada).sprites())

            # Game over
            if jugador.vidas <= 0:
                state = GAMEOVER

        # ---- DRAW 
        if state == MENU:
            pantalla_menu(font_big, font_sm, tick)

        elif state in (PLAYING, PAUSED):
            dibujar_fondo(tile_img)
            monedas.draw(screen)
            dibujar_efecto_ataque(jugador)
            enemigos.draw(screen)

            # Jugador parpadea cuando es invencible
            if jugador.invincible > 0 and (jugador.invincible // 5) % 2 == 0:
                pass
            else:
                screen.blit(jugador.image, jugador.rect)

            # Banner de nueva oleada
            if wave_timer > 0:
                wave_timer -= 1
                t  = font_sm.render(f"!OLA {oleada}!", True, YELLOW)
                bg = pygame.Surface((t.get_width() + 24, 44), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 160))
                screen.blit(bg, (SCREEN_W // 2 - bg.get_width() // 2, SCREEN_H // 2 - 22))
                screen.blit(t,  (SCREEN_W // 2 - t.get_width()  // 2, SCREEN_H // 2 - 12))

            dibujar_hud(jugador, oleada, font_sm, corazon_img)

            if state == PAUSED:
                pantalla_pausa(font_big, font_sm, jugador)

        elif state == GAMEOVER:
            pantalla_gameover(font_big, font_sm,
                              jugador.score if jugador else 0, oleada)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
