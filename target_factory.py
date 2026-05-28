"""
TargetFactory — створює список Target-об'єктів для раунду.

OCP: нові конфігурації рівнів додаються без зміни існуючого коду.
SRP: знає лише як будувати цілі, не як їх рухати чи малювати.

Отримує speed та target_count з Settings (DIP — не читає глобалів).
"""

import random
from target import Target
from direction import Direction


# Повний пул можливих позицій спавну
_SPAWN_POOL: list[tuple[int, int, Direction]] = [
    (50,    10,  Direction.HORIZONTAL),
    (150,   76,  Direction.HORIZONTAL),
    (50,   142,  Direction.HORIZONTAL),
    (150,  208,  Direction.HORIZONTAL),
    (50,   274,  Direction.HORIZONTAL),
    (100,  340,  Direction.HORIZONTAL),
    (-350,  10,  Direction.HORIZONTAL),
    (-250,  76,  Direction.HORIZONTAL),
    (-350, 142,  Direction.HORIZONTAL),
    (-250, 208,  Direction.HORIZONTAL),
    (-350, 274,  Direction.HORIZONTAL),
    (-250, 340,  Direction.HORIZONTAL),
]


class TargetFactory:
    """Будує цілі з урахуванням параметрів складності."""

    @classmethod
    def create(cls, skins, speed: float, count: int) -> list[Target]:
        """
        Вибирає `count` позицій з пулу (або повторює, якщо count > пул)
        і створює Target з заданою швидкістю.
        """
        pool = _SPAWN_POOL * ((count // len(_SPAWN_POOL)) + 1)
        chosen = random.sample(pool, min(count, len(pool)))
        return [Target(x, y, d, skins, speed) for x, y, d in chosen]
