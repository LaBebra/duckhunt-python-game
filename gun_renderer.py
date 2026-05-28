"""
GunRenderer — draws the rotated gun sprite and laser-dot cursor.

Responsibilities (SRP):
  - rotate and blit the gun sprite toward the cursor
  - draw the laser dot on click

Has NO knowledge of shot count or points (that belongs to GameState).
"""

import math
import pygame
from constants import Window, GameConfig


class GunRenderer:
    def __init__(self, skin: pygame.Surface) -> None:
        self._skin = skin
        self._skin_flipped = pygame.transform.flip(skin, True, False)

    def draw(self, screen: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()

        # Don't render inside the banner area
        if mouse_pos[1] >= GameConfig.BANNER_Y:
            return

        pivot = (GameConfig.GUN_PIVOT_X, GameConfig.GUN_PIVOT_Y)
        dx = mouse_pos[0] - pivot[0]
        dy = mouse_pos[1] - pivot[1]
        slope = dy / dx if dx != 0 else -100_000
        rotation = math.degrees(math.atan(slope))

        if mouse_pos[0] < Window.WIDTH / 2:
            rotated = pygame.transform.rotate(self._skin_flipped, 90 - rotation)
            screen.blit(rotated, GameConfig.GUN_BLIT_OFFSET_LEFT)
        else:
            rotated = pygame.transform.rotate(self._skin, 270 - rotation)
            screen.blit(rotated, GameConfig.GUN_BLIT_OFFSET_RIGHT)

        if pygame.mouse.get_pressed()[0]:
            pygame.draw.circle(screen, pygame.Color("red"), mouse_pos,
                               GameConfig.LASER_RADIUS)
