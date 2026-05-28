"""
WorldRenderer — малює фонові шари.

Якщо Settings.bg_color задано — замість зображення заливає фон кольором.
Відповідальність (SRP): лише рендеринг фону.
"""

import pygame
from constants import GameConfig


class WorldRenderer:
    def __init__(self, background: pygame.Surface, banner: pygame.Surface,
                 bg_color: tuple[int, int, int] | None = None) -> None:
        self._background = background
        self._banner = banner
        self._bg_color = bg_color

    def draw(self, screen: pygame.Surface) -> None:
        if self._bg_color is not None:
            # Заливаємо лишеігрову зону (вище банера)
            play_area = pygame.Rect(0, 0, screen.get_width(), GameConfig.BANNER_Y)
            screen.fill(self._bg_color, play_area)
        else:
            screen.blit(self._background, (0, 0))
        screen.blit(self._banner, (0, GameConfig.BANNER_Y))
