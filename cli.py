"""
cli.py — парсинг аргументів командного рядка.

Відповідальність (SRP): лише читає argv і повертає Settings.
Не знає про pygame, Game чи будь-яку ігрову логіку.

Використання:
    python main.py --difficulty hard --bg-color 102,153,51 --shots 30 --mute
"""

import argparse
from dataclasses import dataclass


# ------------------------------------------------------------------ #
# Difficulty presets                                                    #
# ------------------------------------------------------------------ #

@dataclass(frozen=True)
class DifficultyPreset:
    shots: int
    target_speed: float
    target_count: int


DIFFICULTY_PRESETS: dict[str, DifficultyPreset] = {
    "easy":   DifficultyPreset(shots=30, target_speed=1.5, target_count=8),
    "normal": DifficultyPreset(shots=20, target_speed=2.0, target_count=12),
    "hard":   DifficultyPreset(shots=15, target_speed=3.5, target_count=12),
}


# ------------------------------------------------------------------ #
# Settings — єдиний об'єкт конфігурації, що передається в Game         #
# ------------------------------------------------------------------ #

@dataclass(frozen=True)
class Settings:
    difficulty: str
    shots: int
    target_speed: float
    target_count: int
    win_score: int                          # мінімум балів для перемоги
    bg_color: tuple[int, int, int] | None   # None → використати зображення
    mute: bool
    volume: float


# ------------------------------------------------------------------ #
# Parser                                                                #
# ------------------------------------------------------------------ #

def _parse_color(value: str) -> tuple[int, int, int]:
    """Перетворює '255,0,128' або '#ff0080' у кортеж RGB."""
    value = value.strip()
    if value.startswith("#"):
        hex_val = value.lstrip("#")
        if len(hex_val) != 6:
            raise argparse.ArgumentTypeError(
                f"Невірний HEX колір '{value}'. Очікується #RRGGBB."
            )
        r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
    else:
        parts = value.split(",")
        if len(parts) != 3:
            raise argparse.ArgumentTypeError(
                f"Невірний колір '{value}'. Формат: R,G,B або #RRGGBB."
            )
        try:
            r, g, b = (int(p.strip()) for p in parts)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Компоненти кольору мають бути цілими числами: '{value}'."
            )
    for component, name in ((r, "R"), (g, "G"), (b, "B")):
        if not (0 <= component <= 255):
            raise argparse.ArgumentTypeError(
                f"Компонент {name}={component} виходить за межі 0–255."
            )
    return (r, g, b)


def parse_settings(argv: list[str] | None = None) -> Settings:
    """Парсить argv та повертає Settings з урахуванням пресетів складності."""

    parser = argparse.ArgumentParser(
        prog="duck-hunt",
        description="Duck Hunt — аргументи командного рядка",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Приклади:
  python main.py
  python main.py --difficulty hard
  python main.py --difficulty easy --shots 40
  python main.py --win-score 50
  python main.py --bg-color 30,144,255
  python main.py --bg-color "#1e90ff"
  python main.py --mute
  python main.py --volume 0.5 --difficulty hard --win-score 80
        """,
    )

    parser.add_argument(
        "--difficulty", "-d",
        choices=list(DIFFICULTY_PRESETS.keys()),
        default="normal",
        metavar="РІВЕНЬ",
        help="Рівень складності: easy, normal, hard  (за замовч.: normal)",
    )
    parser.add_argument(
        "--shots", "-s",
        type=int,
        default=None,
        metavar="N",
        help="Перевизначити кількість пострілів (ігнорує пресет складності)",
    )
    parser.add_argument(
        "--bg-color", "-c",
        type=_parse_color,
        default=None,
        dest="bg_color",
        metavar="R,G,B або #RRGGBB",
        help="Замінити зображення фону суцільним кольором",
    )
    parser.add_argument(
        "--win-score", "-w",
        type=int,
        default=None,
        dest="win_score",
        metavar="БАЛИ",
        help=(
            "Мінімум балів для перемоги (за замовч.: кількість цілей × 10, "
            "тобто треба збити всіх качок)"
        ),
    )
    parser.add_argument(
        "--mute", "-m",
        action="store_true",
        default=False,
        help="Вимкнути весь звук",
    )
    parser.add_argument(
        "--volume", "-v",
        type=float,
        default=0.1,
        metavar="0.0–1.0",
        help="Гучність звуків (за замовч.: 0.1)",
    )

    args = parser.parse_args(argv)

    preset = DIFFICULTY_PRESETS[args.difficulty]

    shots = args.shots if args.shots is not None else preset.shots

    # За замовчуванням — треба збити всіх качок (максимально можливий рахунок)
    default_win_score = preset.target_count * 10
    win_score = args.win_score if args.win_score is not None else default_win_score

    volume = max(0.0, min(1.0, args.volume))
    if args.mute:
        volume = 0.0

    return Settings(
        difficulty=args.difficulty,
        shots=shots,
        target_speed=preset.target_speed,
        target_count=preset.target_count,
        win_score=win_score,
        bg_color=args.bg_color,
        mute=args.mute,
        volume=volume,
    )
