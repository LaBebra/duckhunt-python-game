"""
Game — головний оркестратор.

Відповідальність (SRP):
  - ініціалізація pygame
  - головний цикл
  - делегування рендерингу, стану, введення спеціалізованим об'єктам

Отримує Settings через конструктор (DIP).
"""

import pygame
from constants import Window, GameConfig
from cli import Settings
from asset_loader import AssetLoader
from game_state import GameState, Phase
from target_factory import TargetFactory
from world_renderer import WorldRenderer
from gun_renderer import GunRenderer
from hud import HUD
from buttons import CMD_PAUSE, CMD_RESTART
from target import Target


class Game:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

        pygame.init()
        self._screen = pygame.display.set_mode((Window.WIDTH, Window.HEIGHT))
        self._clock  = pygame.time.Clock()

        self._assets = AssetLoader(settings)
        pygame.display.set_icon(self._assets.icon)
        pygame.display.set_caption(
            f"{Window.TITLE}  [{settings.difficulty.upper()}]"
        )

        self._world = WorldRenderer(
            self._assets.background,
            self._assets.banner,
            bg_color=settings.bg_color,
        )
        self._gun = GunRenderer(self._assets.gun)
        self._hud = HUD(self._assets.font)

        self._state:   GameState   = self._fresh_state()
        self._targets: list[Target] = self._spawn_targets()

    # ------------------------------------------------------------------ #
    # Public entry point                                                    #
    # ------------------------------------------------------------------ #

    def run(self) -> None:
        while True:
            dt = self._clock.tick(Window.FPS)
            self._handle_events()
            self._update(dt)
            self._render()

    # ------------------------------------------------------------------ #
    # Ініціалізація                                                         #
    # ------------------------------------------------------------------ #

    def _fresh_state(self) -> GameState:
        return GameState(
            points=0,
            shots_left=self._settings.shots,
            phase=Phase.PLAYING,
            win_score=self._settings.win_score,
        )

    def _spawn_targets(self) -> list[Target]:
        return TargetFactory.create(
            self._assets.duck_skins,
            speed=self._settings.target_speed,
            count=self._settings.target_count,
        )

    def _restart(self) -> None:
        self._state   = self._fresh_state()
        self._targets = self._spawn_targets()
        self._screen.fill((0, 0, 0))
        pygame.display.update()

    # ------------------------------------------------------------------ #
    # Обробка подій                                                         #
    # ------------------------------------------------------------------ #

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._on_mouse_click(pygame.mouse.get_pos())

            if event.type == pygame.KEYDOWN:
                self._on_key(event.key)

    def _on_key(self, key: int) -> None:
        if key in (pygame.K_p, pygame.K_ESCAPE):
            self._state.toggle_pause()

        if key == pygame.K_SPACE and self._state.is_over:
            self._restart()

    def _on_mouse_click(self, pos: tuple[int, int]) -> None:
        # 1. Кнопки банера мають пріоритет (незалежно від фази)
        command = self._hud.button_bar.handle_click(pos)
        if command == CMD_PAUSE:
            self._state.toggle_pause()
            return
        if command == CMD_RESTART:
            self._restart()
            return

        # 2. Постріл — лише під час гри, поза банером
        if not self._state.is_playing:
            return
        if pos[1] >= GameConfig.BANNER_Y:
            return
        if not self._state.spend_shot():
            return

        for target in reversed(self._targets):
            if target.was_hit(pos):
                self._assets.duck_shot.play()
                self._state.add_points(GameConfig.POINTS_PER_HIT)
                self._targets.remove(target)
                break

    # ------------------------------------------------------------------ #
    # Оновлення                                                             #
    # ------------------------------------------------------------------ #

    def _update(self, dt: int) -> None:
        if not self._state.is_playing:
            return
        for target in self._targets:
            target.move(dt)
        self._check_end_conditions()

    def _check_end_conditions(self) -> None:
        if self._state.shots_left == 0 and not self._state.score_reached:
            self._state.transition_to(Phase.GAME_OVER)
            self._assets.gameover_sound.play()
        elif self._state.score_reached:
            self._state.transition_to(Phase.WIN)
            self._assets.winner_sound.play()

    # ------------------------------------------------------------------ #
    # Рендеринг                                                             #
    # ------------------------------------------------------------------ #

    def _render(self) -> None:
        if self._state.phase in (Phase.PLAYING, Phase.PAUSED):
            self._render_playing()
        elif self._state.phase == Phase.GAME_OVER:
            self._screen.blit(self._assets.gameover, (0, 0))
        elif self._state.phase == Phase.WIN:
            self._screen.blit(self._assets.winner, (0, 0))
        pygame.display.update()

    def _render_playing(self) -> None:
        self._world.draw(self._screen)
        self._gun.draw(self._screen)
        for target in self._targets:
            target.draw(self._screen)
        # HUD малюється останнім — поверх усього, включно з оверлеєм паузи
        self._hud.draw(self._screen, self._state)
