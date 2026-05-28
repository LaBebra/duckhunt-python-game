"""
buttons.py — невидимі хітбокси поверх кнопок PAUSE і RESTART з banner.png.

Кнопки намальовані прямо на спрайті банера — ми не малюємо нічого зайвого,
лише обробляємо кліки по їх точним координатам (SRP, KISS).

Координати виміряні піксельно з banner.png (800×178, відображається з y=500):
  PAUSE:   x=628..762, y_banner=56..99  → абс. y=556..599
  RESTART: x=628..762, y_banner=105..148 → абс. y=605..648
"""

import pygame

CMD_PAUSE   = "pause"
CMD_RESTART = "restart"

# Абсолютні координати в координатах вікна (banner_y = 500)
_BANNER_Y = 500

_RECTS: dict[str, pygame.Rect] = {
    CMD_PAUSE:   pygame.Rect(628, _BANNER_Y + 56,  135, 44),
    CMD_RESTART: pygame.Rect(628, _BANNER_Y + 105, 135, 44),
}


class ButtonBar:
    """
    Перехоплює кліки по кнопках банера.
    Нічого не малює — зовнішній вигляд забезпечує спрайт banner.png.
    """

    def handle_click(self, pos: tuple[int, int]) -> str | None:
        """Повертає CMD_PAUSE, CMD_RESTART або None."""
        for command, rect in _RECTS.items():
            if rect.collidepoint(pos):
                return command
        return None
