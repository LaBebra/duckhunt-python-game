"""
HUD — рахунок і постріли у банері + оверлей паузи.

Відповідальність (SRP): лише відображення; читає GameState, не змінює.
Не малює кнопки — вони є частиною спрайту banner.png.
"""

import pygame
from game_state import GameState, Phase
from buttons import ButtonBar


class HUD:
    # Оригінальні позиції тексту з banner.png
    _SCORE_POS = (300, 565)
    _SHOTS_POS = (300, 605)
    _COLOR     = "black"

    # Напівпрозорий оверлей паузи поверх ігрової зони
    _OVERLAY_COLOR    = (0, 0, 0, 160)
    _PAUSE_TEXT       = "— ПАУЗА —"
    _PAUSE_TEXT_COLOR = (255, 255, 255)

    def __init__(self, font: pygame.font.Font) -> None:
        self._font       = font
        self._btn_bar    = ButtonBar()
        self._pause_font = pygame.font.Font(None, 72)

    @property
    def button_bar(self) -> ButtonBar:
        return self._btn_bar

    def draw(self, screen: pygame.Surface, state: GameState) -> None:
        self._blit(screen,
                   f"Points: {state.points} / {state.win_score}",
                   self._SCORE_POS)
        self._blit(screen,
                   f"Shots left: {state.shots_left}",
                   self._SHOTS_POS)

        if state.is_paused:
            self._draw_pause_overlay(screen)

    def _blit(self, screen: pygame.Surface, text: str,
              pos: tuple[int, int]) -> None:
        surface = self._font.render(text, True, self._COLOR)
        screen.blit(surface, pos)

    def _draw_pause_overlay(self, screen: pygame.Surface) -> None:
        from constants import GameConfig
        overlay = pygame.Surface(
            (screen.get_width(), GameConfig.BANNER_Y), pygame.SRCALPHA
        )
        overlay.fill(self._OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        text_surf = self._pause_font.render(
            self._PAUSE_TEXT, True, self._PAUSE_TEXT_COLOR
        )
        text_rect = text_surf.get_rect(
            center=(screen.get_width() // 2, GameConfig.BANNER_Y // 2)
        )
        screen.blit(text_surf, text_rect)
