"""
AssetLoader — завантажує всі pygame-ресурси після pygame.init().

Отримує Settings для налаштування гучності (DIP — не читає глобалів).
"""

import pygame
from constants import ASSET_PATHS
from cli import Settings


class AssetLoader:
    def __init__(self, settings: Settings) -> None:
        self.icon       = pygame.image.load(ASSET_PATHS["icon"])
        self.background = pygame.image.load(ASSET_PATHS["background"])
        self.banner     = pygame.image.load(ASSET_PATHS["banner"])
        self.gameover   = pygame.image.load(ASSET_PATHS["gameover"])
        self.winner     = pygame.image.load(ASSET_PATHS["winner"])
        self.gun        = pygame.image.load(ASSET_PATHS["gun"])
        self.font       = pygame.font.Font(ASSET_PATHS["font"], 32)

        self.duck_skins: list[pygame.Surface] = [
            pygame.image.load(path) for path in ASSET_PATHS["duck_skins"]
        ]

        self.duck_shot      = self._load_sound("duck_shot",      settings.volume)
        self.gameover_sound = self._load_sound("gameover_sound", settings.volume)
        self.winner_sound   = self._load_sound("winner_sound",   settings.volume)

    def _load_sound(self, key: str, volume: float) -> pygame.mixer.Sound:
        sound = pygame.mixer.Sound(ASSET_PATHS[key])
        sound.set_volume(volume)
        return sound
