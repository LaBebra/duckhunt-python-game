"""
test_cli.py — тести для cli.py: DifficultyPreset, Settings, parse_settings, _parse_color.

Покриває:
  • значення всіх трьох пресетів складності
  • parse_settings: значення за замовчуванням (normal)
  • parse_settings: вибір кожного рівня складності
  • parse_settings: перевизначення --shots
  • parse_settings: --win-score
  • parse_settings: --mute обнуляє volume
  • parse_settings: --volume clamp до [0.0, 1.0]
  • parse_settings: --bg-color RGB та HEX формати
  • parse_settings: win_score за замовчуванням = target_count × 10
  • _parse_color: коректні та некоректні вхідні дані
"""

import pytest
import argparse
from cli import parse_settings, DIFFICULTY_PRESETS, DifficultyPreset, Settings
from cli import _parse_color


# ── DifficultyPreset ────────────────────────────────────────────────────

class TestDifficultyPresets:
    def test_all_three_presets_exist(self):
        assert "easy" in DIFFICULTY_PRESETS
        assert "normal" in DIFFICULTY_PRESETS
        assert "hard" in DIFFICULTY_PRESETS

    def test_easy_preset_values(self):
        p = DIFFICULTY_PRESETS["easy"]
        assert p.shots == 30
        assert p.target_speed == 1.5
        assert p.target_count == 8

    def test_normal_preset_values(self):
        p = DIFFICULTY_PRESETS["normal"]
        assert p.shots == 20
        assert p.target_speed == 2.0
        assert p.target_count == 12

    def test_hard_preset_values(self):
        p = DIFFICULTY_PRESETS["hard"]
        assert p.shots == 15
        assert p.target_speed == 3.5
        assert p.target_count == 12

    def test_difficulty_order_by_speed(self):
        """Швидкість зростає від easy до hard."""
        assert (
            DIFFICULTY_PRESETS["easy"].target_speed
            < DIFFICULTY_PRESETS["normal"].target_speed
            < DIFFICULTY_PRESETS["hard"].target_speed
        )

    def test_difficulty_order_by_shots(self):
        """Кількість пострілів зменшується від easy до hard."""
        assert (
            DIFFICULTY_PRESETS["easy"].shots
            > DIFFICULTY_PRESETS["normal"].shots
            > DIFFICULTY_PRESETS["hard"].shots
        )

    def test_preset_is_frozen(self):
        """DifficultyPreset — frozen dataclass, не можна змінити."""
        p = DIFFICULTY_PRESETS["easy"]
        with pytest.raises(Exception):
            p.shots = 99  # type: ignore


# ── parse_settings: defaults ─────────────────────────────────────────────

class TestParseSettingsDefaults:
    def test_default_difficulty_is_normal(self):
        s = parse_settings([])
        assert s.difficulty == "normal"

    def test_default_shots_from_normal_preset(self):
        s = parse_settings([])
        assert s.shots == 20

    def test_default_target_speed_from_normal_preset(self):
        s = parse_settings([])
        assert s.target_speed == 2.0

    def test_default_target_count_from_normal_preset(self):
        s = parse_settings([])
        assert s.target_count == 12

    def test_default_win_score_is_target_count_times_10(self):
        """За замовчуванням треба збити всіх качок."""
        s = parse_settings([])
        assert s.win_score == 12 * 10  # 120

    def test_default_bg_color_is_none(self):
        s = parse_settings([])
        assert s.bg_color is None

    def test_default_mute_is_false(self):
        s = parse_settings([])
        assert s.mute is False

    def test_default_volume_is_0_1(self):
        s = parse_settings([])
        assert s.volume == pytest.approx(0.1)


# ── parse_settings: difficulty ───────────────────────────────────────────

class TestParseSettingsDifficulty:
    @pytest.mark.parametrize("difficulty", ["easy", "normal", "hard"])
    def test_sets_correct_difficulty(self, difficulty):
        s = parse_settings(["--difficulty", difficulty])
        assert s.difficulty == difficulty

    def test_short_flag_d(self):
        s = parse_settings(["-d", "hard"])
        assert s.difficulty == "hard"

    def test_easy_win_score_default(self):
        s = parse_settings(["-d", "easy"])
        assert s.win_score == 8 * 10  # 80

    def test_hard_win_score_default(self):
        s = parse_settings(["-d", "hard"])
        assert s.win_score == 12 * 10  # 120

    def test_invalid_difficulty_raises(self):
        with pytest.raises(SystemExit):
            parse_settings(["--difficulty", "impossible"])


# ── parse_settings: shots ────────────────────────────────────────────────

class TestParseSettingsShots:
    def test_override_shots(self):
        s = parse_settings(["--shots", "99"])
        assert s.shots == 99

    def test_short_flag_s(self):
        s = parse_settings(["-s", "5"])
        assert s.shots == 5

    def test_shots_override_ignores_preset(self):
        """--shots має перевагу над пресетом складності."""
        s = parse_settings(["-d", "easy", "--shots", "7"])
        assert s.shots == 7

    def test_shots_zero_is_accepted(self):
        s = parse_settings(["--shots", "0"])
        assert s.shots == 0


# ── parse_settings: win_score ────────────────────────────────────────────

class TestParseSettingsWinScore:
    def test_custom_win_score(self):
        s = parse_settings(["--win-score", "50"])
        assert s.win_score == 50

    def test_short_flag_w(self):
        s = parse_settings(["-w", "30"])
        assert s.win_score == 30

    def test_win_score_overrides_default(self):
        s = parse_settings(["-d", "easy", "--win-score", "999"])
        assert s.win_score == 999


# ── parse_settings: mute / volume ────────────────────────────────────────

class TestParseSettingsVolume:
    def test_mute_sets_volume_to_zero(self):
        s = parse_settings(["--mute"])
        assert s.volume == 0.0
        assert s.mute is True

    def test_mute_short_flag(self):
        s = parse_settings(["-m"])
        assert s.mute is True

    def test_custom_volume(self):
        s = parse_settings(["--volume", "0.5"])
        assert s.volume == pytest.approx(0.5)

    def test_volume_clamped_above_1(self):
        s = parse_settings(["--volume", "9.9"])
        assert s.volume == pytest.approx(1.0)

    def test_volume_clamped_below_0(self):
        s = parse_settings(["--volume", "-5.0"])
        assert s.volume == pytest.approx(0.0)

    def test_mute_overrides_volume(self):
        """Якщо --mute вказано, volume = 0 навіть якщо --volume задано."""
        s = parse_settings(["--volume", "0.8", "--mute"])
        assert s.volume == 0.0


# ── parse_settings: bg_color ─────────────────────────────────────────────

class TestParseSettingsBgColor:
    def test_rgb_string_parsed(self):
        s = parse_settings(["--bg-color", "30,144,255"])
        assert s.bg_color == (30, 144, 255)

    def test_hex_string_parsed(self):
        s = parse_settings(["--bg-color", "#1e90ff"])
        assert s.bg_color == (30, 144, 255)

    def test_short_flag_c(self):
        s = parse_settings(["-c", "0,0,0"])
        assert s.bg_color == (0, 0, 0)

    def test_white_rgb(self):
        s = parse_settings(["--bg-color", "255,255,255"])
        assert s.bg_color == (255, 255, 255)


# ── _parse_color ─────────────────────────────────────────────────────────

class TestParseColor:
    def test_rgb_format(self):
        assert _parse_color("100,200,50") == (100, 200, 50)

    def test_rgb_with_spaces(self):
        assert _parse_color("100, 200, 50") == (100, 200, 50)

    def test_hex_lowercase(self):
        assert _parse_color("#ff0000") == (255, 0, 0)

    def test_hex_mixed_case(self):
        assert _parse_color("#1E90FF") == (30, 144, 255)

    def test_black_rgb(self):
        assert _parse_color("0,0,0") == (0, 0, 0)

    def test_white_rgb(self):
        assert _parse_color("255,255,255") == (255, 255, 255)

    def test_invalid_rgb_too_few_components(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _parse_color("100,200")

    def test_invalid_rgb_too_many_components(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _parse_color("100,200,50,30")

    def test_invalid_rgb_non_numeric(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _parse_color("red,green,blue")

    def test_invalid_hex_too_short(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _parse_color("#fff")

    def test_component_above_255(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _parse_color("256,0,0")

    def test_component_below_0(self):
        with pytest.raises(argparse.ArgumentTypeError):
            _parse_color("-1,0,0")
