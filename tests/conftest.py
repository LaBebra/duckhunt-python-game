"""
conftest.py — глобальна конфігурація pytest для Duck Hunt.

Налаштовує headless-режим для pygame ДО будь-якого імпорту модулів гри,
щоб pygame.display.init() та pygame.mixer.init() не шукали реальний дисплей
і аудіодрайвер (необхідно для CI та для запуску тестів без графічного середовища).

Порядок важливий: змінні середовища мають бути встановлені до першого
виклику `import pygame`, тому цей файл виконується раніше за будь-який тест.
"""

import os

# SDL_VIDEODRIVER=dummy  — pygame використовує фіктивний дисплей замість реального
# SDL_AUDIODRIVER=dummy  — pygame використовує порожній аудіодрайвер
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
