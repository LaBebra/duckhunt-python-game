"""
GameState — single source of truth for all mutable game state.

Follows SRP: holds state only, contains no rendering or pygame logic.
Avoids scattered globals (DRY).
"""

from dataclasses import dataclass, field
from enum import Enum, auto


class Phase(Enum):
    """All possible game phases, making state transitions explicit (SOLID/OCP)."""
    PLAYING   = auto()
    PAUSED    = auto()
    GAME_OVER = auto()
    WIN       = auto()


@dataclass
class GameState:
    points: int = 0
    shots_left: int = 0
    phase: Phase = Phase.PLAYING
    win_score: int = 0       # мінімум балів, необхідних для перемоги

    @property
    def score_reached(self) -> bool:
        return self.points >= self.win_score

    # ------------------------------------------------------------------ #
    # Queries                                                               #
    # ------------------------------------------------------------------ #

    @property
    def is_playing(self) -> bool:
        return self.phase == Phase.PLAYING

    @property
    def is_paused(self) -> bool:
        return self.phase == Phase.PAUSED

    @property
    def is_over(self) -> bool:
        return self.phase in (Phase.GAME_OVER, Phase.WIN)

    # ------------------------------------------------------------------ #
    # Commands                                                              #
    # ------------------------------------------------------------------ #

    def toggle_pause(self) -> None:
        """Перемикає між PLAYING і PAUSED. Ігнорується поза грою."""
        if self.phase == Phase.PLAYING:
            self.phase = Phase.PAUSED
        elif self.phase == Phase.PAUSED:
            self.phase = Phase.PLAYING

    def spend_shot(self) -> bool:
        """Reduce shot counter by 1.  Returns True if the shot was fired."""
        if self.shots_left > 0:
            self.shots_left -= 1
            return True
        return False

    def add_points(self, value: int) -> None:
        self.points += value

    def transition_to(self, phase: Phase) -> None:
        self.phase = phase
