"""
Точка входу — мінімальний main.py (KISS).

Парсить аргументи → передає Settings у Game → запускає.
"""

from cli import parse_settings
from game import Game

if __name__ == "__main__":
    settings = parse_settings()
    Game(settings).run()
