"""Spaced Repetition System using a simplified SM-2 algorithm."""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

PROGRESS_FILE = Path(__file__).parent / "progress.json"

# Quality ratings (0-5 scale, SM-2 standard)
AGAIN = 0  # Complete blackout
HARD = 2   # Recalled with serious difficulty
GOOD = 3   # Recalled with some effort
EASY = 5   # Perfect recall, effortless


@dataclass
class Card:
    """A single SRS card tracking review state."""
    card_id: str
    ease_factor: float = 2.5
    interval_days: float = 0.0
    repetitions: int = 0
    next_review: float = 0.0  # unix timestamp
    last_review: float = 0.0
    total_reviews: int = 0
    correct_count: int = 0

    @property
    def accuracy(self) -> float:
        if self.total_reviews == 0:
            return 0.0
        return self.correct_count / self.total_reviews

    def review(self, quality: int) -> None:
        """Update card state after a review using SM-2."""
        now = time.time()
        self.last_review = now
        self.total_reviews += 1

        if quality >= GOOD:
            self.correct_count += 1

        if quality < GOOD:
            # Failed — reset repetitions, short interval
            self.repetitions = 0
            self.interval_days = 0.007  # ~10 minutes
        else:
            if self.repetitions == 0:
                self.interval_days = 0.04  # ~1 hour
            elif self.repetitions == 1:
                self.interval_days = 1.0
            elif self.repetitions == 2:
                self.interval_days = 3.0
            else:
                self.interval_days *= self.ease_factor
            self.repetitions += 1

        # Update ease factor (SM-2 formula)
        self.ease_factor += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        self.ease_factor = max(1.3, self.ease_factor)

        self.next_review = now + self.interval_days * 86400


class SRSEngine:
    """Manages a collection of SRS cards with persistence."""

    def __init__(self, progress_file: Path | None = None):
        self.progress_file = progress_file or PROGRESS_FILE
        self.cards: dict[str, Card] = {}
        self._load()

    def _load(self) -> None:
        if self.progress_file.exists():
            data = json.loads(self.progress_file.read_text())
            for card_id, card_data in data.items():
                self.cards[card_id] = Card(**card_data)

    def save(self) -> None:
        data = {cid: asdict(card) for cid, card in self.cards.items()}
        self.progress_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def get_card(self, card_id: str) -> Card:
        if card_id not in self.cards:
            self.cards[card_id] = Card(card_id=card_id)
        return self.cards[card_id]

    def get_due_cards(self, card_ids: list[str]) -> list[str]:
        """Return card IDs that are due for review, sorted by priority."""
        now = time.time()
        due = []
        new = []
        for cid in card_ids:
            if cid not in self.cards:
                new.append(cid)
            elif self.cards[cid].next_review <= now:
                due.append(cid)

        # Sort due cards: most overdue first
        due.sort(key=lambda cid: self.cards[cid].next_review)

        # New cards go after due cards
        return due + new

    def record_review(self, card_id: str, quality: int) -> None:
        card = self.get_card(card_id)
        card.review(quality)
        self.save()

    def get_stats(self) -> dict:
        now = time.time()
        total = len(self.cards)
        if total == 0:
            return {"total": 0, "due": 0, "learning": 0, "mature": 0, "accuracy": 0.0}

        due = sum(1 for c in self.cards.values() if c.next_review <= now)
        learning = sum(1 for c in self.cards.values() if c.interval_days < 7)
        mature = sum(1 for c in self.cards.values() if c.interval_days >= 7)
        total_reviews = sum(c.total_reviews for c in self.cards.values())
        total_correct = sum(c.correct_count for c in self.cards.values())
        accuracy = total_correct / total_reviews if total_reviews > 0 else 0.0

        return {
            "total": total,
            "due": due,
            "learning": learning,
            "mature": mature,
            "accuracy": accuracy,
        }
