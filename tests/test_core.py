"""Tests for SRS engine and data integrity."""

import json
import tempfile
import time
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from srs import SRSEngine, Card, AGAIN, HARD, GOOD, EASY


class TestCard:
    def test_new_card_defaults(self):
        card = Card(card_id="test:1")
        assert card.ease_factor == 2.5
        assert card.interval_days == 0.0
        assert card.repetitions == 0
        assert card.accuracy == 0.0

    def test_review_good_first_time(self):
        card = Card(card_id="test:1")
        card.review(GOOD)
        assert card.repetitions == 1
        assert card.interval_days > 0
        assert card.next_review > 0

    def test_review_again_resets_repetitions(self):
        card = Card(card_id="test:1")
        card.review(GOOD)
        card.review(GOOD)
        assert card.repetitions == 2
        card.review(AGAIN)
        assert card.repetitions == 0

    def test_ease_factor_decreases_on_hard(self):
        card = Card(card_id="test:1")
        initial_ease = card.ease_factor
        card.review(HARD)
        assert card.ease_factor < initial_ease

    def test_ease_factor_minimum(self):
        card = Card(card_id="test:1")
        for _ in range(20):
            card.review(AGAIN)
        assert card.ease_factor >= 1.3

    def test_interval_grows_with_repetitions(self):
        card = Card(card_id="test:1")
        intervals = []
        for _ in range(5):
            card.review(GOOD)
            intervals.append(card.interval_days)
        # Each interval should be >= previous after initial ramp
        for i in range(2, len(intervals)):
            assert intervals[i] >= intervals[i - 1]

    def test_accuracy_tracking(self):
        card = Card(card_id="test:1")
        card.review(GOOD)
        card.review(GOOD)
        card.review(AGAIN)
        assert card.total_reviews == 3
        assert card.correct_count == 2
        assert abs(card.accuracy - 2 / 3) < 0.01


class TestSRSEngine:
    def _make_engine(self, tmp_path=None):
        if tmp_path is None:
            tmp = tempfile.mkdtemp()
            tmp_path = Path(tmp)
        return SRSEngine(progress_file=tmp_path / "progress.json")

    def test_get_card_creates_new(self):
        engine = self._make_engine()
        card = engine.get_card("test:1")
        assert card.card_id == "test:1"
        assert card.repetitions == 0

    def test_persistence(self):
        tmp = Path(tempfile.mkdtemp())
        pf = tmp / "progress.json"

        engine1 = SRSEngine(progress_file=pf)
        engine1.record_review("test:1", GOOD)

        engine2 = SRSEngine(progress_file=pf)
        card = engine2.get_card("test:1")
        assert card.total_reviews == 1

    def test_due_cards_new_cards_included(self):
        engine = self._make_engine()
        due = engine.get_due_cards(["a", "b", "c"])
        assert set(due) == {"a", "b", "c"}

    def test_due_cards_excludes_not_due(self):
        engine = self._make_engine()
        engine.record_review("a", EASY)
        # Card "a" should now have a future next_review
        due = engine.get_due_cards(["a", "b"])
        assert "b" in due
        # "a" might not be due depending on timing
        card_a = engine.get_card("a")
        if card_a.next_review > time.time():
            assert due[0] == "b"

    def test_stats_empty(self):
        engine = self._make_engine()
        stats = engine.get_stats()
        assert stats["total"] == 0
        assert stats["accuracy"] == 0.0

    def test_stats_after_reviews(self):
        engine = self._make_engine()
        engine.record_review("a", GOOD)
        engine.record_review("b", AGAIN)
        stats = engine.get_stats()
        assert stats["total"] == 2


class TestData:
    def test_vocab_json_valid(self):
        data_file = Path(__file__).parent.parent / "data" / "vocab.json"
        data = json.loads(data_file.read_text())
        assert len(data) > 0
        for category, entries in data.items():
            assert len(entries) > 0
            for entry in entries:
                assert "korean" in entry
                assert "english" in entry

    def test_grammar_json_valid(self):
        data_file = Path(__file__).parent.parent / "data" / "grammar.json"
        data = json.loads(data_file.read_text())
        assert len(data) > 0
        for category, entries in data.items():
            assert len(entries) > 0
            for entry in entries:
                assert "pattern" in entry
                assert "meaning" in entry
                assert "explanation" in entry

    def test_grammar_drills_have_answers(self):
        data_file = Path(__file__).parent.parent / "data" / "grammar.json"
        data = json.loads(data_file.read_text())
        for category, entries in data.items():
            for entry in entries:
                if "drill" in entry:
                    drill = entry["drill"]
                    assert "prompt" in drill
                    assert "answer" in drill
                    assert "full_sentence" in drill
