"""
Game constants — pure data, no pygame dependencies.
Keeps configuration centralised (DRY) and side-effect-free (KISS).
"""


class Window:
    TITLE = "Duck Hunt"
    WIDTH = 800
    HEIGHT = 678
    FPS = 60


class GameConfig:
    STARTING_SHOTS = 20
    POINTS_PER_HIT = 10
    TARGET_SPEED = 2
    BANNER_Y = 500          # Y-coordinate where the grass banner starts
    GUN_PIVOT_X = Window.WIDTH / 2
    GUN_PIVOT_Y = Window.HEIGHT - 178
    GUN_BLIT_OFFSET_RIGHT = (Window.WIDTH / 2 - 30, Window.HEIGHT - 250)
    GUN_BLIT_OFFSET_LEFT = (Window.WIDTH / 2 - 90, Window.HEIGHT - 250)
    LASER_RADIUS = 5
    SOUND_VOLUME = 0.1


ASSET_PATHS = {
    "icon":       "assets/screen/icon.png",
    "background": "assets/screen/background.jpg",
    "banner":     "assets/screen/banner.png",
    "gameover":   "assets/screen/gameover.png",
    "winner":     "assets/screen/winner.png",
    "gun":        "assets/guns/gun.png",
    "font":       "assets/font/myFont.ttf",
    "duck_shot":  "assets/sounds/duck.mp3",
    "gameover_sound": "assets/sounds/gameover.ogg",
    "winner_sound":   "assets/sounds/winner.ogg",
    "duck_skins": [
        "assets/targets/duck-1-1.png",
        "assets/targets/duck-1-2.png",
        "assets/targets/duck-2-1.png",
        "assets/targets/duck-2-2.png",
        "assets/targets/duck-3-1.png",
        "assets/targets/duck-3-2.png",
    ],
}
