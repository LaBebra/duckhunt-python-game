"""
test_game_state.py — тести для GameState та Phase.

Покриває:
  • початковий стан і всі властивості-запити
  • toggle_pause: PLAYING → PAUSED → PLAYING
  • toggle_pause ігнорується у GAME_OVER та WIN
  • spend_shot: зменшення лічильника, повернення True/False
  • add_points: накопичення очок
  • score_reached: перевірка умови перемоги
  • transition_to: явні переходи між фазами
"""

import pytest
from game_state import GameState, Phase


# ── Fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def playing_state():
    """Стандартний ігровий стан: 20 пострілів, 120 очок для перемоги."""
    return GameState(points=0, shots_left=20, phase=Phase.PLAYING, win_score=120)


@pytest.fixture
def paused_state():
    return GameState(points=0, shots_left=10, phase=Phase.PAUSED, win_score=50)


@pytest.fixture
def gameover_state():
    return GameState(points=0, shots_left=0, phase=Phase.GAME_OVER, win_score=50)


@pytest.fixture
def win_state():
    return GameState(points=120, shots_left=5, phase=Phase.WIN, win_score=120)


# ── Phase enum ──────────────────────────────────────────────────────────

class TestPhase:
    def test_all_phases_exist(self):
        assert Phase.PLAYING
        assert Phase.PAUSED
        assert Phase.GAME_OVER
        assert Phase.WIN

    def test_phases_are_unique(self):
        phases = [Phase.PLAYING, Phase.PAUSED, Phase.GAME_OVER, Phase.WIN]
        assert len(set(phases)) == 4


# ── Властивості-запити ──────────────────────────────────────────────────

class TestGameStateQueries:
    def test_is_playing_true_when_playing(self, playing_state):
        assert playing_state.is_playing is True

    def test_is_playing_false_when_paused(self, paused_state):
        assert paused_state.is_playing is False

    def test_is_playing_false_when_gameover(self, gameover_state):
        assert gameover_state.is_playing is False

    def test_is_paused_true_when_paused(self, paused_state):
        assert paused_state.is_paused is True

    def test_is_paused_false_when_playing(self, playing_state):
        assert playing_state.is_paused is False

    def test_is_over_true_when_gameover(self, gameover_state):
        assert gameover_state.is_over is True

    def test_is_over_true_when_win(self, win_state):
        assert win_state.is_over is True

    def test_is_over_false_when_playing(self, playing_state):
        assert playing_state.is_over is False

    def test_is_over_false_when_paused(self, paused_state):
        assert paused_state.is_over is False


# ── score_reached ────────────────────────────────────────────────────────

class TestScoreReached:
    def test_score_not_reached_initially(self, playing_state):
        assert playing_state.score_reached is False

    def test_score_reached_when_equal_to_win_score(self):
        state = GameState(points=100, shots_left=5, phase=Phase.PLAYING, win_score=100)
        assert state.score_reached is True

    def test_score_reached_when_exceeds_win_score(self):
        state = GameState(points=150, shots_left=5, phase=Phase.PLAYING, win_score=100)
        assert state.score_reached is True

    def test_score_not_reached_when_one_below(self):
        state = GameState(points=99, shots_left=5, phase=Phase.PLAYING, win_score=100)
        assert state.score_reached is False

    def test_score_reached_with_zero_win_score(self):
        """win_score=0 означає перемогу з самого початку."""
        state = GameState(points=0, shots_left=5, phase=Phase.PLAYING, win_score=0)
        assert state.score_reached is True


# ── toggle_pause ────────────────────────────────────────────────────────

class TestTogglePause:
    def test_playing_becomes_paused(self, playing_state):
        playing_state.toggle_pause()
        assert playing_state.phase == Phase.PAUSED

    def test_paused_becomes_playing(self, paused_state):
        paused_state.toggle_pause()
        assert paused_state.phase == Phase.PLAYING

    def test_double_toggle_returns_to_playing(self, playing_state):
        playing_state.toggle_pause()
        playing_state.toggle_pause()
        assert playing_state.phase == Phase.PLAYING

    def test_toggle_ignored_in_gameover(self, gameover_state):
        """toggle_pause не повинен діяти коли гра завершена."""
        gameover_state.toggle_pause()
        assert gameover_state.phase == Phase.GAME_OVER

    def test_toggle_ignored_in_win(self, win_state):
        win_state.toggle_pause()
        assert win_state.phase == Phase.WIN


# ── spend_shot ──────────────────────────────────────────────────────────

class TestSpendShot:
    def test_returns_true_when_shots_available(self, playing_state):
        result = playing_state.spend_shot()
        assert result is True

    def test_decrements_shots_by_one(self, playing_state):
        playing_state.spend_shot()
        assert playing_state.shots_left == 19

    def test_returns_false_when_no_shots(self):
        state = GameState(points=0, shots_left=0, phase=Phase.PLAYING, win_score=50)
        result = state.spend_shot()
        assert result is False

    def test_shots_not_decremented_below_zero(self):
        state = GameState(points=0, shots_left=0, phase=Phase.PLAYING, win_score=50)
        state.spend_shot()
        assert state.shots_left == 0

    def test_spend_all_shots_sequentially(self):
        state = GameState(points=0, shots_left=3, phase=Phase.PLAYING, win_score=50)
        assert state.spend_shot() is True   # shots_left = 2
        assert state.spend_shot() is True   # shots_left = 1
        assert state.spend_shot() is True   # shots_left = 0
        assert state.spend_shot() is False  # shots_left = 0, не витрачено
        assert state.shots_left == 0

    def test_spend_single_shot(self):
        state = GameState(points=0, shots_left=1, phase=Phase.PLAYING, win_score=50)
        assert state.spend_shot() is True
        assert state.shots_left == 0
        assert state.spend_shot() is False


# ── add_points ──────────────────────────────────────────────────────────

class TestAddPoints:
    def test_adds_points_to_zero(self, playing_state):
        playing_state.add_points(10)
        assert playing_state.points == 10

    def test_accumulates_multiple_hits(self, playing_state):
        playing_state.add_points(10)
        playing_state.add_points(10)
        playing_state.add_points(10)
        assert playing_state.points == 30

    def test_add_points_triggers_score_reached(self):
        state = GameState(points=110, shots_left=5, phase=Phase.PLAYING, win_score=120)
        assert state.score_reached is False
        state.add_points(10)
        assert state.score_reached is True

    def test_add_large_value(self, playing_state):
        playing_state.add_points(1000)
        assert playing_state.points == 1000


# ── transition_to ────────────────────────────────────────────────────────

class TestTransitionTo:
    def test_transition_playing_to_gameover(self, playing_state):
        playing_state.transition_to(Phase.GAME_OVER)
        assert playing_state.phase == Phase.GAME_OVER
        assert playing_state.is_over is True

    def test_transition_playing_to_win(self, playing_state):
        playing_state.transition_to(Phase.WIN)
        assert playing_state.phase == Phase.WIN
        assert playing_state.is_over is True

    def test_transition_to_all_phases(self, playing_state):
        for phase in Phase:
            playing_state.transition_to(phase)
            assert playing_state.phase == phase
