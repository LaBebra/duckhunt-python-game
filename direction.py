"""
Direction — simple enumeration of movement directions.
Using IntEnum keeps backward-compat with integer comparisons (KISS).
"""

from enum import IntEnum


class Direction(IntEnum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4
    HORIZONTAL = 5
    VERTICAL = 6
