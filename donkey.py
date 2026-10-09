#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
DONKEY.PY - Remake en Python de DONKEY.BAS (PC DOS, 1981)
Inspirado en el juego original de Bill Gates & Neil Konzen.
Reimplementación independiente ("clean-room") con Pygame.
No contiene código original ni está afiliado a IBM ni a Microsoft.
Licencia MIT - ver archivo LICENSE.
"""

from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple

import pygame


# ─────────────────────────────────────────────
#  CONSTANTES Y CONFIGURACIÓN
# ─────────────────────────────────────────────
SCREEN_W: int = 640
SCREEN_H: int = 480
FPS: int = 60

# Paleta CGA fiel al original (modo CGA Palette 1)
BLACK   = (0,   0,   0)
CYAN    = (0,   170, 170)
MAGENTA = (170, 0,   170)
WHITE   = (170, 170, 170)
BWHITE  = (255, 255, 255)
BGREEN  = (0,   255, 0)
BYELLOW = (255, 255, 0)
BRED    = (255, 85,  85)
BBLUE   = (85,  85,  255)
DARK_GREEN = (0, 100, 0)

# Carretera
ROAD_X      = 160
ROAD_W      = 320
ROAD_H      = SCREEN_H - 60
ROAD_TOP    = 40
LANE_W      = ROAD_W // 2
LEFT_LANE_X = ROAD_X
RIGHT_LANE_X = ROAD_X + LANE_W

# Sprites
CAR_W, CAR_H = 44, 60
DNK_W, DNK_H = 44, 52

# Velocidades (px/s)
DONKEY_BASE_SPEED: float = 140.0
CAR_CREEP_SPEED: float = 8.0    # px/s que sube el coche
CAR_RESET_Y: int = ROAD_TOP + ROAD_H - CAR_H - 10
CAR_TOP_LIMIT: int = ROAD_TOP + 60


# ─────────────────────────────────────────────
#  DIBUJO DE SPRITES EN PYGAME (sin imágenes externas)
# ─────────────────────────────────────────────
def make_car_surface() -> pygame.Surface:
    """Dibuja un coche de perfil (vista cenital), fiel al CGA original."""
    s = pygame.Surface((CAR_W, CAR_H), pygame.SRCALPHA)
    # Carrocería
    pygame.draw.rect(s, CYAN,    (4, 4, CAR_W-8, CAR_H-8), border_radius=4)
    # Ventana delantera
    pygame.draw.rect(s, BWHITE, (8, 6, CAR_W-16, 14), border_radius=2)
    # Ventana trasera
    pygame.draw.rect(s, BWHITE, (8, CAR_H-20, CAR_W-16, 10), border_radius=2)
    # Ruedas
    wheel_color = BLACK
    for wx, wy in [(0,8),(CAR_W-8,8),(0,CAR_H-16),(CAR_W-8,CAR_H-16)]:
        pygame.draw.rect(s, wheel_color, (wx, wy, 8, 14), border_radius=2)
    # Línea central del capó
    pygame.draw.line(s, WHITE, (CAR_W//2, 22), (CAR_W//2, CAR_H-24), 2)
    return s


def make_donkey_surface() -> pygame.Surface:
    """Dibuja un burro (vista cenital), fiel a la forma del CGA original."""
    s = pygame.Surface((DNK_W, DNK_H), pygame.SRCALPHA)
    body_color  = (139, 90, 43)    # marrón
    ear_color   = (180, 120, 60)
    eye_color   = BLACK

    # Cuerpo principal
    pygame.draw.ellipse(s, body_color, (6, 10, DNK_W-12, DNK_H-16))
    # Cabeza
    pygame.draw.ellipse(s, body_color, (DNK_W//2-8, 2, 16, 14))
    # Orejas largas (característico del burro)
    pygame.draw.polygon(s, ear_color, [(DNK_W//2-10, 2),(DNK_W//2-14,  -6),(DNK_W//2-6, 2)])
    pygame.draw.polygon(s, ear_color, [(DNK_W//2+10, 2),(DNK_W//2+14, -6),(DNK_W//2+6, 2)])
    # Ojos
    pygame.draw.circle(s, eye_color, (DNK_W//2-4, 7), 2)
    pygame.draw.circle(s, eye_color, (DNK_W//2+4, 7), 2)
    # Patas (4)
    leg_color = (100, 60, 20)
    legs = [(8, DNK_H-14),(16, DNK_H-12),(DNK_W-16, DNK_H-12),(DNK_W-8, DNK_H-14)]
    for lx, ly in legs:
        pygame.draw.rect(s, leg_color, (lx-3, ly, 6, 12), border_radius=2)
    # Cola
    pygame.draw.line(s, body_color, (DNK_W//2, DNK_H-6), (DNK_W//2+8, DNK_H+2), 3)
    return s


def make_explosion_particles(cx: int, cy: int, count: int = 30) -> List[dict]:
    """Genera partículas de explosión al estilo DONKEY.BAS."""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(60, 220)
        color = random.choice([BRED, BYELLOW, BWHITE, CYAN, MAGENTA])
        particles.append({
            "x": float(cx), "y": float(cy),
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.uniform(0.6, 1.4),
            "max_life": 1.4,
            "color": color,
            "size": random.randint(3, 8),
        })
    return particles


# ─────────────────────────────────────────────
#  ESTADOS DEL JUEGO
# ─────────────────────────────────────────────
class GameState(Enum):
    TITLE   = auto()
    PLAYING = auto()
    BOOM    = auto()
    MISS    = auto()


# ─────────────────────────────────────────────
#  ENTIDADES
# ─────────────────────────────────────────────
@dataclass
class Car:
    x: float = float(LEFT_LANE_X + LANE_W // 2 - CAR_W // 2)
    y: float = float(CAR_RESET_Y)
    lane: int = 0   # 0=izquierda, 1=derecha

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), CAR_W, CAR_H)

    def lane_x(self) -> float:
        lx = LEFT_LANE_X if self.lane == 0 else RIGHT_LANE_X
        return float(lx + LANE_W // 2 - CAR_W // 2)

    def switch_lane(self) -> None:
        self.lane = 1 - self.lane

    def reset(self) -> None:
        self.y = float(CAR_RESET_Y)
        self.x = self.lane_x()

    def update(self, dt: float) -> None:
        """El coche sube lentamente (reduciendo tiempo de reacción)."""
        self.y -= CAR_CREEP_SPEED * dt
        # Interpola horizontalmente al centro del carril (animación suave)
        target_x = self.lane_x()
        self.x += (target_x - self.x) * min(1.0, dt * 12)


@dataclass
class Donkey:
    x: float = 0.0
    y: float = float(ROAD_TOP - DNK_H)
    lane: int = 0
    speed: float = DONKEY_BASE_SPEED

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), DNK_W, DNK_H)

    def reset(self, speed_multiplier: float = 1.0) -> None:
        self.lane = random.randint(0, 1)
        lx = LEFT_LANE_X if self.lane == 0 else RIGHT_LANE_X
        self.x = float(lx + LANE_W // 2 - DNK_W // 2)
        self.y = float(ROAD_TOP - DNK_H - random.randint(0, 60))
        self.speed = DONKEY_BASE_SPEED * speed_multiplier

    def update(self, dt: float) -> None:
        self.y += self.speed * dt

    def is_past_bottom(self) -> bool:
        return self.y > ROAD_TOP + ROAD_H + 20


# ─────────────────────────────────────────────
#  RENDERIZADOR DE TEXTO (estilo CGA retro)
# ─────────────────────────────────────────────
class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font_big   = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_med   = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 16)
        self.font_tiny  = pygame.font.SysFont("consolas", 13)

    def text(
        self,
        msg: str,
        font: pygame.font.Font,
        color: Tuple[int,int,int],
        pos: Tuple[int,int],
        anchor: str = "topleft",
    ) -> None:
        surf = font.render(msg, True, color)
        rect = surf.get_rect(**{anchor: pos})
        self.screen.blit(surf, rect)

    def draw_road(self) -> None:
        """Carretera con zonas laterales y línea central discontinua."""
        # Fondo negro
        self.screen.fill(BLACK)
        # Zonas verdes laterales
        pygame.draw.rect(self.screen, DARK_GREEN, (0, ROAD_TOP, ROAD_X, ROAD_H))
        pygame.draw.rect(self.screen, DARK_GREEN,
                         (ROAD_X + ROAD_W, ROAD_TOP, SCREEN_W - ROAD_X - ROAD_W, ROAD_H))
        # Carretera gris
        pygame.draw.rect(self.screen, (55,55,55), (ROAD_X, ROAD_TOP, ROAD_W, ROAD_H))
        # Bordes blancos de la carretera
        pygame.draw.line(self.screen, BWHITE,
                         (ROAD_X, ROAD_TOP), (ROAD_X, ROAD_TOP+ROAD_H), 3)
        pygame.draw.line(self.screen, BWHITE,
                         (ROAD_X+ROAD_W, ROAD_TOP), (ROAD_X+ROAD_W, ROAD_TOP+ROAD_H), 3)
        # Línea central discontinua
        dash = 24
        gap  = 18
        cx   = ROAD_X + ROAD_W // 2
        y    = ROAD_TOP
        while y < ROAD_TOP + ROAD_H:
            pygame.draw.rect(self.screen, WHITE, (cx-2, y, 4, dash))
            y += dash + gap

    def draw_title_screen(self, tick: int) -> None:
        """Pantalla de título inspirada en el original de 1981."""
        self.screen.fill(BLACK)
        cx = SCREEN_W // 2

        # Caja con bordes (estilo box-drawing chars de la época)
        bx, by, bw, bh = cx-160, 80, 320, 180
        pygame.draw.rect(self.screen, BGREEN, (bx, by, bw, bh), 3, border_radius=4)

        self.text("DONKEY.PY",     self.font_big,   BWHITE,  (cx, by+18),    "midtop")
        self.text("Python Remake",  self.font_med,   BWHITE,  (cx, by+56),    "midtop")
        self.text("D  O  N  K  E  Y", self.font_big, BYELLOW, (cx, by+90),   "midtop")
        self.text("Version 1.10",  self.font_small, BWHITE,  (cx, by+128),   "midtop")
        self.text("Free software - MIT License", self.font_tiny, WHITE,
                  (cx, by+155), "midtop")

        # Parpadeo "Press SPACE"
        if (tick // 30) % 2 == 0:
            self.text("Press SPACE to play   ESC to exit",
                      self.font_small, BYELLOW, (cx, SCREEN_H-60), "midtop")

    def draw_hud(self, donkey_score: int, driver_score: int, speed_level: int) -> None:
        """Panel lateral izquierdo (Donkey) y derecho (Driver)."""
        left_cx  = ROAD_X // 2
        right_cx = ROAD_X + ROAD_W + (SCREEN_W - ROAD_X - ROAD_W) // 2

        # ── Lado izquierdo: Donkey ──
        self.text("Donkey", self.font_med, CYAN,   (left_cx, ROAD_TOP+10),  "midtop")
        self.text(str(donkey_score), self.font_big, BWHITE, (left_cx, ROAD_TOP+38), "midtop")

        # ── Lado derecho: Driver ──
        self.text("Driver", self.font_med, BGREEN, (right_cx, ROAD_TOP+10), "midtop")
        self.text(str(driver_score), self.font_big, BWHITE, (right_cx, ROAD_TOP+38), "midtop")

        # Instrucciones lado derecho
        instrs = ["SPACE:", "switch lanes", "", "ESC:", "exit"]
        for i, line in enumerate(instrs):
            color = BYELLOW if ":" in line else WHITE
            self.text(line, self.font_tiny, color,
                      (right_cx, ROAD_TOP + ROAD_H - 90 + i*16), "midtop")

        # Nivel de dificultad
        self.text(f"Speed x{speed_level}", self.font_tiny, MAGENTA,
                  (left_cx, ROAD_TOP + ROAD_H - 40), "midtop")

    def draw_boom(self) -> None:
        self.text("BOOM!", self.font_big, BRED,
                  (ROAD_X // 2, SCREEN_H // 2 - 14), "midtop")

    def draw_miss(self) -> None:
        right_cx = ROAD_X + ROAD_W + (SCREEN_W - ROAD_X - ROAD_W) // 2
        self.text("Donkey", self.font_med, BYELLOW,
                  (right_cx, SCREEN_H//2 - 28), "midtop")
        self.text("loses!", self.font_med, BYELLOW,
                  (right_cx, SCREEN_H//2),      "midtop")


# ─────────────────────────────────────────────
#  JUEGO PRINCIPAL
# ─────────────────────────────────────────────
class DonkeyGame:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("DONKEY.PY  —  DONKEY.BAS 1981 Remake")
        self.clock = pygame.time.Clock()

        # Sprites
        self.car_surf   = make_car_surface()
        self.donkey_surf = make_donkey_surface()

        # Renderer
        self.rdr = Renderer(self.screen)

        # Estado
        self.state: GameState = GameState.TITLE
        self.tick: int = 0       # contador de frames para animaciones

        # Entidades
        self.car    = Car()
        self.donkey = Donkey()

        # Puntuaciones
        self.donkey_score: int = 0
        self.driver_score: int = 0
        self.speed_level:  int = 1      # sube con cada esquiva del driver

        # Partículas de explosión
        self.particles: List[dict] = []

        # Timers (en segundos)
        self.state_timer: float = 0.0

        # Iniciar primer burro
        self.donkey.reset(self.speed_level)

    # ── Bucle principal ──────────────────────────────────────────
    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.tick += 1
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

    # ── Gestión de eventos ────────────────────────────────────────
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._quit()
                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.TITLE:
                        self._start_game()
                    elif self.state == GameState.PLAYING:
                        self.car.switch_lane()

    # ── Lógica de actualización ───────────────────────────────────
    def _update(self, dt: float) -> None:
        if self.state == GameState.TITLE:
            return

        if self.state in (GameState.BOOM, GameState.MISS):
            self.state_timer -= dt
            self._update_particles(dt)
            if self.state_timer <= 0:
                self._reset_round()
            return

        # ── Estado PLAYING ──
        self.car.update(dt)
        self.donkey.update(dt)
        self._update_particles(dt)

        # Si el coche llega muy arriba → driver gana un punto
        if self.car.y <= CAR_TOP_LIMIT:
            self.driver_score += 1
            self.speed_level = min(self.driver_score + 1, 8)
            self._enter_miss()
            return

        # Colisión coche-burro
        if self.car.rect.colliderect(self.donkey.rect):
            self.donkey_score += 1
            boom_center = (
                self.car.rect.centerx,
                min(self.car.rect.centery, self.donkey.rect.centery)
            )
            self.particles = make_explosion_particles(*boom_center, count=40)
            self._enter_boom()
            return

        # Burro sale por abajo sin colisión
        if self.donkey.is_past_bottom():
            self.driver_score += 1
            self.speed_level = min(self.driver_score + 1, 8)
            self._enter_miss()

    def _update_particles(self, dt: float) -> None:
        """Actualiza posición y vida de cada partícula."""
        alive = []
        for p in self.particles:
            p["x"]    += p["vx"] * dt
            p["y"]    += p["vy"] * dt
            p["vy"]   += 120 * dt   # gravedad
            p["life"] -= dt
            if p["life"] > 0:
                alive.append(p)
        self.particles = alive

    # ── Transiciones de estado ────────────────────────────────────
    def _start_game(self) -> None:
        self.state        = GameState.PLAYING
        self.donkey_score = 0
        self.driver_score = 0
        self.speed_level  = 1
        self.car.reset()
        self.donkey.reset(self.speed_level)

    def _enter_boom(self) -> None:
        self.state       = GameState.BOOM
        self.state_timer = 2.0

    def _enter_miss(self) -> None:
        self.state       = GameState.MISS
        self.state_timer = 1.5

    def _reset_round(self) -> None:
        """Reiniciar posiciones tras BOOM o MISS."""
        self.car.reset()
        self.donkey.reset(self.speed_level)
        self.particles = []
        self.state     = GameState.PLAYING

    # ── Dibujo ────────────────────────────────────────────────────
    def _draw(self) -> None:
        if self.state == GameState.TITLE:
            self.rdr.draw_title_screen(self.tick)
            return

        # Carretera
        self.rdr.draw_road()

        # Sprites (solo si no hay explosión total)
        if self.state != GameState.BOOM or self.state_timer > 1.2:
            self.screen.blit(self.car_surf,    (int(self.car.x),    int(self.car.y)))
        if self.state != GameState.BOOM or self.state_timer > 1.2:
            self.screen.blit(self.donkey_surf, (int(self.donkey.x), int(self.donkey.y)))

        # Partículas de explosión
        for p in self.particles:
            alpha = int(255 * p["life"] / p["max_life"])
            alpha = max(0, min(255, alpha))
            size  = max(1, int(p["size"] * p["life"] / p["max_life"]))
            pygame.draw.circle(
                self.screen, p["color"],
                (int(p["x"]), int(p["y"])), size
            )

        # HUD
        self.rdr.draw_hud(self.donkey_score, self.driver_score, self.speed_level)

        # Mensajes de estado
        if self.state == GameState.BOOM:
            self.rdr.draw_boom()
        elif self.state == GameState.MISS:
            self.rdr.draw_miss()

    # ── Salir ─────────────────────────────────────────────────────
    @staticmethod
    def _quit() -> None:
        pygame.quit()
        sys.exit()


# ─────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ─────────────────────────────────────────────
if __name__ == "__main__":
    DonkeyGame().run()
