"""
Target — один качур, що рухається по екрану.

Відповідальність (SRP):
  - зберігати позицію / скін
  - рухатися згідно з direction та speed
  - повідомляти про піксельне влучання

Не знає про рахунок, постріли чи фазу гри.
"""

import random
import pygame
from constants import Window
from direction import Direction


class Target:
    def __init__(self, x: int, y: int, direction: Direction,
                 skins: list[pygame.Surface], speed: float) -> None:
        self._x = x
        self._y = y
        self._direction = direction
        self._speed = speed
        self._skin: pygame.Surface = random.choice(skins)
        self._mask: pygame.mask.Mask = pygame.mask.from_surface(self._skin)

    def move(self, dt: int) -> None:
        if self._direction == Direction.HORIZONTAL:
            self._x += self._speed
            if self._x > Window.WIDTH:
                self._x = -self._skin.get_width()

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self._skin, (self._x, self._y))

    def was_hit(self, mouse_pos: tuple[int, int]) -> bool:
        offset_x = int(mouse_pos[0] - self._x)
        offset_y = int(mouse_pos[1] - self._y)
        w, h = self._skin.get_size()
        if 0 <= offset_x < w and 0 <= offset_y < h:
            return bool(self._mask.get_at((offset_x, offset_y)))
        return False
