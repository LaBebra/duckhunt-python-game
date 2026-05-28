"""
test_pygame_modules.py — тести для модулів що потребують pygame.

Покриває:
  • Direction enum
  • Target: рух, wrap-around, was_hit (влучання та промах)
  • TargetFactory: кількість цілей, повторення пулу
  • ButtonBar: кліки по PAUSE, RESTART, поза зонами
  • Constants: значення Window, GameConfig, ASSET_PATHS

Увага: цей файл потребує headless-середовища.
Налаштування через conftest.py (SDL_VIDEODRIVER=dummy).
"""

import os
import pytest
import pygame

from direction import Direction
from constants import Window, GameConfig, ASSET_PATHS


# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Ініціалізує pygame один раз для всієї сесії."""
    pygame.display.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture
def dummy_skin():
    """Повністю білий 40×30 Surface — кожен піксель непрозорий."""
    surf = pygame.Surface((40, 30))
    surf.fill((255, 255, 255))
    return surf


@pytest.fixture
def transparent_skin():
    """Повністю прозорий Surface — жоден піксель не є непрозорим."""
    surf = pygame.Surface((40, 30), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    return surf


@pytest.fixture
def screen():
    """Фіктивний екран для тестів рендерингу."""
    return pygame.Surface((Window.WIDTH, Window.HEIGHT))


# ── Direction ─────────────────────────────────────────────────────────────

class TestDirection:
    def test_horizontal_value(self):
        assert Direction.HORIZONTAL == 5

    def test_vertical_value(self):
        assert Direction.VERTICAL == 6

    def test_left_right_up_down_exist(self):
        assert Direction.LEFT == 1
        assert Direction.RIGHT == 2
        assert Direction.UP == 3
        assert Direction.DOWN == 4

    def test_direction_is_int(self):
        assert isinstance(Direction.HORIZONTAL, int)

    def test_comparison_with_int(self):
        assert Direction.HORIZONTAL == 5
        assert Direction.LEFT != Direction.RIGHT


# ── Target ────────────────────────────────────────────────────────────────

class TestTargetMove:
    def test_horizontal_target_moves_right(self, dummy_skin):
        from target import Target
        t = Target(100, 50, Direction.HORIZONTAL, [dummy_skin], speed=2.0)
        t.move(dt=16)
        assert t._x == pytest.approx(102.0)

    def test_horizontal_target_moves_by_speed(self, dummy_skin):
        from target import Target
        t = Target(0, 0, Direction.HORIZONTAL, [dummy_skin], speed=3.5)
        t.move(dt=16)
        assert t._x == pytest.approx(3.5)

    def test_target_wraps_around_right_edge(self, dummy_skin):
        """Коли качка виходить за правий край — з'являється зліва."""
        from target import Target
        t = Target(Window.WIDTH + 1, 50, Direction.HORIZONTAL, [dummy_skin], speed=2.0)
        t.move(dt=16)
        # після wrap: x = -skin_width = -40
        assert t._x == -dummy_skin.get_width()

    def test_target_wraps_exactly_at_boundary(self, dummy_skin):
        from target import Target
        # x рівно на межі WIDTH → наступний крок викликає wrap
        t = Target(Window.WIDTH - 1, 0, Direction.HORIZONTAL, [dummy_skin], speed=2.0)
        t.move(dt=16)
        assert t._x == -dummy_skin.get_width()

    def test_target_y_does_not_change_on_horizontal_move(self, dummy_skin):
        from target import Target
        t = Target(100, 75, Direction.HORIZONTAL, [dummy_skin], speed=2.0)
        t.move(dt=16)
        assert t._y == 75

    def test_multiple_moves_accumulate(self, dummy_skin):
        from target import Target
        t = Target(0, 0, Direction.HORIZONTAL, [dummy_skin], speed=1.0)
        for _ in range(5):
            t.move(dt=16)
        assert t._x == pytest.approx(5.0)


class TestTargetWasHit:
    def test_hit_center_of_opaque_skin(self, dummy_skin):
        from target import Target
        t = Target(100, 50, Direction.HORIZONTAL, [dummy_skin], speed=2.0)
        # Центр спрайта: (100 + 20, 50 + 15) = (120, 65)
        assert t.was_hit((120, 65)) is True

    def test_hit_top_left_corner(self, dummy_skin):
        from target import Target
        t = Target(100, 50, Direction.HORIZONTAL, [dummy_skin], speed=2.0)
        assert t.was_hit((100, 50)) is True

    def test_miss_outside_rect_left(self, dummy_skin):
        from target import Target
        t = Target(100, 50, Direction.HORIZONTAL, [dummy_skin], speed=2.0)
        assert t.was_hit((99, 65)) is False

    def test_miss_outside_rect_right(self, dummy_skin):
        from target import Target
        t = Target(100, 50, Direction.HORIZONTAL, [dummy_skin], speed=2.0)
        # Ширина скіна 40 → правий край 139, клік у 141
        assert t.was_hit((141, 65)) is False

    def test_miss_outside_rect_top(self, dummy_skin):
        from target import Target
        t = Target(100, 50, Direction.HORIZONTAL, [dummy_skin], speed=2.0)
        assert t.was_hit((120, 49)) is False

    def test_miss_outside_rect_bottom(self, dummy_skin):
        from target import Target
        t = Target(100, 50, Direction.HORIZONTAL, [dummy_skin], speed=2.0)
        # Висота скіна 30 → нижній край 79, клік у 81
        assert t.was_hit((120, 81)) is False

    def test_miss_transparent_pixel(self, transparent_skin):
        """Клік по прозорому пікселю — промах, навіть якщо в межах rect."""
        from target import Target
        t = Target(0, 0, Direction.HORIZONTAL, [transparent_skin], speed=2.0)
        assert t.was_hit((20, 15)) is False

    def test_draw_does_not_raise(self, dummy_skin, screen):
        """draw() не кидає виняток при нормальних умовах."""
        from target import Target
        t = Target(100, 50, Direction.HORIZONTAL, [dummy_skin], speed=2.0)
        t.draw(screen)  # не повинно кидати виняток


# ── TargetFactory ─────────────────────────────────────────────────────────

class TestTargetFactory:
    def test_creates_correct_count(self, dummy_skin):
        from target_factory import TargetFactory
        targets = TargetFactory.create([dummy_skin], speed=2.0, count=8)
        assert len(targets) == 8

    def test_creates_normal_count(self, dummy_skin):
        from target_factory import TargetFactory
        targets = TargetFactory.create([dummy_skin], speed=2.0, count=12)
        assert len(targets) == 12

    def test_creates_hard_count(self, dummy_skin):
        from target_factory import TargetFactory
        targets = TargetFactory.create([dummy_skin], speed=3.5, count=12)
        assert len(targets) == 12

    def test_count_exceeds_pool_repeats(self, dummy_skin):
        """Якщо count > розмір пулу (12), пул повторюється."""
        from target_factory import TargetFactory
        targets = TargetFactory.create([dummy_skin], speed=2.0, count=15)
        assert len(targets) == 15

    def test_count_one(self, dummy_skin):
        from target_factory import TargetFactory
        targets = TargetFactory.create([dummy_skin], speed=2.0, count=1)
        assert len(targets) == 1

    def test_returns_target_objects(self, dummy_skin):
        from target_factory import TargetFactory
        from target import Target
        targets = TargetFactory.create([dummy_skin], speed=2.0, count=3)
        assert all(isinstance(t, Target) for t in targets)

    def test_speed_is_set_on_targets(self, dummy_skin):
        from target_factory import TargetFactory
        targets = TargetFactory.create([dummy_skin], speed=3.5, count=3)
        assert all(t._speed == 3.5 for t in targets)

    def test_all_positions_are_from_pool(self, dummy_skin):
        """Всі позиції Y мають відповідати значенням з _SPAWN_POOL."""
        from target_factory import TargetFactory, _SPAWN_POOL
        valid_ys = {entry[1] for entry in _SPAWN_POOL}
        targets = TargetFactory.create([dummy_skin], speed=2.0, count=12)
        assert all(t._y in valid_ys for t in targets)


# ── ButtonBar ─────────────────────────────────────────────────────────────

class TestButtonBar:
    def test_click_in_pause_zone_returns_pause(self):
        from buttons import ButtonBar, CMD_PAUSE
        bar = ButtonBar()
        # Центр кнопки PAUSE: x=628+67=695, y=500+56+22=578
        assert bar.handle_click((695, 578)) == CMD_PAUSE

    def test_click_in_restart_zone_returns_restart(self):
        from buttons import ButtonBar, CMD_RESTART
        bar = ButtonBar()
        # Центр кнопки RESTART: x=695, y=500+105+22=627
        assert bar.handle_click((695, 627)) == CMD_RESTART

    def test_click_outside_returns_none(self):
        from buttons import ButtonBar
        bar = ButtonBar()
        assert bar.handle_click((0, 0)) is None

    def test_click_in_game_area_returns_none(self):
        from buttons import ButtonBar
        bar = ButtonBar()
        # Ігрова зона — вище банера (y < 500)
        assert bar.handle_click((400, 250)) is None

    def test_click_at_pause_left_edge(self):
        from buttons import ButtonBar, CMD_PAUSE
        bar = ButtonBar()
        assert bar.handle_click((628, 578)) == CMD_PAUSE

    def test_click_at_pause_right_edge(self):
        from buttons import ButtonBar, CMD_PAUSE
        bar = ButtonBar()
        # Правий край: 628 + 135 - 1 = 762
        assert bar.handle_click((762, 578)) == CMD_PAUSE

    def test_click_just_outside_pause_left(self):
        from buttons import ButtonBar
        bar = ButtonBar()
        assert bar.handle_click((627, 578)) is None

    def test_click_just_outside_pause_right(self):
        from buttons import ButtonBar
        bar = ButtonBar()
        assert bar.handle_click((763, 578)) is None


# ── Constants ─────────────────────────────────────────────────────────────

class TestWindowConstants:
    def test_width(self):
        assert Window.WIDTH == 800

    def test_height(self):
        assert Window.HEIGHT == 678

    def test_fps(self):
        assert Window.FPS == 60

    def test_title_is_string(self):
        assert isinstance(Window.TITLE, str)
        assert len(Window.TITLE) > 0


class TestGameConfigConstants:
    def test_starting_shots(self):
        assert GameConfig.STARTING_SHOTS == 20

    def test_points_per_hit(self):
        assert GameConfig.POINTS_PER_HIT == 10

    def test_banner_y(self):
        assert GameConfig.BANNER_Y == 500

    def test_laser_radius_positive(self):
        assert GameConfig.LASER_RADIUS > 0

    def test_gun_pivot_x_is_center(self):
        assert GameConfig.GUN_PIVOT_X == Window.WIDTH / 2

    def test_sound_volume_in_range(self):
        assert 0.0 <= GameConfig.SOUND_VOLUME <= 1.0


class TestAssetPaths:
    REQUIRED_KEYS = [
        "icon", "background", "banner", "gameover", "winner",
        "gun", "font", "duck_shot", "gameover_sound", "winner_sound",
        "duck_skins",
    ]

    def test_all_required_keys_present(self):
        for key in self.REQUIRED_KEYS:
            assert key in ASSET_PATHS, f"Відсутній ключ: {key}"

    def test_duck_skins_is_list(self):
        assert isinstance(ASSET_PATHS["duck_skins"], list)

    def test_duck_skins_count(self):
        assert len(ASSET_PATHS["duck_skins"]) == 6

    def test_all_paths_are_strings(self):
        for key, val in ASSET_PATHS.items():
            if key == "duck_skins":
                assert all(isinstance(p, str) for p in val)
            else:
                assert isinstance(val, str)

    def test_asset_files_exist(self):
        """Всі файли мають фізично існувати у папці duckhunt/assets/."""
        base = os.path.join(os.path.dirname(__file__), "..")
        missing = []
        for key, val in ASSET_PATHS.items():
            paths = val if key == "duck_skins" else [val]
            for p in paths:
                full = os.path.normpath(os.path.join(base, p))
                if not os.path.isfile(full):
                    missing.append(p)
        assert missing == [], f"Відсутні asset-файли: {missing}"
